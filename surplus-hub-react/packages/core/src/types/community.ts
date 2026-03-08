import { PaginationMeta } from "./material";

export interface CommunityPost {
  id: string;
  title: string;
  content: string;
  category: string;
  imageUrl?: string;
  authorId: string;
  authorName: string;
  views: number;
  likesCount: number;
  createdAt: string;
}

export interface CommunityPostsResponse {
  data: CommunityPost[];
  meta?: PaginationMeta;
}


export interface CommunityPostCreate {
  title: string;
  content: string;
  category: string;
  imageUrl?: string;
}

export interface CommunityPostsQueryParams {
  page?: number;
  limit?: number;
  category?: string;
  authorId?: string;
}

