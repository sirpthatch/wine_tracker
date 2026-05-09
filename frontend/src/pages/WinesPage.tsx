import { useEffect, useState, useCallback } from "react";
import type { Wine, WineCreate } from "../types/wine";
import { api } from "../api/client";
import { WineCard } from "../components/WineCard";
import { WineForm } from "../components/WineForm";
import { Stars } from "../components/Stars";

export function WinesPage() {
  const [wines, setWines] = useState<Wine[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAdd, setShowAdd] = useState(false);
  const [filterVarietal, setFilterVarietal] = useState("");
  const [filterRegion, setFilterRegion] = useState("");

  const loadWines = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.wines.list({
        varietal: filterVarietal || undefined,
        region: filterRegion || undefined,
      });
      setWines(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load wines");
    } finally {
      setLoading(false);
    }
  }, [filterVarietal, filterRegion]);

  useEffect(() => {
    loadWines();
  }, [loadWines]);

  const handleAdd = async (data: WineCreate) => {
    const created = await api.wines.create(data);
    setWines((prev) => [created, ...prev]);
    setShowAdd(false);
  };

  const handleUpdated = (updated: Wine) =>
    setWines((prev) => prev.map((w) => (w.id === updated.id ? updated : w)));

  const handleDeleted = (id: number) =>
    setWines((prev) => prev.filter((w) => w.id !== id));

  const avgRating =
    wines.filter((w) => w.rating).length > 0
      ? wines.reduce((acc, w) => acc + (w.rating ?? 0), 0) /
        wines.filter((w) => w.rating).length
      : null;

  const uniqueVarietals = new Set(wines.map((w) => w.varietal)).size;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">My Wine Cellar</h1>
        <button className="btn btn-primary" onClick={() => setShowAdd(true)}>
          + Add Wine
        </button>
      </div>

      {wines.length > 0 && (
        <div className="stats-bar">
          <div className="stat-card">
            <div className="stat-value">{wines.length}</div>
            <div className="stat-label">Wines Tried</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{uniqueVarietals}</div>
            <div className="stat-label">Varietals</div>
          </div>
          {avgRating && (
            <div className="stat-card">
              <div className="stat-value" style={{ fontSize: "1.1rem", paddingTop: "0.25rem" }}>
                <Stars rating={Math.round(avgRating)} />
              </div>
              <div className="stat-label">Avg Rating</div>
            </div>
          )}
        </div>
      )}

      <div className="filter-bar">
        <input
          className="form-input"
          placeholder="Filter by varietal..."
          value={filterVarietal}
          onChange={(e) => setFilterVarietal(e.target.value)}
        />
        <input
          className="form-input"
          placeholder="Filter by region..."
          value={filterRegion}
          onChange={(e) => setFilterRegion(e.target.value)}
        />
        {(filterVarietal || filterRegion) && (
          <button
            className="btn btn-secondary"
            onClick={() => {
              setFilterVarietal("");
              setFilterRegion("");
            }}
          >
            Clear
          </button>
        )}
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="spinner" />
      ) : wines.length === 0 ? (
        <div className="empty-state">
          <p>No wines logged yet.</p>
          <button className="btn btn-primary" onClick={() => setShowAdd(true)}>
            Add your first wine
          </button>
        </div>
      ) : (
        <div className="wine-grid">
          {wines.map((wine) => (
            <WineCard
              key={wine.id}
              wine={wine}
              onUpdated={handleUpdated}
              onDeleted={handleDeleted}
            />
          ))}
        </div>
      )}

      {showAdd && (
        <div className="modal-overlay" onClick={() => setShowAdd(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2 className="modal-title">Log a Wine</h2>
            <WineForm
              onSubmit={handleAdd}
              onCancel={() => setShowAdd(false)}
              submitLabel="Add Wine"
            />
          </div>
        </div>
      )}
    </div>
  );
}
