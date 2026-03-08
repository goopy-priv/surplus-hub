"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useCurrentUser, useMyTransactions, useCompleteTransaction, useCreateReview } from "@repo/core";
import { AuthGate } from "../../../components/AuthGate";

const formatDate = (value: string): string => {
  const d = new Date(value);
  if (!Number.isFinite(d.getTime())) return "";
  return d.toLocaleDateString("ko-KR", { year: "numeric", month: "short", day: "numeric" });
};

const statusLabel = (status: string) => {
  switch (status) {
    case "PENDING": return { text: "대기중", color: "bg-yellow-100 text-yellow-700" };
    case "CONFIRMED": return { text: "확인됨", color: "bg-blue-100 text-blue-700" };
    case "COMPLETED": return { text: "완료", color: "bg-green-100 text-green-700" };
    case "CANCELLED": return { text: "취소됨", color: "bg-red-100 text-red-700" };
    default: return { text: status, color: "bg-gray-100 text-gray-700" };
  }
};

function PurchasesContent() {
  const router = useRouter();
  const { data: currentUser } = useCurrentUser();
  const { data, isLoading } = useMyTransactions({ limit: 50 });
  const completeMutation = useCompleteTransaction();
  const reviewMutation = useCreateReview();
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [reviewTarget, setReviewTarget] = useState<{ txId: string; sellerId: string; materialId: string } | null>(null);
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewContent, setReviewContent] = useState("");
  const [reviewedTxIds, setReviewedTxIds] = useState<Set<string>>(new Set());

  const handleComplete = (txId: string) => {
    setPendingId(txId);
    completeMutation.mutate(txId, {
      onError: () => alert("처리에 실패했습니다. 다시 시도해주세요."),
      onSettled: () => setPendingId(null),
    });
  };

  const purchases = (data?.data ?? []).filter(
    (tx) => currentUser && tx.buyerId === currentUser.id
  );

  return (
    <div className="min-h-screen bg-background pb-24">
      <div className="sticky top-0 z-10 flex items-center gap-3 border-b border-border bg-card px-4 py-3">
        <button onClick={() => router.back()} className="p-1">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-5 w-5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
          </svg>
        </button>
        <h1 className="text-base font-bold text-foreground">구매 내역</h1>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-primary" />
        </div>
      ) : purchases.length === 0 ? (
        <div className="px-4 py-20 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-8 w-8 text-muted-foreground">
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 7.5l-9-5.25L3 7.5m18 0-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9" />
            </svg>
          </div>
          <p className="text-sm text-muted-foreground">구매 내역이 없습니다</p>
        </div>
      ) : (
        <div className="divide-y divide-border">
          {purchases.map((tx) => {
            const st = statusLabel(tx.status);
            return (
              <div key={tx.id} className="bg-card px-4 py-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-foreground">{tx.materialTitle || `자재 #${tx.materialId}`}</p>
                    <p className="mt-0.5 text-xs text-muted-foreground">판매자: {tx.sellerName || "알 수 없음"}</p>
                    <p className="mt-0.5 text-xs text-muted-foreground">{formatDate(tx.createdAt)}</p>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <p className="text-sm font-bold text-foreground">{tx.price.toLocaleString()}원</p>
                    <span className={`inline-block rounded-full px-2 py-0.5 text-[10px] font-medium ${st.color}`}>{st.text}</span>
                    {tx.status === "CONFIRMED" && (
                      <button
                        onClick={() => handleComplete(tx.id)}
                        disabled={pendingId === tx.id}
                        className="mt-1 rounded-lg bg-green-500 px-3 py-1 text-xs font-medium text-white hover:bg-green-600 disabled:opacity-50"
                      >
                        {pendingId === tx.id ? "처리중..." : "완료"}
                      </button>
                    )}
                    {tx.status === "COMPLETED" && !reviewedTxIds.has(tx.id) && (
                      <button
                        onClick={() => {
                          setReviewTarget({ txId: tx.id, sellerId: tx.sellerId, materialId: tx.materialId });
                          setReviewRating(5);
                          setReviewContent("");
                        }}
                        className="mt-1 rounded-lg bg-primary px-3 py-1 text-xs font-medium text-primary-foreground hover:bg-primary/90"
                      >
                        리뷰 작성
                      </button>
                    )}
                    {tx.status === "COMPLETED" && reviewedTxIds.has(tx.id) && (
                      <span className="mt-1 inline-block rounded-lg bg-green-100 px-3 py-1 text-xs font-medium text-green-700">
                        리뷰 완료
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Review Modal */}
      {reviewTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
          <div className="w-full max-w-sm rounded-2xl bg-card p-6 shadow-xl">
            <h3 className="mb-4 text-base font-bold text-foreground">리뷰 작성</h3>
            {/* Star Rating */}
            <div className="mb-4 flex items-center gap-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() => setReviewRating(star)}
                  className="p-0.5"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill={star <= reviewRating ? "currentColor" : "none"}
                    stroke="currentColor"
                    strokeWidth={1.5}
                    className={`h-7 w-7 ${star <= reviewRating ? "text-yellow-400" : "text-gray-300"}`}
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
                  </svg>
                </button>
              ))}
              <span className="ml-2 text-sm text-muted-foreground">{reviewRating}점</span>
            </div>
            {/* Content */}
            <textarea
              value={reviewContent}
              onChange={(e) => setReviewContent(e.target.value)}
              placeholder="거래는 어떠셨나요? (선택)"
              className="mb-4 w-full resize-none rounded-lg border border-border bg-background p-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none"
              rows={3}
            />
            {/* Actions */}
            <div className="flex gap-2">
              <button
                onClick={() => setReviewTarget(null)}
                className="flex-1 rounded-lg border border-border px-4 py-2 text-sm font-medium text-muted-foreground hover:bg-accent"
              >
                취소
              </button>
              <button
                onClick={() => {
                  const sellerId = Number(reviewTarget.sellerId);
                  const materialId = Number(reviewTarget.materialId);
                  if (!Number.isFinite(sellerId) || sellerId <= 0) {
                    alert("판매자 정보가 올바르지 않습니다.");
                    return;
                  }
                  reviewMutation.mutate(
                    {
                      targetUserId: sellerId,
                      materialId: materialId || undefined,
                      rating: reviewRating,
                      content: reviewContent || undefined,
                    },
                    {
                      onSuccess: () => {
                        setReviewedTxIds((prev) => new Set(prev).add(reviewTarget.txId));
                        setReviewTarget(null);
                      },
                      onError: () => alert("리뷰 작성에 실패했습니다. 다시 시도해주세요."),
                    }
                  );
                }}
                disabled={reviewMutation.isPending}
                className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
              >
                {reviewMutation.isPending ? "제출 중..." : "제출"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function PurchasesPage() {
  return (
    <AuthGate title="구매 내역은 로그인 후 이용 가능합니다">
      <PurchasesContent />
    </AuthGate>
  );
}
