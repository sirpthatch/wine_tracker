import { useState } from "react";
import type { NearbyStore, ScrapedWine } from "../types/wine";
import { api } from "../api/client";

const RADIUS_OPTIONS = [
  { label: "5 min (~400 m)", value: 400 },
  { label: "10 min (~800 m)", value: 800 },
  { label: "15 min (~1.2 km)", value: 1200 },
  { label: "20 min (~1.6 km)", value: 1600 },
];

export function LocalRecommendationsPage() {
  const [address, setAddress] = useState("");
  const [radius, setRadius] = useState(800);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [geocodedAddress, setGeocodedAddress] = useState<string | null>(null);
  const [stores, setStores] = useState<NearbyStore[] | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!address.trim()) return;
    setLoading(true);
    setError(null);
    setStores(null);
    setGeocodedAddress(null);
    try {
      const res = await api.localRecommendations.search(address.trim(), radius);
      setGeocodedAddress(res.geocoded_address);
      setStores(res.stores);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const matchedCount = stores?.reduce(
    (acc, s) => acc + s.inventory.filter((w) => w.match_reason).length,
    0
  );

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Local Wine Finder</h1>
      </div>

      <p style={{ color: "var(--gray-600)", marginBottom: "1.5rem", fontSize: "0.92rem" }}>
        Enter your address or a nearby landmark to find wine shops within walking
        distance. We'll check their inventory and highlight wines that match your
        taste profile.
      </p>

      {/* Search form */}
      <form className="card" style={{ marginBottom: "1.5rem" }} onSubmit={handleSearch}>
        <div className="form-row" style={{ alignItems: "flex-end" }}>
          <div className="form-group" style={{ flex: 3 }}>
            <label className="form-label">Your address or location</label>
            <input
              className="form-input"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="e.g. 123 Main St, San Francisco, CA"
              required
            />
          </div>
          <div className="form-group" style={{ flex: 1 }}>
            <label className="form-label">Walking distance</label>
            <select
              className="form-select"
              value={radius}
              onChange={(e) => setRadius(Number(e.target.value))}
            >
              {RADIUS_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group" style={{ flex: "0 0 auto" }}>
            <button className="btn btn-primary" type="submit" disabled={loading}>
              {loading ? "Searching…" : "Find Stores"}
            </button>
          </div>
        </div>

        <p
          style={{
            fontSize: "0.78rem",
            color: "var(--gray-400)",
            marginTop: "0.5rem",
          }}
        >
          Store locations are sourced from OpenStreetMap. Inventory is scraped
          directly from each store's website — results vary by site platform.
        </p>
      </form>

      {/* Loading */}
      {loading && (
        <div style={{ textAlign: "center", padding: "2rem" }}>
          <div className="spinner" />
          <p style={{ color: "var(--gray-600)", marginTop: "1rem", fontSize: "0.9rem" }}>
            Locating stores and checking inventory — this can take 10–20 seconds…
          </p>
        </div>
      )}

      {/* Error */}
      {error && <div className="alert alert-error">{error}</div>}

      {/* Results */}
      {stores !== null && !loading && (
        <>
          <div
            style={{
              background: "var(--gray-100)",
              borderRadius: "var(--radius-sm)",
              padding: "0.6rem 1rem",
              marginBottom: "1.25rem",
              fontSize: "0.85rem",
              color: "var(--gray-600)",
            }}
          >
            <span>
              Showing results near{" "}
              <strong style={{ color: "var(--gray-800)" }}>
                {geocodedAddress}
              </strong>
            </span>
            {stores.length > 0 && (
              <span>
                {" "}
                — {stores.length} store{stores.length !== 1 ? "s" : ""} found
                {matchedCount ? `, ${matchedCount} wines matching your taste` : ""}
              </span>
            )}
          </div>

          {stores.length === 0 ? (
            <div className="empty-state">
              <p>No wine stores found in OpenStreetMap within that radius.</p>
              <p style={{ fontSize: "0.85rem", marginTop: "0.5rem" }}>
                Try increasing the walking distance, or the area may not have
                wine shop data in OpenStreetMap yet.
              </p>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              {stores.map((store, i) => (
                <StoreCard key={i} store={store} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------

function StoreCard({ store }: { store: NearbyStore }) {
  const [expanded, setExpanded] = useState(store.inventory.length > 0);

  const matched = store.inventory.filter((w) => w.match_reason);
  const unmatched = store.inventory.filter((w) => !w.match_reason);
  const hasInventory = store.inventory.length > 0;

  return (
    <div className="card" style={{ padding: 0, overflow: "hidden" }}>
      {/* Header */}
      <div
        style={{
          padding: "1rem 1.25rem",
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          gap: "1rem",
        }}
      >
        <div style={{ flex: 1 }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.6rem",
              flexWrap: "wrap",
              marginBottom: "0.3rem",
            }}
          >
            <span
              style={{
                fontWeight: 700,
                fontSize: "1.05rem",
                color: "var(--wine-dark)",
              }}
            >
              {store.name}
            </span>
            <span className="wine-card-badge">
              {store.distance_m < 1000
                ? `${store.distance_m} m`
                : `${(store.distance_m / 1000).toFixed(1)} km`}
            </span>
            <span className="wine-card-badge">~{store.walking_minutes} min walk</span>
            {matched.length > 0 && (
              <span
                className="wine-card-badge"
                style={{
                  background: "rgba(114,47,55,0.12)",
                  color: "var(--wine)",
                }}
              >
                ★ {matched.length} match{matched.length !== 1 ? "es" : ""}
              </span>
            )}
          </div>

          <div
            style={{
              fontSize: "0.82rem",
              color: "var(--gray-600)",
              display: "flex",
              flexWrap: "wrap",
              gap: "0.3rem 1rem",
            }}
          >
            <span>{store.address}</span>
            {store.phone && <span>{store.phone}</span>}
            {store.website && (
              <a
                href={store.website}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "var(--wine)", textDecoration: "none" }}
              >
                {new URL(store.website).hostname} ↗
              </a>
            )}
          </div>
        </div>

        {hasInventory && (
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => setExpanded((e) => !e)}
          >
            {expanded ? "Hide inventory" : `Show ${store.inventory.length} wines`}
          </button>
        )}
      </div>

      {/* Inventory status */}
      <div
        style={{
          padding: "0.4rem 1.25rem",
          background: hasInventory ? "rgba(114,47,55,0.05)" : "var(--gray-50)",
          borderTop: "1px solid var(--gray-100)",
          fontSize: "0.78rem",
          color: hasInventory ? "var(--wine-dark)" : "var(--gray-400)",
          fontStyle: hasInventory ? "normal" : "italic",
        }}
      >
        {store.inventory_status}
      </div>

      {/* Inventory list */}
      {expanded && hasInventory && (
        <div style={{ padding: "0.75rem 1.25rem 1.25rem" }}>
          {matched.length > 0 && (
            <>
              <div
                style={{
                  fontSize: "0.75rem",
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                  color: "var(--wine)",
                  marginBottom: "0.5rem",
                }}
              >
                Matches your taste
              </div>
              {matched.map((w, i) => (
                <WineRow key={i} wine={w} highlight />
              ))}
              {unmatched.length > 0 && (
                <div
                  style={{
                    fontSize: "0.75rem",
                    fontWeight: 700,
                    textTransform: "uppercase",
                    letterSpacing: "0.06em",
                    color: "var(--gray-400)",
                    margin: "0.75rem 0 0.5rem",
                  }}
                >
                  Other wines
                </div>
              )}
            </>
          )}
          {unmatched.map((w, i) => (
            <WineRow key={i} wine={w} highlight={false} />
          ))}
        </div>
      )}
    </div>
  );
}

function WineRow({ wine, highlight }: { wine: ScrapedWine; highlight: boolean }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "baseline",
        justifyContent: "space-between",
        gap: "0.75rem",
        padding: "0.35rem 0",
        borderBottom: "1px solid var(--gray-100)",
      }}
    >
      <div style={{ flex: 1, minWidth: 0 }}>
        <span
          style={{
            fontWeight: highlight ? 600 : 400,
            color: highlight ? "var(--wine-dark)" : "var(--gray-800)",
            fontSize: "0.88rem",
          }}
        >
          {wine.name}
        </span>
        {wine.varietal && (
          <span
            style={{
              marginLeft: "0.5rem",
              fontSize: "0.75rem",
              color: "var(--gray-400)",
            }}
          >
            {wine.varietal}
            {wine.vintage ? ` · ${wine.vintage}` : ""}
          </span>
        )}
        {wine.match_reason && (
          <div style={{ fontSize: "0.75rem", color: "var(--wine-light)", marginTop: "0.1rem" }}>
            ✦ {wine.match_reason}
          </div>
        )}
      </div>
      {wine.price && (
        <span
          style={{
            fontSize: "0.85rem",
            fontWeight: 600,
            color: "var(--gray-600)",
            whiteSpace: "nowrap",
          }}
        >
          {wine.price}
        </span>
      )}
    </div>
  );
}
