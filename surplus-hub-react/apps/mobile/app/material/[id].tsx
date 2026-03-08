import { useState } from "react";
import { View, Text, Image, ScrollView, ActivityIndicator, TouchableOpacity, SafeAreaView } from "react-native";
import { useLocalSearchParams, useRouter, Stack } from "expo-router";
import { useCreateChatRoom, useMaterialDetail } from "@repo/core";

const TRADE_METHOD_LABELS: Record<string, string> = {
  DIRECT: "직거래",
  DELIVERY: "배송 협의",
};

const STATUS_LABELS: Record<string, string> = {
  ACTIVE: "판매중",
  RESERVED: "예약중",
  SOLD: "거래완료",
};

const formatTradeMethod = (tradeMethod?: string): string =>
  tradeMethod ? TRADE_METHOD_LABELS[tradeMethod] ?? tradeMethod : "정보 없음";

const formatStatus = (status?: string): string =>
  status ? STATUS_LABELS[status] ?? status : "정보 없음";

const formatQuantity = (quantity?: number, unit?: string): string =>
  quantity && quantity > 0 ? `${quantity}${unit ? ` ${unit}` : ""}` : "정보 없음";

export default function MaterialDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { data: item, isLoading } = useMaterialDetail(id);
  const { mutateAsync: createChatRoom, isPending: isCreatingRoom } = useCreateChatRoom();
  const router = useRouter();
  const [liked, setLiked] = useState(false);

  const handleStartChat = async () => {
    if (!item) {
      router.push("/chat");
      return;
    }

    const materialId = Number(item.id);
    const sellerId = Number(item.sellerId);

    if (!Number.isFinite(materialId) || !Number.isFinite(sellerId) || materialId <= 0 || sellerId <= 0) {
      router.push("/chat");
      return;
    }

    try {
      const room = await createChatRoom({ materialId, sellerId });
      if (room.id) {
        router.push(`/chat/${room.id}`);
        return;
      }
    } catch {
      // Fall back to chat list when room creation fails.
    }

    router.push("/chat");
  };

  if (isLoading) {
    return (
      <View className="flex-1 items-center justify-center">
        <ActivityIndicator size="large" color="#2563eb" />
      </View>
    );
  }

  if (!item) {
    return (
      <View className="flex-1 items-center justify-center">
        <Text className="text-red-500">자재를 찾을 수 없습니다.</Text>
      </View>
    );
  }

  const createdAt = new Date(item.createdAt).toLocaleDateString();
  const locationLabel = item.location || "위치 정보 없음";
  const sellerDisplayName = item.sellerName || `판매자 #${item.sellerId}`;
  const statusLabel = formatStatus(item.status);
  const tradeMethodLabel = formatTradeMethod(item.tradeMethod);
  const quantityLabel = formatQuantity(item.quantity, item.quantityUnit);

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ title: "자재 상세" }} />

      <ScrollView className="flex-1" contentContainerStyle={{ paddingBottom: 24 }}>
        {item.imageUrl ? (
          <Image source={{ uri: item.imageUrl }} className="h-80 w-full bg-gray-200" resizeMode="cover" />
        ) : (
          <View className="h-80 w-full items-center justify-center bg-gray-200">
            <Text className="text-sm text-gray-500">이미지 없음</Text>
          </View>
        )}

        <View className="p-5">
          <View className="flex-row items-start">
            <View className="flex-1 pr-3">
              <Text className="text-2xl font-bold text-gray-900">{item.title}</Text>
              <Text className="mt-1 text-sm text-gray-500">{createdAt}</Text>
            </View>
          </View>

          <View className="mt-5">
            <View>
              <Text className="text-3xl font-bold text-blue-600">{item.price.toLocaleString()}원</Text>
              <Text className="text-xs text-gray-500">거래 조건은 판매자와 협의</Text>
            </View>
          </View>

          <View className="mt-6 rounded-xl border border-blue-100 bg-blue-50 p-4">
            <Text className="text-sm font-bold text-blue-700">AI 분석</Text>
            <Text className="mt-1 text-sm leading-5 text-blue-800">
              등록 카테고리는 {item.category || "기타"}이며 등록일은 {createdAt}입니다. 상세 조건은 채팅으로 확인해 주세요.
            </Text>
          </View>

          <View className="mt-6">
            <Text className="mb-2 text-lg font-bold text-gray-900">상세 설명</Text>
            <Text className="text-base leading-6 text-gray-700">{item.description}</Text>
          </View>

          <View className="mt-6 rounded-xl bg-gray-50 p-4">
            <View className="mb-3 flex-row items-center justify-between">
              <Text className="text-sm text-gray-500">상태</Text>
              <Text className="text-sm font-semibold text-gray-900">{statusLabel}</Text>
            </View>
            <View className="mb-3 flex-row items-center justify-between">
              <Text className="text-sm text-gray-500">카테고리</Text>
              <Text className="text-sm font-semibold text-gray-900">{item.category || "기타"}</Text>
            </View>
            <View className="mb-3 flex-row items-center justify-between">
              <Text className="text-sm text-gray-500">수량</Text>
              <Text className="text-sm font-semibold text-gray-900">{quantityLabel}</Text>
            </View>
            <View className="mb-3 flex-row items-center justify-between">
              <Text className="text-sm text-gray-500">위치</Text>
              <Text className="text-sm font-semibold text-gray-900">{locationLabel}</Text>
            </View>
            <View className="flex-row items-center justify-between">
              <Text className="text-sm text-gray-500">거래 방식</Text>
              <Text className="text-sm font-semibold text-gray-900">{tradeMethodLabel}</Text>
            </View>
          </View>

          <View className="mt-6 rounded-xl border border-gray-100 p-4">
            <View className="flex-row items-center">
              {item.sellerAvatarUrl ? (
                <Image source={{ uri: item.sellerAvatarUrl }} className="mr-3 h-12 w-12 rounded-full bg-gray-200" />
              ) : (
                <View className="mr-3 h-12 w-12 items-center justify-center rounded-full bg-gray-200">
                  <Text className="text-xs font-bold text-gray-600">판매자</Text>
                </View>
              )}
              <View className="flex-1">
                <Text className="text-base font-bold text-gray-900">{sellerDisplayName}</Text>
                <Text className="text-xs text-gray-500">{locationLabel}</Text>
              </View>
              <Text className="text-lg text-gray-300">›</Text>
            </View>
          </View>
        </View>
      </ScrollView>

      <View className="border-t border-gray-200 bg-white px-4 py-3">
        <View className="flex-row items-center">
          <TouchableOpacity
            onPress={() => setLiked((previous) => !previous)}
            className="h-12 w-12 items-center justify-center rounded-lg border border-gray-200"
          >
            <Text className={`text-lg ${liked ? "text-red-500" : "text-gray-500"}`}>{liked ? "♥" : "♡"}</Text>
          </TouchableOpacity>
          <View className="ml-3 flex-1">
            <Text className="text-lg font-bold text-gray-900">{item.price.toLocaleString()}원</Text>
            <Text className="text-xs text-gray-500">거래 조건은 판매자와 협의</Text>
          </View>
          <TouchableOpacity
            onPress={handleStartChat}
            disabled={isCreatingRoom}
            className="rounded-lg bg-blue-600 px-5 py-3"
          >
            <Text className="text-sm font-bold text-white">{isCreatingRoom ? "채팅 연결 중..." : "판매자와 채팅"}</Text>
          </TouchableOpacity>
        </View>
      </View>
    </SafeAreaView>
  );
}
