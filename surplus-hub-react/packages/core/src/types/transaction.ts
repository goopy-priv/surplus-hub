import { PaginationMeta } from "./material";

export interface TransactionCreate {
  material_id: number;
  note?: string;
}

export interface Transaction {
  id: string;
  materialId: string;
  materialTitle?: string;
  sellerId: string;
  sellerName?: string;
  buyerId: string;
  buyerName?: string;
  price: number;
  status: string;
  note?: string;
  createdAt: string;
  confirmedAt?: string;
  completedAt?: string;
}

export interface TransactionResponse {
  data: Transaction[];
  meta?: PaginationMeta;
}
