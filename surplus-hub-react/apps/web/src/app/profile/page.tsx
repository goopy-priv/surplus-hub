"use client";

import { useRouter } from "next/navigation";
import { useCurrentUser, useUserStats } from "@repo/core";
import { AuthGate } from "../../components/AuthGate";

function ProfileContent() {
  const router = useRouter();
  const { data: currentUser, isLoading: isCurrentUserLoading } = useCurrentUser();
  const { data: stats, isLoading: isStatsLoading } = useUserStats(currentUser?.id);

  const handleSignOut = async () => {
    if (typeof window !== "undefined") {
      const clearLocalTokens = () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("clerk_token");
      };

      const clerkSignOut = (window as Window & { Clerk?: { signOut?: (args?: { redirectUrl?: string }) => Promise<void> } })
        .Clerk?.signOut;

      if (clerkSignOut) {
        clearLocalTokens();
        try {
          await clerkSignOut({ redirectUrl: "/" });
          return;
        } catch {
          window.location.href = "/";
          return;
        }
      }

      clearLocalTokens();
      window.location.href = "/";
    }
  };

  if (isCurrentUserLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-primary" />
      </div>
    );
  }

  if (!currentUser) {
    return (
      <div className="mx-auto max-w-xl px-4 py-10">
        <div className="rounded-2xl border border-gray-200 bg-white p-8 text-center shadow-sm">
          <h2 className="text-lg font-bold text-gray-900">프로필 정보를 불러오지 못했습니다</h2>
          <p className="mt-2 text-sm text-gray-500">
            인증 토큰이 없거나 만료되었을 수 있습니다. 다시 로그인해주세요.
          </p>
        </div>
      </div>
    );
  }

  const displayName = currentUser.name || "사용자";
  const displayImage = currentUser.profileImageUrl;
  const locationLabel = currentUser.location || "위치 정보 없음";
  const mannerTemperature = Number.isFinite(currentUser.mannerTemperature ?? Number.NaN)
    ? (currentUser.mannerTemperature as number)
    : 36.5;
  const mannerBarWidth = Math.max(10, Math.min(100, ((mannerTemperature - 30) / 20) * 100));

  const activityCards = [
    {
      label: "판매 내역",
      value: stats?.materialsSold ?? 0,
      href: "/profile/sales",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5 text-muted-foreground">
          <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 10.5V6a3.75 3.75 0 1 0-7.5 0v4.5m11.356-1.993 1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 0 1-1.12-1.243l1.264-12A1.125 1.125 0 0 1 5.513 7.5h12.974c.576 0 1.059.435 1.119 1.007ZM8.625 10.5a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm7.5 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
        </svg>
      ),
    },
    {
      label: "구매 내역",
      value: stats?.materialsBought ?? 0,
      href: "/profile/purchases",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5 text-muted-foreground">
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 7.5l-9-5.25L3 7.5m18 0-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9" />
        </svg>
      ),
    },
    {
      label: "관심 목록",
      value: stats?.wishlistCount ?? 0,
      href: "/profile/wishlist",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5 text-muted-foreground">
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z" />
        </svg>
      ),
    },
    {
      label: "커뮤니티 작성글",
      value: stats?.communityPostsCount ?? 0,
      href: "/profile/posts",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5 text-muted-foreground">
          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
        </svg>
      ),
    },
  ];

  const settingsItems = [
    { label: "알림 설정", href: "/notifications" },
    { label: "커뮤니티", href: "/community" },
    { label: "앱 정보", href: null as string | null },
  ];

  return (
    <div className="bg-background min-h-screen pb-24">
      {/* Header - Mobile only */}
      <div className="px-4 py-4 flex items-center justify-between md:hidden">
        <h1 className="text-lg font-bold text-foreground">마이페이지</h1>
        <button onClick={() => router.push("/profile/edit")} className="p-2">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z" />
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
          </svg>
        </button>
      </div>

      <div className="mx-4 space-y-4">
        {/* Profile Card */}
        <div className="bg-card rounded-2xl p-5 shadow-sm">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
              {displayImage ? (
                <img src={displayImage} alt={displayName} className="w-full h-full rounded-full object-cover" />
              ) : (
                <span className="text-2xl font-bold text-primary">{displayName.charAt(0)}</span>
              )}
            </div>
            <div className="flex-1">
              <h2 className="text-base font-bold text-foreground">{displayName}</h2>
              <p className="text-xs text-muted-foreground">{locationLabel}</p>
            </div>
            <div className="bg-accent rounded-full px-2.5 py-1 flex items-center gap-1">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-3 h-3 text-accent-foreground">
                <path fillRule="evenodd" d="M12.516 2.17a.75.75 0 0 0-1.032 0 11.209 11.209 0 0 1-7.877 3.08.75.75 0 0 0-.722.515A12.74 12.74 0 0 0 2.25 9.75c0 5.942 4.064 10.933 9.563 12.348a.749.749 0 0 0 .374 0c5.499-1.415 9.563-6.406 9.563-12.348 0-1.39-.223-2.73-.635-3.985a.75.75 0 0 0-.722-.516l-.143.001c-2.996 0-5.717-1.17-7.734-3.08Zm3.094 8.016a.75.75 0 1 0-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 0 0-1.06 1.06l2.25 2.25a.75.75 0 0 0 1.14-.094l3.75-5.25Z" clipRule="evenodd" />
              </svg>
              <span className="text-[11px] font-medium text-accent-foreground">인증회원</span>
            </div>
          </div>

          {/* Manner Temperature */}
          <div className="bg-secondary rounded-xl p-3">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-muted-foreground">
                  <path fillRule="evenodd" d="M12 2.25a.75.75 0 0 1 .75.75v.756a49.106 49.106 0 0 1 9.152 1 .75.75 0 0 1-.152 1.485h-1.918l2.474 10.124a.75.75 0 0 1-.375.84A6.723 6.723 0 0 1 18.75 18a6.723 6.723 0 0 1-3.181-.795.75.75 0 0 1-.375-.84l2.474-10.124H12.75v13.28c1.293.076 2.534.343 3.697.776a.75.75 0 0 1-.262 1.453h-8.37a.75.75 0 0 1-.262-1.453c1.162-.433 2.404-.7 3.697-.775V6.24H6.332l2.474 10.124a.75.75 0 0 1-.375.84A6.723 6.723 0 0 1 5.25 18a6.723 6.723 0 0 1-3.181-.795.75.75 0 0 1-.375-.84L4.168 6.241H2.25a.75.75 0 0 1-.152-1.485 49.105 49.105 0 0 1 9.152-1V3a.75.75 0 0 1 .75-.75Z" clipRule="evenodd" />
                </svg>
                <span className="text-xs font-medium text-muted-foreground">매너온도</span>
              </div>
              <span className="text-sm font-bold text-primary">{mannerTemperature.toFixed(1)}°C</span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-primary via-orange-500 to-red-500 rounded-full" style={{ width: `${mannerBarWidth}%` }} />
            </div>
          </div>
        </div>

        {/* Activity Grid */}
        <div className="grid grid-cols-2 gap-3">
          {activityCards.map((card) => (
            <div
              key={card.label}
              onClick={() => router.push(card.href)}
              className="cursor-pointer bg-card rounded-xl p-4 shadow-sm transition-colors hover:bg-muted/50 active:scale-[0.98]"
            >
              <div className="flex items-center gap-2 mb-2">
                {card.icon}
                <span className="text-xs text-muted-foreground">{card.label}</span>
              </div>
              <p className="text-2xl font-bold text-foreground">
                {isStatsLoading ? "-" : card.value}
              </p>
            </div>
          ))}
        </div>

        {/* Settings Section */}
        <div className="bg-card rounded-xl shadow-sm divide-y divide-border">
          {settingsItems.map((item, i) => (
            <div
              key={i}
              onClick={() => item.href && router.push(item.href)}
              className={`p-4 flex items-center justify-between ${item.href ? "hover:bg-muted/50 cursor-pointer" : "opacity-60"}`}
            >
              <span className="text-sm font-medium text-foreground">{item.label}</span>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4 text-muted-foreground">
                <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
              </svg>
            </div>
          ))}
          <div onClick={() => void handleSignOut()} className="p-4 flex items-center justify-between hover:bg-destructive/10 cursor-pointer">
            <span className="text-sm font-medium text-destructive">로그아웃</span>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4 text-destructive">
              <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ProfilePage() {
  return (
    <AuthGate title="프로필은 로그인 후 이용 가능합니다">
      <ProfileContent />
    </AuthGate>
  );
}
