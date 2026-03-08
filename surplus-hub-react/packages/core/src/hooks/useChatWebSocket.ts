import { useEffect, useRef, useState, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { getApiBaseUrl } from "../api/client";
import type {
  ChatMessage,
  WsServerMessage,
  WsMessageData,
} from "../types";

interface UseChatWebSocketOptions {
  roomId: string;
  token: string | null;
  enabled?: boolean;
}

interface UseChatWebSocketReturn {
  isConnected: boolean;
  sendTextMessage: (content: string) => void;
  sendReadReceipt: () => void;
  sendTyping: () => void;
  typingUser: string | null;
}

const wsMessageToChat = (data: WsMessageData, roomId: string): ChatMessage => ({
  id: String(data.id),
  roomId,
  senderId: String(data.senderId),
  content: data.content,
  timestamp: data.createdAt,
  isRead: data.isRead,
});

export const useChatWebSocket = ({
  roomId,
  token,
  enabled = true,
}: UseChatWebSocketOptions): UseChatWebSocketReturn => {
  const wsRef = useRef<WebSocket | null>(null);
  const queryClient = useQueryClient();
  const [isConnected, setIsConnected] = useState(false);
  const [typingUser, setTypingUser] = useState<string | null>(null);
  const typingTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttempts = useRef(0);
  const MAX_RECONNECT_ATTEMPTS = 5;

  const getWsUrl = useCallback(() => {
    const httpBase = getApiBaseUrl();
    const wsBase = httpBase
      .replace(/^https:/, "wss:")
      .replace(/^http:/, "ws:")
      .replace(/\/api\/v1$/, "");
    return `${wsBase}/ws/chat/${roomId}?token=${token}`;
  }, [roomId, token]);

  const handleMessage = useCallback(
    (event: MessageEvent) => {
      try {
        const msg: WsServerMessage = JSON.parse(event.data);

        if (msg.type === "message") {
          const chatMsg = wsMessageToChat(msg.data, roomId);
          // Append to React Query cache
          queryClient.setQueryData(
            ["chatMessages", roomId, {}],
            (old: { data: ChatMessage[]; meta?: unknown } | undefined) => {
              if (!old) return { data: [chatMsg] };
              // Deduplicate by id
              const exists = old.data.some((m) => m.id === chatMsg.id);
              if (exists) return old;
              return { ...old, data: [...old.data, chatMsg] };
            }
          );
          // Also invalidate chat rooms to update lastMessage/unreadCount
          queryClient.invalidateQueries({ queryKey: ["chatRooms"] });
        } else if (msg.type === "read_receipt") {
          // Mark all messages from the reader as read in cache
          queryClient.setQueryData(
            ["chatMessages", roomId, {}],
            (old: { data: ChatMessage[]; meta?: unknown } | undefined) => {
              if (!old) return old;
              return {
                ...old,
                data: old.data.map((m) => ({
                  ...m,
                  isRead: true,
                })),
              };
            }
          );
        } else if (msg.type === "typing") {
          setTypingUser(msg.data.userName);
          if (typingTimerRef.current) clearTimeout(typingTimerRef.current);
          typingTimerRef.current = setTimeout(() => setTypingUser(null), 3000);
        }
      } catch {
        // Ignore malformed messages
      }
    },
    [roomId, queryClient]
  );

  const connect = useCallback(() => {
    if (!token || !roomId || !enabled) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const ws = new WebSocket(getWsUrl());
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        reconnectAttempts.current = 0;
      };

      ws.onmessage = handleMessage;

      ws.onclose = () => {
        setIsConnected(false);
        wsRef.current = null;
        // Auto-reconnect with exponential backoff
        if (
          enabled &&
          reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS
        ) {
          const delay = Math.min(1000 * 2 ** reconnectAttempts.current, 30000);
          reconnectAttempts.current += 1;
          reconnectTimerRef.current = setTimeout(connect, delay);
        }
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch {
      // WebSocket constructor can throw in some environments
    }
  }, [token, roomId, enabled, getWsUrl, handleMessage]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      if (typingTimerRef.current) clearTimeout(typingTimerRef.current);
      if (wsRef.current) {
        wsRef.current.onclose = null; // Prevent reconnect on intentional close
        wsRef.current.close();
        wsRef.current = null;
      }
      setIsConnected(false);
    };
  }, [connect]);

  const sendTextMessage = useCallback((content: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "text", content }));
    }
  }, []);

  const sendReadReceipt = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "read" }));
    }
  }, []);

  const sendTyping = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "typing" }));
    }
  }, []);

  return {
    isConnected,
    sendTextMessage,
    sendReadReceipt,
    sendTyping,
    typingUser,
  };
};
