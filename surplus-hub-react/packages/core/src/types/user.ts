export interface CurrentUser {
  id: string;
  name?: string;
  profileImageUrl?: string;
  location?: string;
  trustLevel?: number;
  mannerTemperature?: number;
}

export interface UserStats {
  materialsSold: number;
  materialsBought: number;
  activeListings: number;
  rating: number;
  reviews: number;
  wishlistCount: number;
  communityPostsCount: number;
}
