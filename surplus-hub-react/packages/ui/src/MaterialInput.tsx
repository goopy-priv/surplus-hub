import { styled } from "nativewind";
import { TextInput, View, Text } from "react-native";

const StyledView = styled(View);
const StyledText = styled(Text);
const StyledTextInput = styled(TextInput);

export interface MaterialInputProps {
  label: string;
  value: string;
  onChangeText: (text: string) => void;
  placeholder?: string;
  keyboardType?: "default" | "numeric" | "email-address";
  multiline?: boolean;
}

export const MaterialInput = ({
  label,
  value,
  onChangeText,
  placeholder,
  keyboardType = "default",
  multiline = false,
}: MaterialInputProps) => {
  return (
    <StyledView className="mb-4">
      <StyledText className="text-sm font-medium text-gray-700 mb-1">
        {label}
      </StyledText>
      <StyledTextInput
        className={`bg-white border border-gray-300 rounded-lg p-3 text-base text-gray-900 ${
          multiline ? "h-32" : "h-12"
        }`}
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        keyboardType={keyboardType}
        multiline={multiline}
        textAlignVertical={multiline ? "top" : "center"}
      />
    </StyledView>
  );
};
