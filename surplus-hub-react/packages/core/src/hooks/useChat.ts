import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from "@tanstack/react-query";
import { createChatRoom, fetchChatMessages, fetchChatRooms, sendMessage } from "../api";
import { ChatMessage, ChatMessageQueryParams, ChatMessageResponse, ChatRoomQueryParams, ChatRoomResponse } from "../types";

export const useChatRooms = (params?: ChatRoomQueryParams): UseQueryResult<ChatRoomResponse> => {
  return useQuery({
    queryKey: ["chatRooms", params ?? {}],
    queryFn: () => fetchChatRooms(params),
  });
};

export const useChatMessages = (roomId: string, params?: ChatMessageQueryParams): UseQueryResult<ChatMessageResponse> => {
  return useQuery({
    queryKey: ["chatMessages", roomId, params ?? {}],
    queryFn: () => fetchChatMessages(roomId, params),
    enabled: !!roomId,
  });
};

export const useSendMessage = (): UseMutationResult<ChatMessage, Error, { roomId: string; content: string }> => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ roomId, content }: { roomId: string; content: string }) =>
      sendMessage(roomId, content),
    onSuccess: (_, { roomId }) => {
      queryClient.invalidateQueries({ queryKey: ["chatMessages", roomId] });
      queryClient.invalidateQueries({ queryKey: ["chatRooms"] });
    },
  });
};

export const useCreateChatRoom = (): UseMutationResult<{ id: string }, Error, { materialId: number; sellerId: number }> => {
  return useMutation({
    mutationFn: ({ materialId, sellerId }: { materialId: number; sellerId: number }) =>
      createChatRoom(materialId, sellerId),
  });
};
