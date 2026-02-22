import { useContext, useState, useEffect, useRef } from "react";
import { UserContext } from "../context/UserContext";
import { recommendDiet, wakeDietServer } from "../api/dietApi";
import MealCard from "./MealCard";

export default function RecommendationView() {
  const { user } = useContext(UserContext);
  const [meals, setMeals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [serverStatus, setServerStatus] = useState("warming"); // "warming" | "ready" | "slow"
  const pingDone = useRef(false);

  // Wake up the diet server as soon as this tab is shown
  useEffect(() => {
    if (pingDone.current) return;
    pingDone.current = true;
    wakeDietServer().then((ok) => {
      setServerStatus(ok ? "ready" : "slow");
    });
  }, []);

  async function getRecommendations() {
    setLoading(true);
    setError(null);
    try {
      const data = await recommendDiet(user);
      setMeals(data.recommendations || []);
    } catch (err) {
      console.error("❌ Diet recommendation error:", err);
      setError(err.message || "Failed to get recommendations. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  // Compute relative score bounds (ONCE)
  const scores = meals.map(m => m.score);
  const maxScore = scores.length ? Math.max(...scores) : 1;
  const minScore = scores.length ? Math.min(...scores) : 0;

  if (!user) {
    return (
      <div className="empty-state">
        <p>Please complete your profile first.</p>
      </div>
    );
  }

  return (
    <div className="recommendation-container">

      {/* WELCOME BANNER */}
      <div className="recommend-hero">
        <h1>👋 Welcome back, {user.name}!</h1>
        <p>Age: {user.age} | Activity: {user.activityLabel || "—"} | BMI: {user.bmi}</p>
      </div>

      {/* MENTAL HEALTH SUMMARY */}
      <section className="mental-summary">
        <h2>🎯 Your Mental Health Profile</h2>
        <div className="mental-cards">
          <div>🧘 Stress<br /><strong>{user.stress_relief}/10</strong></div>
          <div>😊 Mood<br /><strong>{user.mood_boost}/10</strong></div>
          <div>🌊 Anxiety<br /><strong>{user.anxiety_reduction}/10</strong></div>
          <div>😴 Sleep<br /><strong>{user.sleep_improvement}/10</strong></div>
          <div>🧠 Focus<br /><strong>{user.cognitive_function}/10</strong></div>
        </div>
      </section>

      {/* GENERATE MEAL PLAN */}
      <section className="generate-section">
        <h2>🍽️ Generate Your Meal Plan</h2>
        <p>AI-powered nutrition based on your mental wellness goals</p>

        {/* Server warm-up status */}
        {serverStatus === "warming" && (
          <p style={{ color: "#888", fontSize: "0.85rem", marginBottom: "0.5rem" }}>
            ⏳ Connecting to diet server...
          </p>
        )}
        {serverStatus === "slow" && (
          <p style={{ color: "#e8a838", fontSize: "0.85rem", marginBottom: "0.5rem" }}>
            ⚠️ Diet server is slow to respond — first request may take a moment.
          </p>
        )}

        <button
          className="primary-btn"
          onClick={getRecommendations}
          disabled={loading}
        >
          {loading ? "Analyzing..." : "Get Meal Plan"}
        </button>

        {loading && (
          <p className="loading-text">🤖 AI is analyzing your profile...</p>
        )}

        {error && (
          <p className="error-text" style={{ color: "red", marginTop: "1rem" }}>
            ⚠️ {error}
          </p>
        )}
      </section>

      {/* RESULTS */}
      <div className="meal-grid">
        {meals.map((meal, idx) => (
          <MealCard
            key={idx}
            meal={meal}
            index={idx}
            minScore={minScore}
            maxScore={maxScore}
          />
        ))}
      </div>
    </div>
  );
}
