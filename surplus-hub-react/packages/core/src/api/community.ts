import { apiClient, unwrapApiData, unwrapApiMeta } from "./client";
import {
  CommunityPost,
  CommunityPostCreate,
  CommunityPostsQueryParams,
  CommunityPostsResponse,
} from "../types";
import { readRecord, readString, readNumber, normalizeIso } from "./utils";

const mapCommunityPost = (raw: unknown): CommunityPost => {
  const item = readRecord(raw);

  return {
    id: String(item.id ?? ""),
    title: readString(item.title) || "제목 없음",
    content: readString(item.content) || "",
    category: readString(item.category) || "기타",
    imageUrl: readString(item.imageUrl ?? item.image_url),
    authorId: String(item.authorId ?? item.author_id ?? ""),
    authorName: readString(item.authorName ?? item.author_name) || "작성자 미상",
    views: readNumber(item.views, 0),
    likesCount: readNumber(item.likesCount ?? item.likes_count, 0),
    createdAt: normalizeIso(item.createdAt ?? item.created_at),
  };
};

export const fetchCommunityPosts = async (
  params: CommunityPostsQueryParams = {}
): Promise<CommunityPostsResponse> => {
  const response = await apiClient.get("/api/v1/community/posts", {
    params: {
      page: params.page ?? 1,
      limit: params.limit ?? 20,
      ...(params.category ? { category: params.category } : {}),
      ...(params.authorId ? { author_id: params.authorId } : {}),
    },
  });

  const rawItems = unwrapApiData<unknown[]>(response.data);
  const data = Array.isArray(rawItems) ? rawItems.map(mapCommunityPost) : [];

  return {
    data,
    meta: unwrapApiMeta(response.data),
  };
};

export const createCommunityPost = async (
  data: CommunityPostCreate
): Promise<CommunityPost> => {
  const response = await apiClient.post("/api/v1/community/posts", data);
  const rawItem = unwrapApiData<unknown>(response.data);
  return mapCommunityPost(rawItem);
};

export interface CommunityComment {
  id: string;
  postId: string;
  authorId: string;
  authorName: string;
  content: string;
  likesCount: number;
  createdAt: string;
}

const mapCommunityComment = (raw: unknown, postId: string): CommunityComment => {
  const item = readRecord(raw);
  return {
    id: String(item.id ?? ""),
    postId,
    authorId: String(item.authorId ?? item.author_id ?? ""),
    authorName: readString(item.authorName ?? item.author_name) || "익명",
    content: readString(item.content) || "",
    likesCount: readNumber(item.likesCount ?? item.likes_count, 0),
    createdAt: normalizeIso(item.createdAt ?? item.created_at),
  };
};

export const fetchCommunityPost = async (
  id: string
): Promise<CommunityPost> => {
  const response = await apiClient.get(`/api/v1/community/posts/${id}`);
  const rawItem = unwrapApiData<unknown>(response.data);
  return mapCommunityPost(rawItem);
};

export const fetchComments = async (
  postId: string
): Promise<CommunityComment[]> => {
  const response = await apiClient.get(
    `/api/v1/community/posts/${postId}/comments`
  );
  const rawItems = unwrapApiData<unknown[]>(response.data);
  return Array.isArray(rawItems)
    ? rawItems.map((item) => mapCommunityComment(item, postId))
    : [];
};

export const createComment = async (
  postId: string,
  content: string
): Promise<CommunityComment> => {
  const response = await apiClient.post(
    `/api/v1/community/posts/${postId}/comments`,
    { content }
  );
  const rawItem = unwrapApiData<unknown>(response.data);
  return mapCommunityComment(rawItem, postId);
};

export const togglePostLike = async (
  postId: string
): Promise<{ liked: boolean; likesCount: number }> => {
  const response = await apiClient.post(
    `/api/v1/community/posts/${postId}/like`
  );
  const raw = readRecord(unwrapApiData<unknown>(response.data));
  return {
    liked: Boolean(raw.isLiked ?? raw.liked ?? raw.is_liked ?? false),
    likesCount: readNumber(raw.likesCount ?? raw.likes_count, 0),
  };
};

export const updateCommunityPost = async (
  id: string,
  data: { title: string; content: string; category: string; imageUrl?: string }
): Promise<CommunityPost> => {
  const response = await apiClient.put(`/api/v1/community/posts/${id}`, data);
  const rawItem = unwrapApiData<unknown>(response.data);
  return mapCommunityPost(rawItem);
};

export const deleteCommunityPost = async (id: string): Promise<void> => {
  await apiClient.delete(`/api/v1/community/posts/${id}`);
};

export const updateComment = async (
  postId: string,
  commentId: string,
  content: string
): Promise<CommunityComment> => {
  const response = await apiClient.put(
    `/api/v1/community/posts/${postId}/comments/${commentId}`,
    { content }
  );
  const rawItem = unwrapApiData<unknown>(response.data);
  return mapCommunityComment(rawItem, postId);
};

export const deleteComment = async (
  postId: string,
  commentId: string
): Promise<void> => {
  await apiClient.delete(
    `/api/v1/community/posts/${postId}/comments/${commentId}`
  );
};
