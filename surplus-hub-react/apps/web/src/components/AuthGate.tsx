"use client";

import { useUser } from "@clerk/nextjs";
import type { ReactNode } from "react";
import { shouldBypassAuth } from "./authGatePolicy";

const SHOULD_BYPASS_AUTH = shouldBypassAuth();

type AuthGateProps = {
  children: ReactNode;
  title?: string;
  description?: string;
};

export function AuthGate({
  children,
  title = "로그인이 필요합니다",
  description = "해당 화면은 로그인 후 이용할 수 있습니다.",
}: AuthGateProps) {
  const { isLoaded, isSignedIn } = useUser();

  // 1. 개발자 우회 모드이거나
  if (SHOULD_BYPASS_AUTH) {
    return <>{children}</>;
  }

  // 2. Clerk가 아직 로딩 중이면 로딩 스피너 표시
  if (!isLoaded) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-primary" />
      </div>
    );
  }

  // 3. 로그인이 되어 있다면 컨텐츠 표시
  if (isSignedIn) {
    return <>{children}</>;
  }

  // 4. 로그인이 안 되어 있다면 차단 화면 표시
  return (
    <div className="mx-auto flex min-h-[50vh] w-full max-w-xl items-center justify-center px-4">
      <div className="w-full rounded-2xl border border-gray-200 bg-white p-8 text-center shadow-sm">
        <h1 className="text-xl font-bold text-gray-900">{title}</h1>
        <p className="mt-2 text-sm text-gray-500">{description}</p>
        <p className="mt-2 text-xs text-gray-400">상단 로그인 버튼으로 로그인한 뒤 다시 확인해주세요.</p>
        <a
          href="/sign-in"
          className="mt-5 inline-block rounded-lg bg-primary px-5 py-3 text-sm font-bold text-white hover:bg-[#e65c00]"
        >
          로그인 하러 가기
        </a>
      </div>
    </div>
  );
}
