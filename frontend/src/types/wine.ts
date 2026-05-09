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
