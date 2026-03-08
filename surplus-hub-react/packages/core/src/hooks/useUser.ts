import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from "@tanstack/react-query";
import { fetchCurrentUser, fetchUserStats, updateProfile, UserUpdateData } from "../api";
import { CurrentUser, UserStats } from "../types";

export const useCurrentUser = (): UseQueryResult<CurrentUser> => {
  return useQuery<CurrentUser>({
    queryKey: ["currentUser"],
    queryFn: fetchCurrentUser,
  });
};

export const useUserStats = (userId: string | undefined): UseQueryResult<UserStats> => {
  return useQuery<UserStats>({
    queryKey: ["userStats", userId],
    queryFn: () => fetchUserStats(userId!),
    enabled: !!userId,
  });
};

export const useUpdateProfile = (): UseMutationResult<CurrentUser, Error, UserUpdateData> => {
  const queryClient = useQueryClient();
  return useMutation<CurrentUser, Error, UserUpdateData>({
    mutationFn: updateProfile,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["currentUser"] });
    },
  });
};
