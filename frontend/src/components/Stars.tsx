interface StarsProps {
  rating: number | null;
  interactive?: boolean;
  onChange?: (rating: number) => void;
}

export function Stars({ rating, interactive = false, onChange }: StarsProps) {
  return (
    <div className="stars">
      {[1, 2, 3, 4, 5].map((n) => (
        <span
          key={n}
          className={n <= (rating ?? 0) ? "star-filled" : "star-empty"}
          style={interactive ? { cursor: "pointer" } : undefined}
          onClick={() => interactive && onChange?.(n)}
        >
          ★
        </span>
      ))}
    </div>
  );
}
