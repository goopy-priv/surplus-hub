import { useQuery, UseQueryResult } from "@tanstack/react-query";
import { fetchEvent, fetchEvents } from "../api";
import { Event, EventsQueryParams, EventsResponse } from "../types";

export const useEvents = (params?: EventsQueryParams): UseQueryResult<EventsResponse> => {
  return useQuery<EventsResponse>({
    queryKey: ["events", params ?? {}],
    queryFn: () => fetchEvents(params),
  });
};

export const useEvent = (eventId: string): UseQueryResult<Event> => {
  return useQuery<Event>({
    queryKey: ["event", eventId],
    queryFn: () => fetchEvent(eventId),
    enabled: Boolean(eventId),
  });
};
