import { apiClient, unwrapApiData, unwrapApiMeta } from "./client";
import { Event, EventsQueryParams, EventsResponse } from "../types";
import { readRecord, readString, normalizeIso } from "./utils";

const mapEvent = (raw: unknown): Event => {
  const item = readRecord(raw);

  return {
    id: String(item.id ?? ""),
    title: readString(item.title) || "제목 없음",
    description: readString(item.description) || "",
    imageUrl: readString(item.imageUrl ?? item.image_url),
    startDate: normalizeIso(item.startDate ?? item.start_date),
    endDate: normalizeIso(item.endDate ?? item.end_date),
    isActive: item.isActive === true || item.is_active === true,
    createdAt: normalizeIso(item.createdAt ?? item.created_at),
  };
};

export const fetchEvents = async (
  params: EventsQueryParams = {}
): Promise<EventsResponse> => {
  const response = await apiClient.get("/api/v1/events/", {
    params: {
      page: params.page ?? 1,
      limit: params.limit ?? 20,
    },
  });

  const rawItems = unwrapApiData<unknown[]>(response.data);
  const data = Array.isArray(rawItems) ? rawItems.map(mapEvent) : [];

  return {
    data,
    meta: unwrapApiMeta(response.data),
  };
};

export const fetchEvent = async (eventId: string): Promise<Event> => {
  const response = await apiClient.get(`/api/v1/events/${eventId}`);
  const rawItem = unwrapApiData<unknown>(response.data);
  return mapEvent(rawItem);
};
