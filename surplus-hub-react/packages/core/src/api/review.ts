import { apiClient, unwrapApiData, unwrapApiMeta } from "./client";
import { Review, ReviewCreate, ReviewsQueryParams, ReviewsResponse } from "../types";
import { readRecord, readString, readNumber, normalizeIso } from "./utils";

const mapReview = (raw: unknown): Review => {
  const item = readRecord(raw);

  return {
    id: String(item.id ?? ""),
    transactionId: readString(item.transactionId ?? item.transaction_id),
    materialId: readString(item.materialId ?? item.material_id),
    reviewerId: String(item.reviewerId ?? item.reviewer_id ?? ""),
    reviewerName: readString(item.reviewerName ?? item.reviewer_name),
    targetUserId: String(item.targetUserId ?? item.target_user_id ?? ""),
    rating: readNumber(item.rating, 0),
    content: readString(item.content),
    createdAt: normalizeIso(item.createdAt ?? item.created_at),
  };
};

export const fetchUserReviews = async (
  userId: string,
  params: ReviewsQueryParams = {}
): Promise<ReviewsResponse> => {
  const response = await apiClient.get(`/api/v1/reviews/user/${userId}`, {
    params: {
      page: params.page ?? 1,
      limit: params.limit ?? 20,
    },
  });

  const rawItems = unwrapApiData<unknown[]>(response.data);
  const data = Array.isArray(rawItems) ? rawItems.map(mapReview) : [];

  return {
    data,
    meta: unwrapApiMeta(response.data),
  };
};

export const fetchReview = async (reviewId: string): Promise<Review> => {
  const response = await apiClient.get(`/api/v1/reviews/${reviewId}`);
  const rawItem = unwrapApiData<unknown>(response.data);
  return mapReview(rawItem);
};

export const createReview = async (data: ReviewCreate): Promise<Review> => {
  const response = await apiClient.post("/api/v1/reviews/", data);
  const rawItem = unwrapApiData<unknown>(response.data);
  return mapReview(rawItem);
};
