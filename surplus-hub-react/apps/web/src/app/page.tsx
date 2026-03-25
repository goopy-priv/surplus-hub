"use client";

import { MaterialItem, useMaterials } from "@repo/core";
import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";

const CATEGORIES = [
  { emoji: "💡", label: "조명" },
  { emoji: "🚪", label: "문/창호" },
  { emoji: "🧱", label: "건축자재" },
  { emoji: "⚡", label: "전기/배선" },
  { emoji: "🔧", label: "설비/배관" },
  { emoji: "🏗️", label: "철강/금속" },
  { emoji: "🪵", label: "목재" },
  { emoji: "📦", label: "기타" },
] as const;

const REGIONS = [
  "전체",
  "서울특별시",
  "경기도",
  "인천광역시",
  "부산광역시",
  "대구광역시",
  "광주광역시",
  "대전광역시",
  "울산광역시",
  "세종특별자치시",
  "강원도",
  "충청북도",
  "충청남도",
  "전라북도",
  "전라남도",
  "경상북도",
  "경상남도",
  "제주특별자치도",
] as const;

const FIXED_SORT = "latest" as const;
const PAGE_SIZE = 20;

export default function Home() {
  const [searchInput, setSearchInput] = useState("");
  const [submittedKeyword, setSubmittedKeyword] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>(undefined);
  const [selectedRegion, setSelectedRegion] = useState<string>("전체");
  const [sortOption, setSortOption] = useState<"latest" | "price_asc" | "price_desc">("latest");
  const [page, setPage] = useState(1);
  const [materials, setMaterials] = useState<MaterialItem[]>([]);
  const [hasReachedMax, setHasReachedMax] = useState(false);

  const queryParams = useMemo(
    () => ({
      page,
      limit: PAGE_SIZE,
      category: selectedCategory,
      sort: sortOption,
      keyword: submittedKeyword.trim() ? submittedKeyword.trim() : undefined,
      location: selectedRegion !== "전체" ? selectedRegion : undefined,
    }),
    [page, selectedCategory, sortOption, submittedKeyword, selectedRegion]
  );

  const { data, isLoading, isFetching, error } = useMaterials(queryParams);

  useEffect(() => {
    setPage(1);
    setMaterials([]);
    setHasReachedMax(false);
  }, [selectedCategory, submittedKeyword, sortOption, selectedRegion]);

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

  const handleSearchSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmittedKeyword(searchInput);
  };

  const handleLoadMore = () => {
    if (hasReachedMax || isFetching) return;
    setPage((currentPage) => currentPage + 1);
  };

  const getCategoryEmoji = (category: string): string => {
    const found = CATEGORIES.find((c) => c.label === category);
    return found?.emoji || "📦";
  };

  const showInitialLoading = isLoading && page === 1 && materials.length === 0;

  if (showInitialLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error && materials.length === 0) {
    return <div className="p-4 text-center text-red-500">자재 목록을 불러오지 못했습니다.</div>;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header Section - mobile only */}
      <div className="bg-card border-b border-border px-4 py-3 md:hidden">
        <div className="flex items-center justify-between mb-3">
          <div className="relative flex items-center gap-1">
            <select
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="appearance-none cursor-pointer bg-transparent pr-5 text-sm font-medium text-foreground outline-none"
            >
              {REGIONS.map((region) => (
                <option key={region} value={region}>
                  {region}
                </option>
              ))}
            </select>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
              className="pointer-events-none absolute right-0 h-4 w-4 text-muted-foreground"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
            </svg>
          </div>
          <Link href="/notifications">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="h-6 w-6 text-foreground"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0"
              />
            </svg>
          </Link>
        </div>
        <h1 className="text-xl font-bold text-foreground">잉여자재</h1>
        <p className="text-sm text-muted-foreground">내 주변 잔여 자재를 찾아보세요</p>
      </div>

      <div className="container mx-auto max-w-2xl px-4 py-6">
        {/* Search bar - desktop only */}
        <div className="mb-6 hidden md:block">
          <form className="relative" onSubmit={handleSearchSubmit}>
            <input
              type="text"
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="시멘트, 파이프, 목재 검색..."
              className="w-full rounded-full border border-border bg-card p-4 pl-12 shadow-sm focus:border-primary focus:outline-none"
            />
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="absolute left-4 top-1/2 h-6 w-6 -translate-y-1/2 text-muted-foreground"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z"
              />
            </svg>
            <button
              type="submit"
              className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full bg-primary px-4 py-2 text-sm font-bold text-primary-foreground"
            >
              검색
            </button>
          </form>
        </div>

        {/* Categories Section */}
        <div className="mb-4 flex gap-2 overflow-x-auto pb-4 scrollbar-hide">
          {CATEGORIES.map((category) => (
            <button
              key={category.label}
              onClick={() => setSelectedCategory(category.label)}
              className={`flex items-center gap-2 whitespace-nowrap rounded-xl border px-4 py-2 text-sm font-medium transition-colors ${selectedCategory === category.label
                  ? "border-primary bg-accent text-accent-foreground"
                  : "border-border bg-card text-foreground hover:bg-muted"
                }`}
            >
              <span>{category.emoji}</span>
              <span>{category.label}</span>
            </button>
          ))}
        </div>

        {/* Sort dropdown */}
        <div className="mb-4 flex justify-end">
          <select
            value={sortOption}
            onChange={(e) => setSortOption(e.target.value as "latest" | "price_asc" | "price_desc")}
            className="cursor-pointer rounded-lg border border-border bg-card px-3 py-2 text-sm font-semibold text-foreground outline-none focus:border-primary focus:ring-1 focus:ring-primary"
          >
            <option value="latest">최신순</option>
            <option value="price_asc">가격 낮은순</option>
            <option value="price_desc">가격 높은순</option>
          </select>
        </div>

        {/* Material Cards List */}
        <div className="space-y-0">
          {materials.map((item) => (
            <Link href={`/material/${item.id}`} key={item.id} className="block">
              <div className="flex gap-4 border-b border-border bg-card p-4">
                {/* Left: Image */}
                <div className="h-28 w-28 flex-shrink-0 overflow-hidden rounded-xl bg-muted">
                  {item.imageUrl ? (
                    <img src={item.imageUrl} alt={item.title} className="h-full w-full object-cover" />
                  ) : (
                    <div className="flex h-full w-full items-center justify-center text-muted-foreground">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={1.5}
                        stroke="currentColor"
                        className="h-12 w-12"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z"
                        />
                      </svg>
                    </div>
                  )}
                </div>

                {/* Right: Content */}
                <div className="flex min-w-0 flex-1 flex-col justify-between">
                  {/* Title row */}
                  <div className="mb-1 flex items-start gap-2">
                    <span className="text-base">{getCategoryEmoji(item.category || "")}</span>
                    <h3 className="line-clamp-2 flex-1 text-sm font-medium text-foreground">{item.title}</h3>
                  </div>

                  {/* Status badge (if reserved/sold) */}
                  {(item.status === "RESERVED" || item.status === "SOLD") && (
                    <div className="mb-1">
                      <span className="inline-block rounded bg-accent px-2 py-0.5 text-[11px] text-accent-foreground">
                        {item.status === "RESERVED" ? "예약중" : "판매완료"}
                      </span>
                    </div>
                  )}

                  {/* Location + time */}
                  <div className="mb-2 text-xs text-muted-foreground">
                    <span>{item.location || "위치 정보 없음"}</span>
                    {item.createdAt && (
                      <>
                        <span className="mx-1">•</span>
                        <span>{new Date(item.createdAt).toLocaleDateString()}</span>
                      </>
                    )}
                  </div>

                  {/* Price */}
                  <div className="mb-1 text-base font-bold text-foreground">{item.price.toLocaleString()}원</div>

                  {/* Condition grade badge */}
                  {item.conditionGrade && (
                    <div className="mb-1">
                      <span
                        className={`inline-block rounded px-2 py-0.5 text-[11px] font-medium ${
                          item.conditionGrade === "상"
                            ? "bg-green-100 text-green-700"
                            : item.conditionGrade === "중"
                              ? "bg-orange-100 text-orange-700"
                              : "bg-red-100 text-red-700"
                        }`}
                      >
                        {item.conditionGrade}
                      </span>
                    </div>
                  )}

                  {/* Stats row - like count and inquiry text */}
                  <div className="flex items-center gap-3 text-xs text-muted-foreground">
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
                          d="M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 0 1-2.555-.337A5.972 5.972 0 0 1 5.41 20.97a5.969 5.969 0 0 1-.474-.065 4.48 4.48 0 0 0 .978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25Z"
                        />
                      </svg>
                      <span>문의</span>
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
                          d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z"
                        />
                      </svg>
                      <span>{item.likesCount ?? 0}</span>
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>

        {!showInitialLoading && materials.length === 0 ? (
          <div className="mt-12 flex flex-col items-center gap-4 text-center">
            <p className="text-lg font-medium text-foreground">아직 등록된 자재가 없어요</p>
            <p className="text-sm text-muted-foreground">첫 자재를 등록해보세요!</p>
            <Link href="/register" className="rounded-lg bg-primary px-6 py-3 text-sm font-bold text-primary-foreground">등록하기</Link>
          </div>
        ) : null}

        {!hasReachedMax && materials.length > 0 ? (
          <div className="mt-6 flex justify-center">
            <button
              type="button"
              onClick={handleLoadMore}
              disabled={isFetching}
              className="rounded-lg border border-border bg-card px-6 py-3 text-sm font-semibold text-foreground shadow-sm disabled:opacity-60"
            >
              {isFetching ? "불러오는 중..." : "더 보기"}
            </button>
          </div>
        ) : null}
      </div>

    </div>
  );
}
