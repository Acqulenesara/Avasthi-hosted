import React from "react";
import { motion } from "framer-motion";
import "./RecommenderCard.css";

const RecommendationCard = ({ title, description, image, score }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className="recommendation-card"
    >
      <img
        src={image || "https://via.placeholder.com/300x200.png?text=Activity"}
        alt={title}
        className="recommendation-image"
      />
      <h3 className="recommendation-title">{title}</h3>
      <p className="recommendation-desc">{description}</p>
      <p className="recommendation-score">
        Match Score: {(score * 100).toFixed(1)}%
      </p>
    </motion.div>
  );
};

export default RecommendationCard;
