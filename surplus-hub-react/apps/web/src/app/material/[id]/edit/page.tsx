"use client";

import {
  useCurrentUser,
  useMaterialDetail,
  useUpdateMaterial,
} from "@repo/core";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { AuthGate } from "../../../../components/AuthGate";

const CATEGORIES = [
  { emoji: "🔩", label: "볼트/너트" },
  { emoji: "🪵", label: "목재" },
  { emoji: "🔧", label: "공구" },
  { emoji: "⚡", label: "전기자재" },
  { emoji: "🧱", label: "건축자재" },
  { emoji: "🛢️", label: "배관" },
  { emoji: "🏗️", label: "철강" },
  { emoji: "📦", label: "포장재" },
  { emoji: "🧪", label: "화학소재" },
  { emoji: "⚙️", label: "기타" },
] as const;

const TRADE_METHODS = [
  { label: "직거래", value: "DIRECT" },
  { label: "배송 협의", value: "DELIVERY" },
] as const;

const STATUS_OPTIONS = [
  { label: "판매중", value: "ACTIVE" },
  { label: "예약중", value: "RESERVED" },
  { label: "거래완료", value: "SOLD" },
] as const;

function EditContent({ id }: { id: string }) {
  const router = useRouter();
  const { data: item, isLoading: isLoadingItem } = useMaterialDetail(id);
  const { data: currentUser } = useCurrentUser();
  const { mutateAsync: updateMaterial, isPending: isSubmitting } = useUpdateMaterial(id);

  const [form, setForm] = useState({
    title: "",
    category: "",
    description: "",
    price: "",
    tradeMethod: "DIRECT" as string,
    status: "ACTIVE" as string,
    location: "위치 미정",
    quantity: "1",
    quantityUnit: "개",
  });
  const initializedRef = useRef(false);

  useEffect(() => {
    if (item && !initializedRef.current) {
      const matchedCategory = CATEGORIES.find(
        (cat) => item.category?.includes(cat.label) || cat.label.includes(item.category ?? "")
      );
      const categoryDisplay = matchedCategory
        ? `${matchedCategory.emoji} ${matchedCategory.label}`
        : item.category ?? "";

      setForm({
        title: item.title,
        category: categoryDisplay,
        description: item.description,
        price: String(item.price),
        tradeMethod: item.tradeMethod ?? "DIRECT",
        status: item.status ?? "ACTIVE",
        location: item.location || "위치 미정",
        quantity: item.quantity != null ? String(item.quantity) : "1",
        quantityUnit: item.quantityUnit ?? "개",
      });
      initializedRef.current = true;
    }
  }, [item]);

  // 소유자 확인: 로딩 완료 후 다른 사람이면 상세 페이지로 리다이렉트
  useEffect(() => {
    if (!isLoadingItem && item && currentUser && currentUser.id !== item.sellerId) {
      router.replace(`/material/${id}`);
    }
  }, [isLoadingItem, item, currentUser, id, router]);

  const handleSubmit = async () => {
    if (!form.title.trim() || !form.price) {
      alert("제목과 가격을 입력해주세요.");
      return;
    }

    const categoryLabel = CATEGORIES.find(
      (cat) => `${cat.emoji} ${cat.label}` === form.category
    )?.label ?? form.category;

    try {
      await updateMaterial({
        title: form.title.trim(),
        description: form.description.trim(),
        price: Number(form.price),
        quantity: form.quantity ? Number(form.quantity) : 1,
        quantityUnit: form.quantityUnit || "개",
        tradeMethod: form.tradeMethod,
        status: form.status,
        location: { address: form.location || "위치 미정" },
        category: categoryLabel,
      });
      router.push(`/material/${id}`);
    } catch {
      alert("수정 요청 중 오류가 발생했습니다.");
    }
  };

  if (isLoadingItem) {
    return (
      <div className="flex justify-center items-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!item) {
    return <div className="text-center p-8">자재를 찾을 수 없습니다.</div>;
  }

  return (
    <div className="bg-background min-h-screen">
      {/* Header */}
      <div className="sticky top-0 left-0 right-0 h-14 bg-card border-b border-border flex items-center justify-between px-4 z-50">
        <div className="flex items-center gap-3">
          <button onClick={() => router.back()} className="text-foreground">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
            </svg>
          </button>
          <h1 className="font-bold text-lg">자재 수정</h1>
        </div>
      </div>

      {/* Form */}
      <div className="p-4 max-w-lg mx-auto pb-28 space-y-5">
        {/* Title */}
        <div>
          <label className="block text-sm font-bold text-foreground mb-2">제목</label>
          <input
            type="text"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            className="w-full p-3 border border-border rounded-lg text-sm bg-card focus:border-primary focus:ring-1 focus:ring-primary outline-none"
          />
        </div>

        {/* Category */}
        <div>
          <label className="block text-sm font-bold text-foreground mb-2">카테고리</label>
          <div className="flex flex-wrap gap-2">
            {CATEGORIES.map((cat) => {
              const isSelected = form.category === `${cat.emoji} ${cat.label}`;
              return (
                <button
                  key={cat.label}
                  onClick={() => setForm({ ...form, category: `${cat.emoji} ${cat.label}` })}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isSelected
                      ? "bg-primary text-primary-foreground"
                      : "bg-secondary text-foreground hover:bg-accent"
                  }`}
                >
                  {cat.emoji} {cat.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-bold text-foreground mb-2">상세 설명</label>
          <textarea
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            className="w-full p-3 border border-border rounded-lg text-sm h-28 resize-none bg-card focus:border-primary focus:ring-1 focus:ring-primary outline-none"
          />
        </div>

        {/* Price */}
        <div>
          <label className="block text-sm font-bold text-foreground mb-2">가격</label>
          <div className="relative">
            <input
              type="text"
              value={form.price}
              inputMode="numeric"
              onChange={(e) => setForm({ ...form, price: e.target.value.replace(/\D/g, "") })}
              className="w-full p-3 border border-border rounded-lg text-sm bg-card focus:border-primary focus:ring-1 focus:ring-primary outline-none pr-12"
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-muted-foreground font-bold">원</span>
          </div>
        </div>

        {/* Quantity */}
        <div className="flex gap-3">
          <div className="flex-1">
            <label className="block text-sm font-bold text-foreground mb-2">수량</label>
            <input
              type="text"
              value={form.quantity}
              inputMode="numeric"
              onChange={(e) => setForm({ ...form, quantity: e.target.value.replace(/\D/g, "") })}
              className="w-full p-3 border border-border rounded-lg text-sm bg-card focus:border-primary focus:ring-1 focus:ring-primary outline-none"
            />
          </div>
          <div className="w-24">
            <label className="block text-sm font-bold text-foreground mb-2">단위</label>
            <input
              type="text"
              value={form.quantityUnit}
              onChange={(e) => setForm({ ...form, quantityUnit: e.target.value })}
              className="w-full p-3 border border-border rounded-lg text-sm bg-card focus:border-primary focus:ring-1 focus:ring-primary outline-none"
            />
          </div>
        </div>

        {/* Trade Method */}
        <div>
          <label className="block text-sm font-bold text-foreground mb-2">거래 방식</label>
          <div className="flex gap-2">
            {TRADE_METHODS.map((method) => {
              const isSelected = form.tradeMethod === method.value;
              return (
                <button
                  key={method.value}
                  onClick={() => setForm({ ...form, tradeMethod: method.value })}
                  className={`flex-1 py-3 rounded-lg text-sm font-medium border transition-colors ${
                    isSelected
                      ? "border-primary bg-primary/5 text-primary"
                      : "border-border bg-card text-foreground hover:bg-accent"
                  }`}
                >
                  {method.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Status */}
        <div>
          <label className="block text-sm font-bold text-foreground mb-2">판매 상태</label>
          <div className="flex gap-2">
            {STATUS_OPTIONS.map((option) => {
              const isSelected = form.status === option.value;
              return (
                <button
                  key={option.value}
                  onClick={() => setForm({ ...form, status: option.value })}
                  className={`flex-1 py-3 rounded-lg text-sm font-medium border transition-colors ${
                    isSelected
                      ? "border-primary bg-primary/5 text-primary"
                      : "border-border bg-card text-foreground hover:bg-accent"
                  }`}
                >
                  {option.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Location */}
        <div>
          <label className="block text-sm font-bold text-foreground mb-2">거래 위치</label>
          <input
            type="text"
            value={form.location}
            onChange={(e) => setForm({ ...form, location: e.target.value })}
            placeholder="거래 위치를 입력하세요"
            className="w-full p-3 border border-border rounded-lg text-sm bg-card focus:border-primary focus:ring-1 focus:ring-primary outline-none"
          />
        </div>
      </div>

      {/* Submit Button */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-card border-t border-border pb-safe z-50">
        <div className="max-w-lg mx-auto">
          <button
            onClick={handleSubmit}
            disabled={isSubmitting || !form.title.trim() || !form.price}
            className="w-full fab-gradient text-white rounded-xl py-4 font-bold disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90 transition-opacity"
          >
            {isSubmitting ? "수정 중..." : "수정 완료"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function MaterialEditPage({ params }: { params: { id: string } }) {
  return (
    <AuthGate title="자재 수정은 로그인 후 이용 가능합니다">
      <EditContent id={params.id} />
    </AuthGate>
  );
}
