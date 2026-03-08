import { ActivityIndicator, FlatList, SafeAreaView, Text, TouchableOpacity, View } from "react-native";
import { useChatRooms } from "@repo/core";
import { useRouter } from "expo-router";

export default function NotificationsScreen() {
  const router = useRouter();
  const { data, isLoading, error } = useChatRooms({ page: 1, limit: 20 });
  const unreadRooms = (data?.data ?? []).filter((room) => room.unreadCount > 0);

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <View className="px-4 pt-4">
        <Text className="text-2xl font-bold text-gray-900">알림</Text>
        <Text className="mt-1 text-sm text-gray-500">읽지 않은 메시지 알림을 확인하세요.</Text>
      </View>

      {isLoading ? (
        <View className="mt-8 items-center">
          <ActivityIndicator size="large" color="#2563eb" />
        </View>
      ) : null}

      {error ? <Text className="px-4 pt-6 text-sm text-red-500">알림을 불러오지 못했습니다.</Text> : null}

      {!isLoading && !error ? (
        <FlatList
          data={unreadRooms}
          keyExtractor={(item) => item.id}
          contentContainerStyle={{ padding: 16, paddingBottom: 24 }}
          renderItem={({ item }) => (
            <TouchableOpacity
              onPress={() => router.push(`/chat/${item.id}`)}
              className="mb-3 flex-row items-center justify-between rounded-xl border border-gray-200 bg-white p-4"
            >
              <View className="flex-1 pr-3">
                <Text className="text-sm font-bold text-gray-900">{item.otherUser.name}</Text>
                <Text className="mt-1 text-xs text-gray-500" numberOfLines={1}>
                  {item.lastMessage?.content || "새 메시지가 도착했습니다."}
                </Text>
              </View>
              <Text className="rounded-full bg-blue-600 px-2 py-1 text-xs font-bold text-white">{item.unreadCount}</Text>
            </TouchableOpacity>
          )}
          ListEmptyComponent={
            <View className="rounded-xl border border-dashed border-gray-300 bg-white p-6">
              <Text className="text-center text-sm text-gray-500">새 알림이 없습니다.</Text>
            </View>
          }
        />
      ) : null}
    </SafeAreaView>
  );
}
