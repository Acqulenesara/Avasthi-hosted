import React, { useEffect, useState, useCallback } from "react";
import { motion } from "framer-motion";
import RecommendationCard from "./RecommenderCard";
import { jwtDecode } from "jwt-decode";
import "./recom.css";

export default function Recom() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [username, setUsername] = useState("");

  useEffect(() => {
    // ✅ Step 1: Get token and decode username
    const token = localStorage.getItem("token"); // ✅ match what you store in App.js
    if (!token) {
      console.error("⚠️ No token found. User may not be logged in.");
      setLoading(false);
      return;
    }
    try {
      const decoded = jwtDecode(token);
      console.log("✅ Decoded token:", decoded);
      setUsername(decoded.sub || decoded.username || ""); // fallback
    } catch (err) {
      console.error("⚠️ Failed to decode token:", err);
      setLoading(false);
    }
  }, []);

  const fetchRecs = useCallback(async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`http://127.0.0.1:8000/recommendations/?username=${username}&top_k=8`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });
      console.log("📡 Response status:", res.status);
      const data = await res.json();
      console.log("✅ Recommendations received:", data);
      const recs = Array.isArray(data) ? data : data.recommendations || [];
      setRecommendations(recs);
    } catch (err) {
      console.error("❌ Error fetching recommendations:", err);
    } finally {
      setLoading(false);
    }
  }, [username]);

  useEffect(() => {
    if (username) {
      console.log("📡 Fetching recommendations for:", username);
      fetchRecs();
    }
  }, [username, fetchRecs]);

  const handleFeedback = async (activity_title, liked = true) => {
    try {
      const token = localStorage.getItem("token");
      await fetch("http://127.0.0.1:8000/feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ username, activity_title, liked }),
      });
      fetchRecs(); // refresh recommendations
    } catch (err) {
      console.error("❌ Error saving feedback:", err);
    }
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <p>Loading recommendations...</p>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="dashboard-header">
        <h1>Mind Balance Dashboard</h1>
        <p>Personalized wellness activities just for you</p>
      </header>
      <div className="recommendations-grid">
        {recommendations.length > 0 ? (
          recommendations.map((rec, idx) => (
            <motion.div
              key={rec.id || rec.title || idx}
              whileHover={{ scale: 1.05 }}
              className="recommendation-card-wrapper"
            >
              <RecommendationCard
                title={rec.title}
                description={
                  rec.rationale ||
                  rec.short_description ||
                  rec.description ||
                  "No description available"
                }
                image={
                  rec.visual_asset_id
                    ? `/activities/${rec.visual_asset_id}`
                    : "/activities/activity.png"
                }
                score={rec.score}
              />
              <div className="feedback-buttons">
                <button
                  className="like-btn"
                  onClick={() => handleFeedback(rec.title, true)}
                >
                  👍 Like
                </button>
                <button
                  className="dislike-btn"
                  onClick={() => handleFeedback(rec.title, false)}
                >
                  👎 Dislike
                </button>
              </div>
            </motion.div>
          ))
        ) : (
          <p>No recommendations available right now.</p>
        )}
      </div>
    </div>
  );
}
//</div>
//  return (
//    <div className="app-container">
//      <header className="dashboard-header">
//        <h1>Mind Balance Dashboard</h1>
//        <p>Personalized wellness activities just for you</p>
//      </header>
//
//      <div className="recommendations-grid">
//        {recommendations.length > 0 ? (
//          recommendations.map((rec, idx) => (
//
//            <motion.div
//              key={idx}
//              whileHover={{ scale: 1.05 }}
//              className="recommendation-card-wrapper"
//            >
//              <RecommendationCard
//                title={rec.title}
//                description={rec.rationale || rec.short_description || rec.description || "No description available"}
//                image={
//                  rec.visual_asset_id
//                        ? `/activities/${rec.visual_asset_id}`
//                        : "/activities/activity.png"
//                }
//                score={rec.score }
//              />
//              <div className="feedback-buttons">
//                <button
//                  className="like-btn"
//                  onClick={() => handleFeedback(rec.title, true)}
//                >
//                  👍 Like
//                </button>
//                <button
//                  className="dislike-btn"
//                  onClick={() => handleFeedback(rec.title, false)}
//                >
//                  👎 Dislike
//                </button>
//              </div>
//            </motion.div>
//          ))
//        ) : (
//          <p>No recommendations available right now.</p>
//        )}
//      </div>
//    </div>
//  );
//}
