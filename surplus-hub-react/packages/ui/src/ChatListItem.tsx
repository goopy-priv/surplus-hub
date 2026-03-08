import { styled } from "nativewind";
import { View, Text, TouchableOpacity, Image } from "react-native";
import { ChatRoom } from "@repo/core";

const StyledTouchable = styled(TouchableOpacity);
const StyledView = styled(View);
const StyledText = styled(Text);
const StyledImage = styled(Image);

interface ChatListItemProps {
  room: ChatRoom;
  onPress: () => void;
}

export const ChatListItem = ({ room, onPress }: ChatListItemProps) => {
  return (
    <StyledTouchable
      className="flex-row items-center p-4 bg-white border-b border-gray-100 active:bg-gray-50"
      onPress={onPress}
    >
      <StyledImage
        source={{ uri: room.otherUser.avatarUrl }}
        className="w-12 h-12 rounded-full bg-gray-200 mr-3"
      />
      <StyledView className="flex-1">
        <StyledView className="flex-row justify-between mb-1">
          <StyledText className="font-bold text-gray-900">{room.otherUser.name}</StyledText>
          <StyledText className="text-xs text-gray-500">
            {new Date(room.updatedAt).toLocaleDateString()}
          </StyledText>
        </StyledView>
        <StyledView className="flex-row justify-between items-center">
          <StyledText className="text-gray-600 text-sm" numberOfLines={1}>
            {room.lastMessage?.content || "No messages yet"}
          </StyledText>
          {room.unreadCount > 0 && (
            <StyledView className="bg-red-500 rounded-full w-5 h-5 items-center justify-center">
              <StyledText className="text-white text-xs font-bold">{room.unreadCount}</StyledText>
            </StyledView>
          )}
        </StyledView>
      </StyledView>
    </StyledTouchable>
  );
};
