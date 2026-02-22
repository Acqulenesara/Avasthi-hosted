import React, { useState } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import "../styles/Login.css";
import logo from "../assets/logo.png";
import character from "../assets/character.png";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");
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

    setLoading(true);
    setStatusMsg("Connecting to server...");

    const controller = new AbortController();
    // 30s timeout — if backend is cold it wakes up within ~20s
    const timeoutId = setTimeout(() => {
      controller.abort();
    }, 30000);

    // Show a "still waking up" hint after 5s
    const hintId = setTimeout(() => {
      setStatusMsg("Server is waking up, please wait...");
    }, 5000);

    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || "http://127.0.0.1:8000"}/token`,
        {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({ username, password }),
          signal: controller.signal,
        }
      );

      clearTimeout(timeoutId);
      clearTimeout(hintId);

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
        setStatusMsg("");
        alert(`❌ Login Failed: ${data.detail || "Incorrect username or password"}`);
      }
    } catch (error) {
      clearTimeout(timeoutId);
      clearTimeout(hintId);
      if (error.name === "AbortError") {
        alert("⏱️ Login timed out. The server may be starting up — please try again in a moment.");
      } else {
        alert("⚠️ Something went wrong. Check your connection and try again.");
      }
      console.error("Login Error:", error);
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

      <div className="login-container">
        <div className="login-box">
          <h2>Login</h2>
          <img src={character} alt="Character" className="character" />

          <input
            type="text"
            placeholder="Enter your username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={loading}
            onKeyPress={(e) => e.key === "Enter" && !loading && handleLogin()}
          />

          <div className="password-container">
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              onKeyPress={(e) => e.key === "Enter" && !loading && handleLogin()}
            />
            <button
              onClick={() => setShowPassword(!showPassword)}
              type="button"
              className="show-btn"
              disabled={loading}
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          </div>

          {statusMsg && (
            <p className="status-msg" style={{ color: "#888", fontSize: "0.85rem", margin: "6px 0" }}>
              {statusMsg}
            </p>
          )}

          <button
            onClick={handleLogin}
            className="login-btn"
            disabled={loading}
            style={{ opacity: loading ? 0.7 : 1, cursor: loading ? "not-allowed" : "pointer" }}
          >
            {loading ? "Logging in..." : "LOGIN"}
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
