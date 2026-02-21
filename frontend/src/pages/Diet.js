import { useState } from "react";
// ✅ CORRECT PATHS (based on your structure)
import ProfileForm from "./diet/components/ProfileForm";
import RecommendationView from "./diet/components/RecommendationView";
import { UserContext } from "./diet/context/UserContext";
import "./diet/styles/Diet.css";


export default function Diet() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState("profile");

  return (
    <UserContext.Provider value={{ user, setUser }}>
      <div className="diet-page">

        {/* Tabs */}
        <div className="tabs-container">
          <button
            className={`tab-btn ${activeTab === "profile" ? "active" : ""}`}
            onClick={() => setActiveTab("profile")}
          >
            🧍 Profile
          </button>

          <button
            className={`tab-btn ${activeTab === "recommendations" ? "active" : ""}`}
            onClick={() => setActiveTab("recommendations")}
            disabled={!user}
          >
            🍽 Recommendations
          </button>
        </div>

        {/* Content */}
        {activeTab === "profile" && <ProfileForm />}
        {activeTab === "recommendations" && <RecommendationView />}
      </div>
    </UserContext.Provider>
  );
}
