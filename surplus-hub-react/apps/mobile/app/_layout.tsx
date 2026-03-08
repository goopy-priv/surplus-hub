import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ClerkProvider, SignedIn, SignedOut, useSSO } from "@clerk/clerk-expo";
import { Stack } from "expo-router";
import { AUTH_TOKEN_CHANGE_EVENT, tokenCache } from "../utils/tokenCache";
import { ActivityIndicator, Alert, SafeAreaView, Text, TouchableOpacity, View } from "react-native";
import { type ReactNode, useCallback, useEffect, useState } from "react";
import { configureApiClient } from "@repo/core";
import * as Linking from "expo-linking";

const CLERK_PUBLISHABLE_KEY = process.env.EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY || "pk_test_YWRhcHRlZC1wZXJjaC0xNC5jbGVyay5hY2NvdW50cy5kZXYk";
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000";
const parseBooleanEnv = (key: string): boolean => {
  const value = process.env[key]?.trim().toLowerCase();
  return value === "1" || value === "true" || value === "yes" || value === "on";
};

const DEV_AUTH_BYPASS = parseBooleanEnv("EXPO_PUBLIC_DEV_AUTH_BYPASS");
const DEV_AUTH_E2E = parseBooleanEnv("EXPO_PUBLIC_DEV_AUTH_E2E");
const SHOULD_BYPASS_AUTH = DEV_AUTH_BYPASS;
const SHOULD_USE_LOCAL_AUTH_GATE = !SHOULD_BYPASS_AUTH && DEV_AUTH_E2E;

configureApiClient({
  baseUrl: API_BASE_URL,
  tokenProvider: async () => {
    const accessToken = await tokenCache.getToken("access_token");
    if (accessToken) return accessToken;
    return tokenCache.getToken("clerk_token");
  },
});

function SignedOutFallback() {
  const { startSSOFlow } = useSSO();
  const [isSigningIn, setIsSigningIn] = useState(false);

  const handleGoogleSignIn = async () => {
    try {
      setIsSigningIn(true);

      const { createdSessionId, setActive } = await startSSOFlow({
        strategy: "oauth_google",
        redirectUrl: Linking.createURL("/(tabs)"),
      });

      if (createdSessionId && setActive) {
        await setActive({ session: createdSessionId });
        return;
      }

      Alert.alert("로그인 실패", "세션을 생성하지 못했습니다.");
    } catch {
      Alert.alert("로그인 실패", "Google 로그인 중 오류가 발생했습니다.");
    } finally {
      setIsSigningIn(false);
    }
  };

  return (
    <SafeAreaView className="flex-1 items-center justify-center bg-gray-50 px-6">
      <View className="w-full max-w-sm rounded-2xl border border-gray-200 bg-white p-6">
        <Text className="text-center text-2xl font-bold text-gray-900">로그인이 필요합니다</Text>
        <Text className="mt-2 text-center text-sm text-gray-500">
          서비스 이용을 위해 계정에 로그인해주세요.
        </Text>
        <TouchableOpacity
          onPress={handleGoogleSignIn}
          disabled={isSigningIn}
          className="mt-5 rounded-lg bg-blue-600 py-3"
        >
          <Text className="text-center text-sm font-bold text-white">
            {isSigningIn ? "로그인 중..." : "Google로 로그인"}
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

function LocalAuthGate({ children }: { children: ReactNode }) {
  const [isReady, setIsReady] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isSigningIn, setIsSigningIn] = useState(false);

  const refreshAuthState = useCallback(async () => {
    const accessToken = await tokenCache.getToken("access_token");
    const clerkToken = accessToken ? null : await tokenCache.getToken("clerk_token");
    setIsAuthenticated(Boolean(accessToken || clerkToken));
    setIsReady(true);
  }, []);

  const handleDevSignIn = useCallback(async () => {
    setIsSigningIn(true);
    try {
      await tokenCache.saveToken("access_token", "mobile-e2e-token");
      await refreshAuthState();
    } finally {
      setIsSigningIn(false);
    }
  }, [refreshAuthState]);

  useEffect(() => {
    void refreshAuthState();

    if (typeof window === "undefined") return;

    const handleFocus = () => {
      void refreshAuthState();
    };
    const handleTokenChange = () => {
      void refreshAuthState();
    };

    window.addEventListener("focus", handleFocus);
    window.addEventListener(AUTH_TOKEN_CHANGE_EVENT, handleTokenChange);

    return () => {
      window.removeEventListener("focus", handleFocus);
      window.removeEventListener(AUTH_TOKEN_CHANGE_EVENT, handleTokenChange);
    };
  }, [refreshAuthState]);

  if (!isReady) {
    return (
      <SafeAreaView className="flex-1 items-center justify-center bg-gray-50">
        <ActivityIndicator size="large" color="#2563eb" />
      </SafeAreaView>
    );
  }

  if (isAuthenticated) {
    return <>{children}</>;
  }

  return (
    <SafeAreaView className="flex-1 items-center justify-center bg-gray-50 px-6">
      <View className="w-full max-w-sm rounded-2xl border border-gray-200 bg-white p-6">
        <Text className="text-center text-2xl font-bold text-gray-900">로그인이 필요합니다</Text>
        <Text className="mt-2 text-center text-sm text-gray-500">
          개발용 인증 모드입니다. 테스트 로그인을 통해 계속 진행할 수 있습니다.
        </Text>

        <TouchableOpacity
          onPress={() => {
            void handleDevSignIn();
          }}
          disabled={isSigningIn}
          className="mt-5 rounded-lg bg-blue-600 py-3"
        >
          <Text className="text-center text-sm font-bold text-white">
            {isSigningIn ? "로그인 중..." : "테스트 로그인"}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => {
            void refreshAuthState();
          }}
          className="mt-3 rounded-lg border border-gray-300 bg-white py-3"
        >
          <Text className="text-center text-sm font-bold text-gray-700">로그인 상태 다시 확인</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

function AppStack() {
  return (
    <Stack>
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="register" options={{ title: "자재 등록" }} />
      <Stack.Screen name="material/[id]" options={{ title: "자재 상세" }} />
      <Stack.Screen name="search" options={{ title: "검색" }} />
      <Stack.Screen name="notifications" options={{ title: "알림" }} />
    </Stack>
  );
}

export default function RootLayout() {
  const [queryClient] = useState(() => new QueryClient());

  return (
    <ClerkProvider publishableKey={CLERK_PUBLISHABLE_KEY} tokenCache={tokenCache}>
      <QueryClientProvider client={queryClient}>
        <SafeAreaView style={{ flex: 1 }}>
          {SHOULD_BYPASS_AUTH ? (
            <AppStack />
          ) : SHOULD_USE_LOCAL_AUTH_GATE ? (
            <LocalAuthGate>
              <AppStack />
            </LocalAuthGate>
          ) : (
            <>
              <SignedIn>
                <AppStack />
              </SignedIn>
              <SignedOut>
                <SignedOutFallback />
              </SignedOut>
            </>
          )}
        </SafeAreaView>
      </QueryClientProvider>
    </ClerkProvider>
  );
}
