import { useMutation, useQuery, useQueryClient, UseQueryResult, UseMutationResult } from "@tanstack/react-query";
import { createReview, fetchUserReviews } from "../api";
import { Review, ReviewCreate, ReviewsQueryParams, ReviewsResponse } from "../types";

export const useUserReviews = (userId: string, params?: ReviewsQueryParams): UseQueryResult<ReviewsResponse> => {
  return useQuery<ReviewsResponse>({
    queryKey: ["userReviews", userId, params ?? {}],
    queryFn: () => fetchUserReviews(userId, params),
    enabled: Boolean(userId),
  });
};

export const useCreateReview = (): UseMutationResult<Review, Error, ReviewCreate> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ReviewCreate) => createReview(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["userReviews"] });
    },
  });
};
