import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Signup.css";
import PSSQuestionnaire from "./pssquestionnaire";
import logo from "../assets/logo.png";
import character from "../assets/character.png";

const Signup = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

  const handleSignup = async () => {
    if (!username || !password) {
      setErrorMessage("⚠️ Please fill in all fields!");
      return;
    }

    try {
      // 1️⃣ Register new user
      const registerResponse = await fetch("http://127.0.0.1:8000/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      const registerData = await registerResponse.json();

      if (!registerResponse.ok) {
        setErrorMessage(registerData.detail || "❌ Signup failed. Try again.");
        return;
      }

      // ✅ Registration successful
      alert("✅ Signup successful! Please complete the questionnaire.");
      // Store username temporarily if needed later in PSS page
      localStorage.setItem("newUser", username);

      // 2️⃣ Redirect to PSS Questionnaire instead of logging in
      navigate("/pssquestionnaire");
    } catch (error) {
      console.error("Signup Error:", error);
      setErrorMessage("⚠️ Something went wrong. Please try again later.");
    }
  };

  return (
    <>
      <div className="navbar">
        <img src={logo} alt="Logo" className="logo" />
        <div>
          <a href="/">HOME</a>
          <a href="/about">ABOUT US</a>
          <a href="/resources">RESOURCES</a>
          <a href="/contact">CONTACT</a>
        </div>
      </div>

      <div className="signup-container">
        <div className="signup-box">
          <h2>Sign Up</h2>
          <img src={character} alt="Character" className="character" />

          <input
            type="text"
            placeholder="Enter your username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <div className="password-container">
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button
              onClick={() => setShowPassword(!showPassword)}
              type="button"
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          </div>

          {errorMessage && <p className="error-message">{errorMessage}</p>}

          <button onClick={handleSignup}>SIGN UP</button>

          <p>
            Already have an account? <a href="/login">Login</a>
          </p>
        </div>
      </div>
    </>
  );
};

export default Signup;
