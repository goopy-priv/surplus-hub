import { apiClient, unwrapApiData } from "./client";
import { Notification, NotificationsResponse } from "../types";

const readRecord = (value: unknown): Record<string, unknown> =>
  value && typeof value === "object" ? (value as Record<string, unknown>) : {};

const readString = (value: unknown): string | undefined =>
  typeof value === "string" && value.trim().length > 0 ? value : undefined;

const readBoolean = (value: unknown, fallback = false): boolean => {
  if (typeof value === "boolean") return value;
  if (typeof value === "string") {
    if (value.toLowerCase() === "true") return true;
    if (value.toLowerCase() === "false") return false;
  }
  return fallback;
};

const normalizeIso = (value: unknown): string => {
  if (typeof value === "string" && value.trim()) return value;
  if (value instanceof Date) return value.toISOString();
  return new Date().toISOString();
};

const mapNotification = (raw: unknown): Notification => {
  const item = readRecord(raw);
  return {
    id: String(item.id ?? ""),
    type: readString(item.type ?? item.notification_type) || "SYSTEM",
    title: readString(item.title) || "",
    message: readString(item.message ?? item.body ?? item.content) || "",
    isRead: readBoolean(item.isRead ?? item.is_read, false),
    referenceId: readString(item.referenceId ?? item.reference_id),
    referenceType: readString(item.referenceType ?? item.reference_type),
    createdAt: normalizeIso(item.createdAt ?? item.created_at),
  };
};

export const fetchNotifications = async (): Promise<NotificationsResponse> => {
  const response = await apiClient.get("/api/v1/notifications/");
  const rawItems = unwrapApiData<unknown[]>(response.data);
  const data = Array.isArray(rawItems) ? rawItems.map(mapNotification) : [];
  return { data };
};

export const markAsRead = async (id: string): Promise<void> => {
  await apiClient.patch(`/api/v1/notifications/${id}/read`);
};

export const markAllAsRead = async (): Promise<void> => {
  await apiClient.patch("/api/v1/notifications/read-all");
};

export const fetchUnreadCount = async (): Promise<number> => {
  const response = await apiClient.get("/api/v1/notifications/unread-count");
  const raw = readRecord(unwrapApiData<unknown>(response.data));
  const count = raw.count ?? raw.unreadCount ?? raw.unread_count;
  if (typeof count === "number") return count;
  if (typeof count === "string") {
    const parsed = Number(count);
    return Number.isFinite(parsed) ? parsed : 0;
  }
  return 0;
};
