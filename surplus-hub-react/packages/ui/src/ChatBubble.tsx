import { styled } from "nativewind";
import { View, Text } from "react-native";
import { ChatMessage } from "@repo/core";

const StyledView = styled(View);
const StyledText = styled(Text);

interface ChatBubbleProps {
  message: ChatMessage;
  isMe: boolean;
}

export const ChatBubble = ({ message, isMe }: ChatBubbleProps) => {
  return (
    <StyledView
      className={`max-w-[80%] rounded-2xl p-3 mb-2 ${
        isMe ? "bg-blue-600 self-end rounded-tr-none" : "bg-gray-200 self-start rounded-tl-none"
      }`}
    >
      <StyledText className={`${isMe ? "text-white" : "text-gray-900"}`}>
        {message.content}
      </StyledText>
      <StyledView className="flex-row justify-end items-center mt-1">
        {isMe && message.isRead && (
          <StyledText className="text-xs text-blue-200 mr-1">
            읽음
          </StyledText>
        )}
        <StyledText className={`text-xs ${isMe ? "text-blue-200" : "text-gray-500"}`}>
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </StyledText>
      </StyledView>
    </StyledView>
  );
};
