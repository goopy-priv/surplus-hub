import { useState } from "react";
import { ActivityIndicator, FlatList, SafeAreaView, Text, TextInput, TouchableOpacity, View } from "react-native";
import { useMaterials } from "@repo/core";
import { useRouter } from "expo-router";

export default function SearchScreen() {
  const router = useRouter();
  const [keyword, setKeyword] = useState("");
  const [submittedKeyword, setSubmittedKeyword] = useState("");
  const { data, isLoading, error } = useMaterials({
    keyword: submittedKeyword || undefined,
    page: 1,
    limit: 20,
  });

  const handleSubmit = () => {
    setSubmittedKeyword(keyword.trim());
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <View className="px-4 pt-4">
        <Text className="text-2xl font-bold text-gray-900">검색</Text>
        <Text className="mt-1 text-sm text-gray-500">자재명을 검색해 원하는 매물을 찾으세요.</Text>
        <View className="mt-4 flex-row gap-2">
          <TextInput
            value={keyword}
            onChangeText={setKeyword}
            onSubmitEditing={handleSubmit}
            placeholder="시멘트, 파이프, 목재 검색..."
            className="flex-1 rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm"
            returnKeyType="search"
          />
          <TouchableOpacity onPress={handleSubmit} className="rounded-xl bg-blue-600 px-4 py-3">
            <Text className="text-sm font-bold text-white">검색</Text>
          </TouchableOpacity>
        </View>
      </View>

      {isLoading ? (
        <View className="mt-8 items-center">
          <ActivityIndicator size="large" color="#2563eb" />
        </View>
      ) : null}

      {error ? <Text className="px-4 pt-6 text-sm text-red-500">검색 결과를 불러오지 못했습니다.</Text> : null}

      {!isLoading && !error ? (
        <FlatList
          data={data?.data ?? []}
          keyExtractor={(item) => item.id}
          contentContainerStyle={{ padding: 16, paddingBottom: 24 }}
          renderItem={({ item }) => (
            <TouchableOpacity
              onPress={() => router.push(`/material/${item.id}`)}
              className="mb-3 rounded-xl border border-gray-200 bg-white p-4"
            >
              <View className="flex-row items-start justify-between">
                <View className="flex-1 pr-3">
                  <Text className="text-base font-bold text-gray-900">{item.title}</Text>
                  <Text className="mt-1 text-sm text-gray-600" numberOfLines={2}>
                    {item.description}
                  </Text>
                  <Text className="mt-2 text-xs text-gray-500">{item.location || "위치 정보 없음"}</Text>
                </View>
                <Text className="text-sm font-bold text-blue-600">{item.price.toLocaleString()}원</Text>
              </View>
            </TouchableOpacity>
          )}
          ListEmptyComponent={
            <View className="rounded-xl border border-dashed border-gray-300 bg-white p-6">
              <Text className="text-center text-sm text-gray-500">검색 결과가 없습니다.</Text>
            </View>
          }
        />
      ) : null}
    </SafeAreaView>
  );
}
