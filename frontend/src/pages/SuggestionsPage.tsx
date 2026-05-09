import { useEffect, useState } from "react";
import type { Suggestion } from "../types/wine";
import { api } from "../api/client";

export function SuggestionsPage() {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.suggestions
      .list()
      .then(setSuggestions)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Failed to load suggestions")
      )
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Wine Suggestions</h1>
      </div>

      <p style={{ color: "var(--gray-600)", marginBottom: "1.5rem", fontSize: "0.92rem" }}>
        Personalized recommendations based on your highest-rated wines. Rate more
        wines (4+ stars) to improve suggestions.
      </p>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="spinner" />
      ) : suggestions.length === 0 ? (
        <div className="empty-state">
          <p>No suggestions yet.</p>
          <p style={{ fontSize: "0.85rem" }}>
            Start logging wines and rating them to get personalized recommendations.
          </p>
        </div>
      ) : (
        <div className="suggestion-grid">
          {suggestions.map((s, i) => (
            <div key={i} className="suggestion-card">
              <div className="suggestion-name">{s.name}</div>
              <div className="suggestion-varietal">{s.varietal}</div>
              <div className="suggestion-location">
                {s.region} &middot; {s.country}
              </div>
              <p className="suggestion-desc">{s.description}</p>
              <div className="suggestion-reason">💡 {s.reason}</div>
              <div className="suggestion-price">Est. {s.estimated_price_range}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
