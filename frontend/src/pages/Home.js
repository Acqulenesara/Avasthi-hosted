import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Home.css";
import "../pages/ResultPage.js";
import logo from "../assets/logo.png";
import meditationCharacter from "../assets/meditation_character.png"; // Replace with your image

const Home = () => {
  const navigate = useNavigate(); // Hook for navigation

  return (
    <>
      {/* Navbar */}
      <div className="navbar">
        <img src={logo} alt="Avasthi Logo" className="logo" />
        <div className="nav-links">
          <a href="/">HOME</a>
          <a href="/about">ABOUT US</a>
          <a href="/resources">RESOURCES</a>
          <a href="/contact">CONTACT</a>
        </div>
      </div>

      {/* Hero Section */}
      <div className="hero-section">
        <div className="text-content">
          <h2><b>A</b>spire to</h2>
          <h2><b>V</b>ibrance, embrace</h2>
          <h2><b>A</b>daptability with strength</h2>
          <h2><b>S</b>upport balance</h2>
          <h2><b>T</b>ranquility, compassion</h2>
          <h2><b>H</b>eal through hope and instill</h2>
          <h2><b>I</b>ndependence</h2>

          {/* Buttons to Redirect */}
          <button className="btn" onClick={() => navigate("/login")}>GET STARTED</button>
          <button className="btn secondary" onClick={() => navigate("/ResultPage")}>Check Well-being</button>
        </div>
        <img src={meditationCharacter} alt="Meditation Character" className="hero-image" />
      </div>

      {/* Resources Section */}
      <div className="resource-links">
  <button onClick={() => alert("Coming soon!")}>Mindfulness &rarr;</button>
  <button onClick={() => alert("Coming soon!")}>Meditation &rarr;</button>
  <button onClick={() => alert("Coming soon!")}>Stress &rarr;</button>
  <button onClick={() => alert("Coming soon!")}>Self-care &rarr;</button>
  <button onClick={() => alert("Coming soon!")}>Panic attacks &rarr;</button>
</div>


    </>
  );
};

export default Home;
