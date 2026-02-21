export default function MealCard({ meal, index, minScore, maxScore }) {

  // ✅ UI-calibrated score (70–95)
  let displayScore = 85;

  if (maxScore > minScore) {
    displayScore =
      70 +
      ((meal.score - minScore) / (maxScore - minScore)) * 25;
  }

  displayScore = Math.round(displayScore);

  const badgeClass =
    displayScore >= 90 ? "high" :
    displayScore >= 80 ? "mid" : "low";

  return (
    <div className="meal-card">
      {/* Header */}
      <div className="meal-card-header">
        <h3>Meal #{index + 1}</h3>
        <span className="score-badge">
  Relevance: {displayScore}
</span>
      </div>

      {/* Food list */}
      <ul className="meal-items">
        {meal.foods.map((f, i) => (
          <li key={i}>
            <span className="food-name">{f.name}</span>
            <span className="food-meta">
              ({f.category}) — {f.calories} kcal
            </span>
          </li>
        ))}
      </ul>

      {/* Footer */}
      <div className="meal-footer">
        <strong>Total Calories:</strong>
        <span>{meal.total_calories}</span>
      </div>
    </div>
  );
}
