export interface Wine {
  id: number;
  name: string;
  varietal: string;
  producer: string | null;
  region: string | null;
  country: string | null;
  vintage: number | null;
  rating: number | null;
  notes: string | null;
  date_tried: string | null;
  price: number | null;
}

export type WineCreate = Omit<Wine, "id">;

export type WineUpdate = Partial<WineCreate>;

export interface Suggestion {
  name: string;
  varietal: string;
  region: string;
  country: string;
  description: string;
  reason: string;
  estimated_price_range: string;
}

// --- Local recommendations ---------------------------------------------------

export interface ScrapedWine {
  name: string;
  varietal: string | null;
  vintage: string | null;
  price: string | null;
  match_reason: string | null;
}

export interface NearbyStore {
  name: string;
  address: string;
  website: string | null;
  phone: string | null;
  distance_m: number;
  walking_minutes: number;
  inventory: ScrapedWine[];
  inventory_status: string;
}

export interface LocalRecommendationsResponse {
  geocoded_address: string;
  stores: NearbyStore[];
}
