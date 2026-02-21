import React, { useState } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import "../styles/Login.css";
import Signup from "./Signup";
import logo from "../assets/logo.png";
import character from "../assets/character.png";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // Get where user came from (e.g., /login?from=chatbot)
  const queryParams = new URLSearchParams(location.search);
  const from = queryParams.get("from"); // chatbot | recommendation

  const handleLogin = async () => {
    if (!username || !password) {
      alert("⚠️ Please fill in all fields!");
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000'}/token`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username, password }),
      });

      const data = await response.json();
      console.log("API Response:", data);

      if (response.ok) {
        alert("✅ Login Successful!");
        localStorage.setItem("token", data.access_token);

        // Redirect based on where the user came from
        if (from === "chatbot") {
          navigate("/chatbot");
        } else if (from === "recommendation") {
          navigate("/recom-dashboard");
        } else {
          navigate("/"); // fallback to home page
        }
      } else {
        alert(`❌ Login Failed: ${data.detail || "Unknown error"}`);
      }
    } catch (error) {
      console.error("Login Error:", error);
      alert("⚠️ Something went wrong. Try again later.");
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

      <div className="login-container">
        <div className="login-box">
          <h2>Login</h2>
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
              className="show-btn"
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          </div>

          <button onClick={handleLogin} className="login-btn">
            LOGIN
          </button>

          <p>
            Don't have an account? <Link to="/signup">Sign up</Link>
          </p>
        </div>
      </div>
    </>
  );
};

export default Login;
