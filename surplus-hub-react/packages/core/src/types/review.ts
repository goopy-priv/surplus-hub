import { PaginationMeta } from "./material";

export interface Review {
  id: string;
  transactionId?: string;
  materialId?: string;
  reviewerId: string;
  reviewerName?: string;
  targetUserId: string;
  rating: number;
  content?: string;
  createdAt: string;
}

export interface ReviewsResponse {
  data: Review[];
  meta?: PaginationMeta;
}

export interface ReviewCreate {
  targetUserId: number;
  materialId?: number;
  rating: number;
  content?: string;
}

export interface ReviewsQueryParams {
  page?: number;
  limit?: number;
}
