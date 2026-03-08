import type { BottomTabBarProps } from "@react-navigation/bottom-tabs";
import { Tabs, usePathname, useRouter } from "expo-router";
import { Text, TouchableOpacity, View } from "react-native";

const TAB_CONFIG: Record<string, { label: string; icon: string }> = {
  index: { label: "홈", icon: "🏠" },
  community: { label: "커뮤니티", icon: "🧩" },
  "chat/index": { label: "채팅", icon: "💬" },
  profile: { label: "내 정보", icon: "👤" },
};

function AppTabBar({ state, descriptors, navigation }: BottomTabBarProps) {
  const router = useRouter();
  const pathname = usePathname();

  // Chat room is treated as full-screen flow, not tab-shell flow.
  if (pathname.startsWith("/chat/") && pathname !== "/chat") {
    return null;
  }

  const tabRoutes = state.routes.filter((route) => TAB_CONFIG[route.name]);
  const leftRoutes = tabRoutes.slice(0, 2);
  const rightRoutes = tabRoutes.slice(2);

  const renderTabButton = (route: (typeof state.routes)[number]) => {
    const routeIndex = state.routes.findIndex((item) => item.key === route.key);
    const isFocused = state.index === routeIndex;
    const config = TAB_CONFIG[route.name];

    const onPress = () => {
      const event = navigation.emit({
        type: "tabPress",
        target: route.key,
        canPreventDefault: true,
      });

      if (!isFocused && !event.defaultPrevented) {
        navigation.navigate(route.name);
      }
    };

    const onLongPress = () => {
      navigation.emit({
        type: "tabLongPress",
        target: route.key,
      });
    };

    return (
      <TouchableOpacity
        key={route.key}
        accessibilityRole="button"
        accessibilityLabel={descriptors[route.key]?.options.tabBarAccessibilityLabel}
        accessibilityState={isFocused ? { selected: true } : {}}
        onPress={onPress}
        onLongPress={onLongPress}
        style={{
          flex: 1,
          alignItems: "center",
          justifyContent: "center",
          minHeight: 56,
        }}
      >
        <Text
          style={{
            fontSize: 20,
            color: isFocused ? "#2563eb" : "#9ca3af",
            marginBottom: 2,
          }}
        >
          {config.icon}
        </Text>
        <Text
          style={{
            fontSize: 11,
            fontWeight: "600",
            color: isFocused ? "#2563eb" : "#9ca3af",
          }}
        >
          {config.label}
        </Text>
      </TouchableOpacity>
    );
  };

  return (
    <View
      style={{
        borderTopWidth: 1,
        borderTopColor: "#e5e7eb",
        backgroundColor: "#ffffff",
        paddingHorizontal: 8,
        paddingTop: 4,
        paddingBottom: 8,
      }}
    >
      <View style={{ flexDirection: "row", alignItems: "center", position: "relative" }}>
        {leftRoutes.map(renderTabButton)}
        <View style={{ width: 64 }} />
        {rightRoutes.map(renderTabButton)}

        <TouchableOpacity
          accessibilityRole="button"
          accessibilityLabel="자재 등록"
          onPress={() => router.push("/register")}
          style={{
            position: "absolute",
            left: "50%",
            top: -24,
            marginLeft: -28,
            width: 56,
            height: 56,
            borderRadius: 28,
            backgroundColor: "#2563eb",
            borderWidth: 4,
            borderColor: "#ffffff",
            alignItems: "center",
            justifyContent: "center",
            shadowColor: "#2563eb",
            shadowOpacity: 0.3,
            shadowOffset: { width: 0, height: 4 },
            shadowRadius: 8,
            elevation: 8,
          }}
        >
          <Text style={{ color: "#ffffff", fontSize: 30, lineHeight: 30, marginTop: -2 }}>+</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

export default function TabLayout() {
  return (
    <Tabs tabBar={(props) => <AppTabBar {...props} />} screenOptions={{ headerShown: false }}>
      <Tabs.Screen name="index" options={{ title: "홈" }} />
      <Tabs.Screen name="community" options={{ title: "커뮤니티" }} />
      <Tabs.Screen name="chat/index" options={{ title: "채팅" }} />
      <Tabs.Screen name="profile" options={{ title: "내 정보" }} />
    </Tabs>
  );
}
