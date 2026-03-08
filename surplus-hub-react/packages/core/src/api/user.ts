import { CurrentUser, UserStats } from "../types";
import { apiClient, unwrapApiData } from "./client";

const readNumber = (value: unknown, fallback = 0): number => {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string") {
    const numeric = Number(value);
    return Number.isFinite(numeric) ? numeric : fallback;
  }
  return fallback;
};

const readRecord = (value: unknown): Record<string, unknown> =>
  value && typeof value === "object" ? (value as Record<string, unknown>) : {};

const readString = (value: unknown): string | undefined =>
  typeof value === "string" && value.trim().length > 0 ? value : undefined;

const mapCurrentUser = (raw: Record<string, unknown>): CurrentUser => ({
  id: String(raw.id ?? ""),
  name: readString(raw.name),
  profileImageUrl: readString(raw.profileImageUrl ?? raw.profile_image_url),
  location: readString(raw.location),
  trustLevel: readNumber(raw.trustLevel ?? raw.trust_level, 0),
  mannerTemperature: readNumber(raw.mannerTemperature ?? raw.manner_temperature, 36.5),
});

const fetchCurrentUserRaw = async (): Promise<Record<string, unknown>> => {
  const response = await apiClient.get("/api/v1/users/me");
  return unwrapApiData<Record<string, unknown>>(response.data);
};

export const fetchCurrentUser = async (): Promise<CurrentUser> => {
  return mapCurrentUser(await fetchCurrentUserRaw());
};

export interface UserUpdateData {
  name?: string;
  location?: string;
  profile_image_url?: string;
}

export const updateProfile = async (data: UserUpdateData): Promise<CurrentUser> => {
  const response = await apiClient.put("/api/v1/users/me", data);
  return mapCurrentUser(readRecord(unwrapApiData<unknown>(response.data)));
};

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const fetchUserStats = async (_userId: string): Promise<UserStats> => {
  const userData = await fetchCurrentUserRaw();
  const currentUser = mapCurrentUser(userData);

  const stats = readRecord(userData.stats);
  const trustLevel = currentUser.trustLevel ?? readNumber(userData.trustLevel ?? userData.trust_level, 0);
  const mannerTemperature =
    currentUser.mannerTemperature ??
    readNumber(userData.mannerTemperature ?? userData.manner_temperature, 36.5);

  const ratingFromStats = readNumber(stats.rating, Number.NaN);
  const ratingFromTrustLevel = trustLevel > 0 ? trustLevel : Number((mannerTemperature / 20).toFixed(1));
  const rating = Number.isFinite(ratingFromStats) ? ratingFromStats : ratingFromTrustLevel;

  return {
    materialsSold: readNumber(stats.salesCount ?? stats.materialsSold, 0),
    materialsBought: readNumber(stats.purchaseCount ?? stats.materialsBought, 0),
    activeListings: readNumber(stats.activeListings, 0),
    rating,
    reviews: readNumber(stats.reviewCount ?? stats.reviews, 0),
    wishlistCount: readNumber(stats.wishlistCount ?? stats.wishlist_count, 0),
    communityPostsCount: readNumber(stats.communityPostsCount ?? stats.community_posts_count, 0),
  };
};
