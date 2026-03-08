import { useMutation, useQuery, useQueryClient, UseQueryResult, UseMutationResult } from "@tanstack/react-query";
import {
  confirmTransaction,
  completeTransaction,
  createTransaction,
  fetchMyTransactions,
  fetchTransactionDetail,
} from "../api";
import { Transaction, TransactionCreate, TransactionResponse } from "../types";

export const useMyTransactions = (params?: { page?: number; limit?: number; offset?: number; role?: "seller" | "buyer" }): UseQueryResult<TransactionResponse> => {
  return useQuery<TransactionResponse>({
    queryKey: ["myTransactions", params ?? {}],
    queryFn: () => fetchMyTransactions(params),
  });
};

export const useTransactionDetail = (transactionId: number): UseQueryResult<Transaction> => {
  return useQuery<Transaction>({
    queryKey: ["transaction", transactionId],
    queryFn: () => fetchTransactionDetail(transactionId),
    enabled: transactionId > 0,
  });
};

export const useCreateTransaction = (): UseMutationResult<Transaction, Error, TransactionCreate> => {
  const queryClient = useQueryClient();
  return useMutation<Transaction, Error, TransactionCreate>({
    mutationFn: createTransaction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["myTransactions"] });
    },
  });
};

export const useConfirmTransaction = (): UseMutationResult<Transaction, Error, string | number> => {
  const queryClient = useQueryClient();
  return useMutation<Transaction, Error, string | number>({
    mutationFn: confirmTransaction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["myTransactions"] });
    },
  });
};

export const useCompleteTransaction = (): UseMutationResult<Transaction, Error, string | number> => {
  const queryClient = useQueryClient();
  return useMutation<Transaction, Error, string | number>({
    mutationFn: completeTransaction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["myTransactions"] });
    },
  });
};
