import { useEffect, useMemo, useState } from "react";
import { View, Text, FlatList, ActivityIndicator, TextInput, TouchableOpacity } from "react-native";
import { MaterialItem, useMaterials } from "@repo/core";
import { MaterialCard } from "@repo/ui";
import { useRouter } from "expo-router";

const CATEGORIES = ["전체", "목재", "금속", "콘크리트", "공구", "전기"] as const;
const FIXED_SORT = "latest" as const;
const PAGE_SIZE = 20;

export default function Home() {
  const [searchInput, setSearchInput] = useState("");
  const [submittedKeyword, setSubmittedKeyword] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<(typeof CATEGORIES)[number]>("전체");
  const [page, setPage] = useState(1);
  const [materials, setMaterials] = useState<MaterialItem[]>([]);
  const [hasReachedMax, setHasReachedMax] = useState(false);

  const queryParams = useMemo(
    () => ({
      page,
      limit: PAGE_SIZE,
      category: selectedCategory === "전체" ? undefined : selectedCategory,
      sort: FIXED_SORT,
      keyword: submittedKeyword.trim() ? submittedKeyword.trim() : undefined,
    }),
    [page, selectedCategory, submittedKeyword]
  );

  const { data, isLoading, isFetching, error } = useMaterials(queryParams);
  const router = useRouter();

  useEffect(() => {
    setPage(1);
    setMaterials([]);
    setHasReachedMax(false);
  }, [selectedCategory, submittedKeyword]);

  useEffect(() => {
    if (!data) return;

    const incoming = data?.data ?? [];

    setMaterials((previous) => {
      if (page === 1) {
        return incoming;
      }

      const merged = [...previous];
      const seen = new Set(previous.map((item) => item.id));

      for (const item of incoming) {
        if (!seen.has(item.id)) {
          merged.push(item);
          seen.add(item.id);
        }
      }

      return merged;
    });

    setHasReachedMax(incoming.length < PAGE_SIZE);
  }, [data, page]);

  const handleSearch = () => {
    setSubmittedKeyword(searchInput);
  };

  const handleLoadMore = () => {
    if (isFetching || hasReachedMax) return;
    setPage((currentPage) => currentPage + 1);
  };

  const showInitialLoading = isLoading && page === 1 && materials.length === 0;

  if (showInitialLoading) {
    return (
      <View className="flex-1 justify-center items-center">
        <ActivityIndicator size="large" color="#2563eb" />
      </View>
    );
  }

  if (error && materials.length === 0) {
    return (
      <View className="flex-1 justify-center items-center">
        <Text className="text-red-500">자재 목록을 불러오지 못했습니다.</Text>
      </View>
    );
  }

  return (
    <FlatList
      className="flex-1 bg-gray-50"
      data={materials}
      contentContainerStyle={{ padding: 16, paddingBottom: 24 }}
      ListHeaderComponent={
        <View>
          <View className="mb-6 mt-2">
            <Text className="mb-4 text-center text-3xl font-extrabold text-gray-900">
              내 주변 잉여 자재를
              {"\n"}
              <Text className="text-blue-600">찾아보세요</Text>
            </Text>

            <View className="relative">
              <TextInput
                value={searchInput}
                onChangeText={setSearchInput}
                onSubmitEditing={handleSearch}
                placeholder="시멘트, 파이프, 목재 검색..."
                className="rounded-2xl border border-gray-200 bg-white px-4 py-3 pr-20 text-base text-gray-900"
                returnKeyType="search"
              />
              <TouchableOpacity
                onPress={handleSearch}
                className="absolute right-2 top-1/2 -translate-y-1/2 rounded-xl bg-blue-600 px-4 py-2"
              >
                <Text className="text-sm font-bold text-white">검색</Text>
              </TouchableOpacity>
            </View>
          </View>

          <FlatList
            horizontal
            data={CATEGORIES}
            keyExtractor={(item) => item}
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={{ paddingBottom: 12 }}
            renderItem={({ item }) => {
              const isSelected = item === selectedCategory;
              return (
                <TouchableOpacity
                  onPress={() => setSelectedCategory(item)}
                  className={`mr-2 rounded-full px-4 py-2 ${
                    isSelected ? "bg-gray-900" : "border border-gray-200 bg-white"
                  }`}
                >
                  <Text className={`text-sm font-semibold ${isSelected ? "text-white" : "text-gray-600"}`}>
                    {item}
                  </Text>
                </TouchableOpacity>
              );
            }}
          />

          <View className="mb-4 flex-row justify-end">
            <View className="rounded-xl border border-gray-200 bg-white px-3 py-2">
              <Text className="text-xs font-semibold text-gray-700">정렬: 최신순</Text>
            </View>
          </View>
        </View>
      }
      ListEmptyComponent={
        <View className="items-center py-16">
          <Text className="text-sm text-gray-500">검색 조건에 맞는 자재가 없습니다.</Text>
        </View>
      }
      ListFooterComponent={
        !hasReachedMax && materials.length > 0 ? (
          <View className="items-center pt-2">
            <TouchableOpacity
              onPress={handleLoadMore}
              disabled={isFetching}
              className="rounded-lg border border-gray-200 bg-white px-6 py-3"
            >
              <Text className="text-sm font-semibold text-gray-800">
                {isFetching ? "불러오는 중..." : "더 보기"}
              </Text>
            </TouchableOpacity>
          </View>
        ) : null
      }
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => (
        <MaterialCard
          title={item.title}
          price={item.price}
          location={item.location}
          imageUrl={item.imageUrl}
          onPress={() => router.push(`/material/${item.id}`)}
        />
      )}
    />
  );
}
