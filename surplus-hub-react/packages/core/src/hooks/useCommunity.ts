import { useMutation, useQuery, useQueryClient, UseQueryResult, UseMutationResult } from "@tanstack/react-query";
import { createCommunityPost, fetchCommunityPosts } from "../api";
import {
  CommunityPost,
  CommunityPostCreate,
  CommunityPostsQueryParams,
  CommunityPostsResponse,
} from "../types";

export const useCommunityPosts = (params?: CommunityPostsQueryParams): UseQueryResult<CommunityPostsResponse> => {
  return useQuery<CommunityPostsResponse>({
    queryKey: ["communityPosts", params ?? {}],
    queryFn: () => fetchCommunityPosts(params),
  });
};

export const useCreateCommunityPost = (): UseMutationResult<CommunityPost, Error, CommunityPostCreate> => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CommunityPostCreate) => createCommunityPost(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["communityPosts"] });
    },
  });
};
