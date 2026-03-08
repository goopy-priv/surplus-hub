"use client";

import { styled } from "nativewind";
import { TouchableOpacity, Text } from "react-native";

const StyledButton = styled(TouchableOpacity);
const StyledText = styled(Text);

export const Button = ({ onPress, title }: { onPress: () => void; title: string }) => {
  return (
    <StyledButton className="bg-blue-500 p-4 rounded-lg items-center" onPress={onPress}>
      <StyledText className="text-white font-bold text-lg">{title}</StyledText>
    </StyledButton>
  );
};
