export default function Tabs({ active, setActive }) {
  return (
    <div className="tabs-container">
      <button
        className={`tab-btn ${active === "profile" ? "active" : ""}`}
        onClick={() => setActive("profile")}
      >
        👤 Profile
      </button>

      <button
        className={`tab-btn ${active === "recommend" ? "active" : ""}`}
        onClick={() => setActive("recommend")}
      >
        🍽️ Recommendations
      </button>
    </div>
  );
}
