import { styled } from "nativewind";
import { View, Text, Image, TouchableOpacity } from "react-native";

const StyledView = styled(View);
const StyledText = styled(Text);
const StyledImage = styled(Image);
const StyledTouchable = styled(TouchableOpacity);

export interface MaterialCardProps {
  title: string;
  price: number;
  location: string;
  imageUrl: string;
  onPress?: () => void;
}

export const MaterialCard = ({
  title,
  price,
  location,
  imageUrl,
  onPress,
}: MaterialCardProps) => {
  return (
    <StyledTouchable
      className="bg-white rounded-xl shadow-sm overflow-hidden mb-4 border border-gray-100"
      onPress={onPress}
    >
      <StyledImage source={{ uri: imageUrl }} className="w-full h-48 bg-gray-200" resizeMode="cover" />
      <StyledView className="p-4">
        <StyledText className="text-lg font-bold text-gray-900 mb-1" numberOfLines={1}>
          {title}
        </StyledText>
        <StyledText className="text-sm text-gray-500 mb-2">{location}</StyledText>
        <StyledText className="text-lg font-bold text-blue-600">
          {price.toLocaleString()} KRW
        </StyledText>
      </StyledView>
    </StyledTouchable>
  );
};
