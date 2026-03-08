/**
 * Shared date/format utilities for page components.
 */

/** Korean locale date string (e.g. "2024년 1월 15일") */
export const formatDate = (dateStr: string): string => {
  const d = new Date(dateStr);
  if (!Number.isFinite(d.getTime())) return "";
  return d.toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

/** Korean locale long date string (e.g. "2024년 1월 15일") using month: "long" */
export const formatDateLong = (dateStr: string): string => {
  const d = new Date(dateStr);
  if (!Number.isFinite(d.getTime())) return "";
  return d.toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};

/**
 * Relative time ago string.
 * Returns: 방금 전, n분 전, n시간 전, n일 전, or a formatted date for 30+ days.
 */
export const formatTimeAgo = (dateStr: string): string => {
  const time = new Date(dateStr).getTime();
  if (!Number.isFinite(time)) return "방금 전";

  const diffMinutes = Math.max(0, Math.floor((Date.now() - time) / 60000));
  if (diffMinutes < 1) return "방금 전";
  if (diffMinutes < 60) return `${diffMinutes}분 전`;

  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}시간 전`;

  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 30) return `${diffDays}일 전`;

  return new Date(dateStr).toLocaleDateString("ko-KR");
};

/**
 * Alias for formatTimeAgo. Some components used "formatRelativeTime" naming.
 */
export const formatRelativeTime = formatTimeAgo;

/** Transaction status Korean label with Tailwind color classes */
export const statusLabel = (
  status: string
): { text: string; color: string } => {
  switch (status) {
    case "PENDING":
      return { text: "대기중", color: "bg-yellow-100 text-yellow-700" };
    case "CONFIRMED":
      return { text: "확인됨", color: "bg-blue-100 text-blue-700" };
    case "COMPLETED":
      return { text: "완료", color: "bg-green-100 text-green-700" };
    case "CANCELLED":
      return { text: "취소됨", color: "bg-red-100 text-red-700" };
    default:
      return { text: status, color: "bg-gray-100 text-gray-700" };
  }
};

/** Check if an event is currently ongoing based on start/end dates */
export const isEventOngoing = (
  startDate: string,
  endDate: string
): boolean => {
  const now = Date.now();
  return (
    new Date(startDate).getTime() <= now && now <= new Date(endDate).getTime()
  );
};
