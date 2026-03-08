import { PaginationMeta } from "./material";

export interface Event {
  id: string;
  title: string;
  description: string;
  imageUrl?: string;
  startDate: string;
  endDate: string;
  isActive: boolean;
  createdAt: string;
}

export interface EventsResponse {
  data: Event[];
  meta?: PaginationMeta;
}

export interface EventsQueryParams {
  page?: number;
  limit?: number;
}
