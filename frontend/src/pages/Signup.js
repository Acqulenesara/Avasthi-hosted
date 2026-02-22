import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Signup.css";
import logo from "../assets/logo.png";
import character from "../assets/character.png";

const Signup = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");
  const navigate = useNavigate();

  const handleSignup = async () => {
    if (!username || !password) {
      setErrorMessage("⚠️ Please fill in all fields!");
      return;
    }

    setLoading(true);
    setErrorMessage("");
    setStatusMsg("Connecting to server...");

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);
    const hintId = setTimeout(() => setStatusMsg("Server is waking up, please wait..."), 5000);

    try {
      const registerResponse = await fetch(
        `${process.env.REACT_APP_API_URL || "http://127.0.0.1:8000"}/register`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password }),
          signal: controller.signal,
        }
      );

      clearTimeout(timeoutId);
      clearTimeout(hintId);

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
      clearTimeout(timeoutId);
      clearTimeout(hintId);
      if (error.name === "AbortError") {
        setErrorMessage("⏱️ Request timed out. The server may be starting up — please try again.");
      } else {
        setErrorMessage("⚠️ Something went wrong. Please try again later.");
      }
      console.error("Signup Error:", error);
    } finally {
      setLoading(false);
      setStatusMsg("");
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
            disabled={loading}
            onKeyPress={(e) => e.key === "Enter" && !loading && handleSignup()}
          />

          <div className="password-container">
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              onKeyPress={(e) => e.key === "Enter" && !loading && handleSignup()}
            />
            <button
              onClick={() => setShowPassword(!showPassword)}
              type="button"
              disabled={loading}
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          </div>

          {statusMsg && (
            <p style={{ color: "#888", fontSize: "0.85rem", margin: "6px 0" }}>{statusMsg}</p>
          )}
          {errorMessage && <p className="error-message">{errorMessage}</p>}

          <button
            onClick={handleSignup}
            disabled={loading}
            style={{ opacity: loading ? 0.7 : 1, cursor: loading ? "not-allowed" : "pointer" }}
          >
            {loading ? "Signing up..." : "SIGN UP"}
          </button>

          <p>
            Already have an account? <a href="/login">Login</a>
          </p>
        </div>
      </div>
    </>
  );
};

export default Signup;
