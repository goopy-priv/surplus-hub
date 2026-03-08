"use client";

import {
  useCreateChatRoom,
  useCurrentUser,
  useDeleteMaterial,
  useMaterialDetail,
  useMaterialLikeStatus,
  useToggleMaterialLike,
} from "@repo/core";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";

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

export default function MaterialDetailPage({ params }: { params: { id: string } }) {
  const { data: item, isLoading } = useMaterialDetail(params.id);
  const { data: currentUser } = useCurrentUser();
  const { data: likeStatus } = useMaterialLikeStatus(params.id);
  const { mutate: toggleLike, isPending: isTogglingLike } = useToggleMaterialLike(params.id);
  const { mutateAsync: createChatRoom, isPending: isCreatingRoom } = useCreateChatRoom();
  const { mutate: deleteMaterial, isPending: isDeletingMaterial } = useDeleteMaterial();
  const router = useRouter();

  const isOwner = !!currentUser && !!item && currentUser.id === item.sellerId;
  const isLiked = likeStatus?.liked ?? false;
  const likesCount = likeStatus?.likesCount ?? item?.likesCount ?? 0;

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
      // Fall back to the chat list when room creation fails.
    }

    router.push("/chat");
  };

  const handleDelete = () => {
    if (!confirm("정말로 이 자재를 삭제하시겠습니까?")) return;
    deleteMaterial(params.id, {
      onSuccess: () => router.push("/"),
      onError: () => alert("자재 삭제에 실패했습니다. 다시 시도해주세요."),
    });
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!item) {
    return <div className="text-center p-8">자재를 찾을 수 없습니다.</div>;
  }

  const createdAt = new Date(item.createdAt).toLocaleDateString();
  const sellerDisplayName = item.sellerName || `판매자 #${item.sellerId}`;
  const locationLabel = item.location || "위치 정보 없음";
  const quantityLabel = formatQuantity(item.quantity, item.quantityUnit);
  const statusLabel = formatStatus(item.status);
  const tradeMethodLabel = formatTradeMethod(item.tradeMethod);

  return (
    <div className="bg-white dark:bg-gray-900 min-h-screen pb-24">
      {/* Header with Back Button */}
      <div className="fixed top-0 left-0 right-0 h-14 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md z-50 flex items-center px-4 border-b border-gray-100 dark:border-gray-700">
        <Link href="/" aria-label="뒤로가기" className="p-2 -ml-2 text-gray-800 dark:text-gray-200">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
          </svg>
        </Link>
        <h1 className="ml-2 font-bold text-lg truncate flex-1">{item.title}</h1>
        {isOwner ? (
          <div className="flex items-center gap-2">
            <Link
              href={`/material/${params.id}/edit`}
              className="text-sm text-primary font-medium px-2 py-1"
            >
              수정
            </Link>
            <button
              onClick={handleDelete}
              disabled={isDeletingMaterial}
              className="text-sm text-red-500 font-medium px-2 py-1 disabled:opacity-50"
            >
              삭제
            </button>
          </div>
        ) : (
          <button className="p-2" aria-label="공유">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-gray-600 dark:text-gray-400">
              <path strokeLinecap="round" strokeLinejoin="round" d="M7.217 10.907a2.25 2.25 0 1 0 0 2.186m0-2.186c.18.324.283.696.283 1.093s-.103.77-.283 1.093m0-2.186 9.566-5.314m-9.566 7.5 9.566 5.314m0 0a2.25 2.25 0 1 0 3.935 2.186 2.25 2.25 0 0 0-3.935-2.186Zm0-12.814a2.25 2.25 0 1 0 3.933-2.185 2.25 2.25 0 0 0-3.933 2.185Z" />
            </svg>
          </button>
        )}
      </div>

      {/* Main Content */}
      <div className="pt-14">
        {/* Image */}
        <div className="relative h-80 bg-gray-100 dark:bg-gray-800">
          {item.imageUrl ? (
            <Image src={item.imageUrl} alt={item.title} fill className="object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-16 h-16">
                <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
              </svg>
            </div>
          )}
        </div>

        {/* Seller Profile */}
        <div className="px-4 py-4 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-gray-200 dark:bg-gray-700 relative overflow-hidden">
              {item.sellerAvatarUrl ? (
                <Image src={item.sellerAvatarUrl} alt={sellerDisplayName} fill className="object-cover" />
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-full h-full text-gray-400 mt-2">
                  <path fillRule="evenodd" d="M7.5 6a4.5 4.5 0 1 1 9 0 4.5 4.5 0 0 1-9 0ZM3.751 20.105a8.25 8.25 0 0 1 16.498 0 .75.75 0 0 1-.437.695A18.683 18.683 0 0 1 12 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 0 1-.437-.695Z" clipRule="evenodd" />
                </svg>
              )}
            </div>
            <div>
              <h3 className="font-bold text-gray-900 dark:text-gray-100">{sellerDisplayName}</h3>
              <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
                <span>{locationLabel}</span>
                <span>•</span>
                <span className="text-primary font-medium">판매자 정보</span>
              </div>
            </div>
          </div>
          <div className="text-right text-xs text-gray-500 dark:text-gray-400">
            <p>판매자 ID</p>
            <p className="font-semibold text-gray-700 dark:text-gray-300">{item.sellerId || "-"}</p>
          </div>
        </div>

        <div className="p-4 space-y-6">
          {/* Material Info */}
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-1">{item.title}</h2>
            <div className="flex text-sm text-gray-500 dark:text-gray-400 mb-4">
              <span>{item.category}</span>
              <span className="mx-2">•</span>
              <span>{createdAt}</span>
            </div>
            <p className="text-gray-800 dark:text-gray-200 leading-relaxed whitespace-pre-wrap">
              {item.description}
            </p>
          </div>

          {/* AI Analysis */}
          <div className="bg-accent p-4 rounded-xl border border-accent-foreground/20">
            <div className="flex items-center gap-2 mb-2">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5 text-accent-foreground">
                <path fillRule="evenodd" d="M9 4.5a.75.75 0 0 1 .721.544l.813 2.846a3.75 3.75 0 0 0 2.576 2.576l2.846.813a.75.75 0 0 1 0 1.442l-2.846.813a3.75 3.75 0 0 0-2.576 2.576l-.813 2.846a.75.75 0 0 1-1.442 0l-.813-2.846a3.75 3.75 0 0 0-2.576-2.576l-2.846-.813a.75.75 0 0 1 0-1.442l2.846-.813a3.75 3.75 0 0 0 2.576-2.576l.813-2.846A.75.75 0 0 1 9 4.5ZM18 1.5a.75.75 0 0 1 .728.568l.258 1.036c.236.94.97 1.674 1.91 1.91l1.036.258a.75.75 0 0 1 0 1.456l-1.036.258c-.94.236-1.674.97-1.91 1.91l-.258 1.036a.75.75 0 0 1-1.456 0l-.258-1.036a2.625 2.625 0 0 0-1.91-1.91l-1.036-.258a.75.75 0 0 1 0-1.456l1.036-.258a2.625 2.625 0 0 0 1.91-1.91l.258-1.036A.75.75 0 0 1 18 1.5M16.5 15a.75.75 0 0 1 .712.513l.394 1.183c.15.447.5.799.948.948l1.183.395a.75.75 0 0 1 0 1.422l-1.183.395c-.447.15-.799.5-.948.948l-.395 1.183a.75.75 0 0 1-1.422 0l-.395-1.183a1.5 1.5 0 0 0-.948-.948l-1.183-.395a.75.75 0 0 1 0-1.422l1.183-.395c.447-.15.799-.5.948-.948l.395-1.183A.75.75 0 0 1 16.5 15Z" clipRule="evenodd" />
              </svg>
              <span className="font-bold text-accent-foreground">AI 분석</span>
            </div>
            <p className="text-sm text-accent-foreground leading-snug">
              등록 카테고리는 <span className="font-semibold">{item.category || "기타"}</span>이며 등록일은{" "}
              <span className="font-semibold">{createdAt}</span>입니다. 상세 조건은 채팅으로 확인해 주세요.
            </p>
          </div>

          <div className="rounded-xl bg-secondary p-4">
            <div className="mb-3 flex items-center justify-between text-sm">
              <span className="text-gray-500 dark:text-gray-400">상태</span>
              <span className="font-semibold text-gray-900 dark:text-gray-100">{statusLabel}</span>
            </div>
            <div className="mb-3 flex items-center justify-between text-sm">
              <span className="text-gray-500 dark:text-gray-400">카테고리</span>
              <span className="font-semibold text-gray-900 dark:text-gray-100">{item.category || "기타"}</span>
            </div>
            <div className="mb-3 flex items-center justify-between text-sm">
              <span className="text-gray-500 dark:text-gray-400">수량</span>
              <span className="font-semibold text-gray-900 dark:text-gray-100">{quantityLabel}</span>
            </div>
            <div className="mb-3 flex items-center justify-between text-sm">
              <span className="text-gray-500 dark:text-gray-400">거래 방식</span>
              <span className="font-semibold text-gray-900 dark:text-gray-100">{tradeMethodLabel}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500 dark:text-gray-400">위치</span>
              <span className="font-semibold text-gray-900 dark:text-gray-100">{locationLabel}</span>
            </div>
          </div>

          {/* Location Info */}
          <div>
            <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-3">거래 위치</h3>
            <div className="bg-gray-100 dark:bg-gray-800 h-40 rounded-lg flex items-center justify-center text-gray-400 dark:text-gray-500">
              <div className="text-center">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-8 h-8 mx-auto mb-2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z" />
                </svg>
                <span className="text-sm">지도 연동 준비 중</span>
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2 flex items-center gap-1">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-gray-400">
                <path fillRule="evenodd" d="M11.54 22.351l.07.04.028.016a.76.76 0 00.723 0l.028-.015.071-.041a16.975 16.975 0 001.144-.742 19.58 19.58 0 002.683-2.282c1.944-1.99 3.963-4.98 3.963-8.827a8.25 8.25 0 00-16.5 0c0 3.846 2.02 6.837 3.963 8.827a19.58 19.58 0 002.682 2.282 16.975 16.975 0 001.145.742zM12 13.5a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
              </svg>
              {locationLabel}
            </p>
          </div>
        </div>
      </div>

      {/* Bottom Action Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 safe-area-bottom flex items-center justify-between z-40">
        <div className="flex items-center gap-4">
          <button
            onClick={() => toggleLike(undefined, {
              onError: () => alert("좋아요 처리에 실패했습니다. 다시 시도해주세요."),
            })}
            disabled={isTogglingLike}
            className="flex flex-col items-center gap-0.5 text-gray-500 disabled:opacity-60"
          >
            {isLiked ? (
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6 text-red-500">
                <path d="m11.645 20.91-.007-.003-.022-.012a15.247 15.247 0 0 1-.383-.218 25.18 25.18 0 0 1-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0 1 12 5.052 5.5 5.5 0 0 1 16.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 0 1-4.244 3.17 15.247 15.247 0 0 1-.383.219l-.022.012-.007.004-.003.001a.752.752 0 0 1-.704 0l-.003-.001Z" />
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z" />
              </svg>
            )}
            <span className={`text-xs ${isLiked ? "text-red-500" : "text-gray-500"}`}>
              관심 {likesCount > 0 ? likesCount : ""}
            </span>
          </button>
          <div className="h-8 w-px bg-gray-200"></div>
          <div>
            <p className="font-bold text-lg text-foreground leading-none">{item.price.toLocaleString()}원</p>
            <p className="text-xs text-primary font-medium mt-0.5">거래 조건은 판매자와 협의</p>
          </div>
        </div>
        {isOwner ? (
          <Link
            href={`/material/${params.id}/edit`}
            className="bg-primary text-primary-foreground px-6 py-3 rounded-lg font-bold hover:bg-primary/90 transition-colors shadow-lg shadow-primary/30"
          >
            수정하기
          </Link>
        ) : (
          <button
            type="button"
            onClick={handleStartChat}
            disabled={isCreatingRoom}
            className="bg-primary text-primary-foreground px-6 py-3 rounded-lg font-bold hover:bg-primary/90 transition-colors shadow-lg shadow-primary/30 disabled:opacity-70"
          >
            {isCreatingRoom ? "채팅 연결 중..." : "판매자와 채팅"}
          </button>
        )}
      </div>
    </div>
  );
}
