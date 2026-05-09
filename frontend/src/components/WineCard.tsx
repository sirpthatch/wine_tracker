import { useState } from "react";
import type { Wine, WineCreate } from "../types/wine";
import { Stars } from "./Stars";
import { WineForm } from "./WineForm";
import { api } from "../api/client";

interface WineCardProps {
  wine: Wine;
  onUpdated: (wine: Wine) => void;
  onDeleted: (id: number) => void;
}

export function WineCard({ wine, onUpdated, onDeleted }: WineCardProps) {
  const [editing, setEditing] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const handleUpdate = async (data: WineCreate) => {
    const updated = await api.wines.update(wine.id, data);
    onUpdated(updated);
    setEditing(false);
  };

  const handleDelete = async () => {
    await api.wines.delete(wine.id);
    onDeleted(wine.id);
  };

  const meta = [
    wine.varietal,
    wine.vintage ? String(wine.vintage) : null,
    [wine.region, wine.country].filter(Boolean).join(", "),
  ].filter(Boolean);

  return (
    <>
      <div className="wine-card">
        <div className="wine-card-name">{wine.name}</div>

        <div className="wine-card-meta">
          {meta.map((m, i) => (
            <span key={i}>{m}</span>
          ))}
          {wine.producer && (
            <span style={{ color: "var(--wine-light)" }}>{wine.producer}</span>
          )}
        </div>

        {wine.rating && (
          <Stars rating={wine.rating} />
        )}

        {wine.notes && <p className="wine-card-notes">{wine.notes}</p>}

        <div className="wine-card-footer">
          <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
            {wine.price && (
              <span className="wine-card-badge">${wine.price.toFixed(0)}</span>
            )}
            {wine.date_tried && (
              <span className="wine-card-badge">
                {new Date(wine.date_tried + "T00:00:00").toLocaleDateString(
                  "en-US",
                  { month: "short", day: "numeric", year: "numeric" }
                )}
              </span>
            )}
          </div>
          <div style={{ display: "flex", gap: "0.4rem" }}>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setEditing(true)}
            >
              Edit
            </button>
            {confirmDelete ? (
              <>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={handleDelete}
                >
                  Confirm
                </button>
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => setConfirmDelete(false)}
                >
                  No
                </button>
              </>
            ) : (
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => setConfirmDelete(true)}
              >
                Delete
              </button>
            )}
          </div>
        </div>
      </div>

      {editing && (
        <div className="modal-overlay" onClick={() => setEditing(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2 className="modal-title">Edit Wine</h2>
            <WineForm
              initial={wine}
              onSubmit={handleUpdate}
              onCancel={() => setEditing(false)}
              submitLabel="Update Wine"
            />
          </div>
        </div>
      )}
    </>
  );
}
