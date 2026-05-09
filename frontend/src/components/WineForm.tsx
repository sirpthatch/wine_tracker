import { useState } from "react";
import type { Wine, WineCreate } from "../types/wine";
import { Stars } from "./Stars";

interface WineFormProps {
  initial?: Partial<Wine>;
  onSubmit: (data: WineCreate) => Promise<void>;
  onCancel: () => void;
  submitLabel?: string;
}

const COMMON_VARIETALS = [
  "Cabernet Sauvignon",
  "Merlot",
  "Pinot Noir",
  "Syrah/Shiraz",
  "Zinfandel",
  "Sangiovese",
  "Nebbiolo",
  "Tempranillo",
  "Chardonnay",
  "Sauvignon Blanc",
  "Riesling",
  "Pinot Grigio",
  "Gewurztraminer",
  "Viognier",
  "Other",
];

export function WineForm({
  initial = {},
  onSubmit,
  onCancel,
  submitLabel = "Save",
}: WineFormProps) {
  const [form, setForm] = useState<WineCreate>({
    name: initial.name ?? "",
    varietal: initial.varietal ?? "",
    producer: initial.producer ?? "",
    region: initial.region ?? "",
    country: initial.country ?? "",
    vintage: initial.vintage ?? null,
    rating: initial.rating ?? null,
    notes: initial.notes ?? "",
    date_tried: initial.date_tried ?? new Date().toISOString().slice(0, 10),
    price: initial.price ?? null,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const set = (field: keyof WineCreate, value: unknown) =>
    setForm((f) => ({ ...f, [field]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await onSubmit(form);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="form" onSubmit={handleSubmit}>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="form-row">
        <div className="form-group" style={{ gridColumn: "1 / -1" }}>
          <label className="form-label">Wine Name *</label>
          <input
            className="form-input"
            value={form.name}
            onChange={(e) => set("name", e.target.value)}
            placeholder="e.g. Opus One 2019"
            required
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Varietal *</label>
          <input
            className="form-input"
            list="varietals"
            value={form.varietal}
            onChange={(e) => set("varietal", e.target.value)}
            placeholder="e.g. Cabernet Sauvignon"
            required
          />
          <datalist id="varietals">
            {COMMON_VARIETALS.map((v) => (
              <option key={v} value={v} />
            ))}
          </datalist>
        </div>

        <div className="form-group">
          <label className="form-label">Producer / Winery</label>
          <input
            className="form-input"
            value={form.producer ?? ""}
            onChange={(e) => set("producer", e.target.value || null)}
            placeholder="e.g. Robert Mondavi"
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Region</label>
          <input
            className="form-input"
            value={form.region ?? ""}
            onChange={(e) => set("region", e.target.value || null)}
            placeholder="e.g. Napa Valley"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Country</label>
          <input
            className="form-input"
            value={form.country ?? ""}
            onChange={(e) => set("country", e.target.value || null)}
            placeholder="e.g. USA"
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Vintage Year</label>
          <input
            className="form-input"
            type="number"
            value={form.vintage ?? ""}
            onChange={(e) =>
              set("vintage", e.target.value ? parseInt(e.target.value) : null)
            }
            placeholder="e.g. 2019"
            min={1800}
            max={2100}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Price ($)</label>
          <input
            className="form-input"
            type="number"
            value={form.price ?? ""}
            onChange={(e) =>
              set("price", e.target.value ? parseFloat(e.target.value) : null)
            }
            placeholder="e.g. 45"
            min={0}
            step={0.01}
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label className="form-label">Date Tried</label>
          <input
            className="form-input"
            type="date"
            value={form.date_tried ?? ""}
            onChange={(e) => set("date_tried", e.target.value || null)}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Rating</label>
          <Stars
            rating={form.rating}
            interactive
            onChange={(r) => set("rating", r)}
          />
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Tasting Notes</label>
        <textarea
          className="form-textarea"
          value={form.notes ?? ""}
          onChange={(e) => set("notes", e.target.value || null)}
          placeholder="Aromas, flavors, finish, food pairings..."
        />
      </div>

      <div className="form-actions">
        <button type="button" className="btn btn-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? "Saving..." : submitLabel}
        </button>
      </div>
    </form>
  );
}
