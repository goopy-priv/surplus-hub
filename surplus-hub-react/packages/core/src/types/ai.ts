export interface AiImageAnalysis {
  title: string;
  category: string;
  description: string;
  condition?: string;
}

export interface AiDescription {
  description: string;
}

export interface AiPriceSuggestion {
  price: number;
  marketPrice: {
    min: number;
    ideal: number;
    max: number;
    recentTrades: number;
  };
  reasoning?: string;
}

export interface AiChatSuggestion {
  suggestions: string[];
}

export interface AiCommunityAnswer {
  answer: string;
}

export interface AiDiscussionSummary {
  summary: string[];
}

export interface AiSearchParams {
  q: string;
  page?: number;
  limit?: number;
  category?: string;
  priceMin?: number;
  priceMax?: number;
  locationLat?: number;
  locationLng?: number;
  radiusKm?: number;
  dateFrom?: string;
  dateTo?: string;
  tradeMethod?: string;
  sortBy?: string;
}

export interface AiSearchResult {
  id: string;
  title: string;
  description?: string;
  price: number;
  category?: string;
  location?: string;
  imageUrl?: string;
  score?: number;
}

export interface AiSearchResponse {
  data: AiSearchResult[];
  total: number;
  page: number;
}

export interface AiSearchSuggestions {
  suggestions: string[];
}

export interface Category {
  id: string | number;
  name: string;
  slug?: string;
}
