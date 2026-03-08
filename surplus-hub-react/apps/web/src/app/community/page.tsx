"use client";

import { useRouter } from "next/navigation";
import { useCommunityPosts } from "@repo/core";
import { useMemo, useState } from "react";

const CATEGORIES = ["전체", "QnA", "노하우", "안전", "정보"] as const;

const formatTimeAgo = (value: string): string => {
  const time = new Date(value).getTime();
  if (!Number.isFinite(time)) return "방금";

  const diffMinutes = Math.max(0, Math.floor((Date.now() - time) / 60000));
  if (diffMinutes < 1) return "방금";
  if (diffMinutes < 60) return `${diffMinutes}분 전`;

  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}시간 전`;

  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 30) return `${diffDays}일 전`;

  return new Date(value).toLocaleDateString();
};

const getCategoryColor = (category: string) => {
  switch (category) {
    case "QnA":
      return {
        bg: "bg-purple-50",
        text: "text-purple-700",
        border: "border-purple-200",
      };
    case "노하우":
      return {
        bg: "bg-blue-50",
        text: "text-blue-700",
        border: "border-blue-200",
      };
    case "안전":
      return {
        bg: "bg-orange-50",
        text: "text-orange-700",
        border: "border-orange-200",
      };
    case "정보":
      return {
        bg: "bg-yellow-50",
        text: "text-yellow-700",
        border: "border-yellow-200",
      };
    default:
      return {
        bg: "bg-muted",
        text: "text-muted-foreground",
        border: "border-border",
      };
  }
};

export default function CommunityPage() {
  const router = useRouter();
  const [selectedCategory, setSelectedCategory] = useState<(typeof CATEGORIES)[number]>("전체");

  const params = useMemo(
    () => ({
      page: 1,
      limit: 20,
      category: selectedCategory === "전체" ? undefined : selectedCategory,
    }),
    [selectedCategory]
  );

  const { data, isLoading, error } = useCommunityPosts(params);
  const posts = data?.data ?? [];

  return (
    <div className="min-h-screen bg-background">
      <div className="border-b border-border bg-card px-4 py-6">
        <h1 className="mb-2 text-xl font-bold text-foreground md:hidden">커뮤니티 게시판</h1>
        <p className="text-sm text-muted-foreground">
          지식을 공유하고, 질문하고, 다른 건설인들과 소통하세요.
        </p>
      </div>

      <div className="mt-4 overflow-x-auto px-4 pb-2 scrollbar-hide">
        <div className="flex gap-2">
          {CATEGORIES.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`whitespace-nowrap rounded-full px-5 py-2 text-sm font-medium transition-all ${
                selectedCategory === category
                  ? "bg-primary text-white shadow-md"
                  : "border border-border bg-secondary text-muted-foreground hover:bg-accent"
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="p-8 text-center text-sm text-muted-foreground">게시글을 불러오는 중...</div>
      ) : null}

      {error ? (
        <div className="p-8 text-center text-sm text-red-500">게시글을 불러오지 못했습니다.</div>
      ) : null}

      {!isLoading && !error ? (
        <div className="p-4">
          {posts.map((post) => {
            const catColors = getCategoryColor(post.category);

            return (
              <div
                key={post.id}
                onClick={() => router.push(`/community/${post.id}`)}
                className="cursor-pointer border-b border-border bg-card p-4 transition-shadow hover:shadow-md active:bg-muted/50"
              >
                <div className="mb-2 flex items-center justify-between">
                  <div
                    className={`inline-block rounded-full border px-2 py-0.5 text-xs font-medium ${catColors.bg} ${catColors.text} ${catColors.border}`}
                  >
                    {post.category}
                  </div>
                  <span className="text-xs text-muted-foreground">{formatTimeAgo(post.createdAt)}</span>
                </div>

                <h3 className="mb-1 text-sm font-bold text-foreground">{post.title}</h3>
                <p className="mb-2 line-clamp-2 text-xs text-muted-foreground">{post.content}</p>

                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>{post.authorName}</span>
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-1">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={1.5}
                        stroke="currentColor"
                        className="h-4 w-4"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M6.633 10.5c.806 0 1.533-.446 2.031-1.08a9.041 9.041 0 012.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 00.322-1.672V3a.75.75 0 01.75-.75A2.25 2.25 0 0116.5 4.5c0 1.152-.26 2.247-.723 3.218-.266.558.107 1.282.725 1.282h3.126c1.026 0 1.945.694 2.054 1.715.045.422.068.85.068 1.285a11.95 11.95 0 01-2.649 7.521c-.388.482-.987.729-1.605.729H13.48c-.483 0-.964-.078-1.423-.23l-3.114-1.04a4.501 4.501 0 00-1.423-.23H5.904M14.25 9h2.25M5.904 18.75c.083.205.173.405.27.602.197.4-.078.898-.523.898h-.908c-.889 0-1.713-.518-1.972-1.368a12 12 0 01-.521-3.507c0-1.553.295-3.036.831-4.398C3.387 10.203 4.167 9.75 5 9.75h1.053c.472 0 .745.556.5.96a8.958 8.958 0 00-1.302 4.665c0 1.194.232 2.333.654 3.375z"
                        />
                      </svg>
                      <span>{post.likesCount}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={1.5}
                        stroke="currentColor"
                        className="h-4 w-4"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z"
                        />
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"
                        />
                      </svg>
                      <span>{post.views}</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}

          {posts.length === 0 ? (
            <div className="rounded-xl border border-dashed border-border bg-card p-8 text-center text-sm text-muted-foreground">
              조건에 맞는 게시글이 없습니다.
            </div>
          ) : null}
        </div>
      ) : null}

      <button
        onClick={() => router.push("/community/write")}
        className="fixed bottom-24 right-4 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-b from-primary to-[#e65c00] text-white shadow-lg shadow-primary/30 hover:shadow-xl"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          className="h-6 w-6"
        >
          <path d="M21.731 2.269a2.625 2.625 0 00-3.712 0l-1.157 1.157 3.712 3.712 1.157-1.157a2.625 2.625 0 000-3.712zM19.513 8.199l-3.712-3.712-12.15 12.15a5.25 5.25 0 00-1.32 2.214l-.8 2.685a.75.75 0 00.933.933l2.685-.8a5.25 5.25 0 002.214-1.32L19.513 8.2z" />
        </svg>
      </button>
    </div>
  );
}
