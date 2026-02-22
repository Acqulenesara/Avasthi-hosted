import React, { useState, useEffect, useRef } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import "../styles/Login.css";
import logo from "../assets/logo.png";
import character from "../assets/character.png";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";
const MAX_RETRIES = 3;

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");
  const [serverReady, setServerReady] = useState(false);  // tracks if server responded to ping
  const [serverError, setServerError] = useState("");
  const pingDone = useRef(false);
  const navigate = useNavigate();
  const location = useLocation();

  const queryParams = new URLSearchParams(location.search);
  const from = queryParams.get("from");

  // ── Wake-up ping on mount ────────────────────────────────────────
  useEffect(() => {
    if (pingDone.current) return;
    pingDone.current = true;

    const wakeServer = async () => {
      setStatusMsg("🔄 Connecting to server...");
      for (let attempt = 1; attempt <= 5; attempt++) {
        try {
          const res = await fetch(`${API_URL}/`, { method: "GET" });
          if (res.ok) {
            setServerReady(true);
            setStatusMsg("✅ Server ready!");
            // Clear the message after 2s so it doesn't distract
            setTimeout(() => setStatusMsg(""), 2000);
            return;
          }
        } catch (_) {
          // server still cold — keep trying
        }
        if (attempt < 5) {
          setStatusMsg(`⏳ Server is warming up... (${attempt}/5)`);
          await new Promise((r) => setTimeout(r, 5000)); // wait 5s between pings
        }
      }
      // After 5 attempts (~25s) still no response — warn but don't block login
      setServerReady(true); // allow the user to try anyway
      setStatusMsg("⚠️ Server slow to respond — login may take a moment.");
      setTimeout(() => setStatusMsg(""), 4000);
    };

    wakeServer();
  }, []);

  // ── Core login with auto-retry ───────────────────────────────────
  const attemptLogin = async (attempt = 1) => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    try {
      const response = await fetch(`${API_URL}/token`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username, password }),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return response;
    } catch (err) {
      clearTimeout(timeoutId);
      if (attempt < MAX_RETRIES) {
        const isTimeout = err.name === "AbortError";
        setStatusMsg(
          isTimeout
            ? `⏳ Server waking up... retrying (${attempt}/${MAX_RETRIES})`
            : `🔄 Retrying... (${attempt}/${MAX_RETRIES})`
        );
        await new Promise((r) => setTimeout(r, 5000));
        return attemptLogin(attempt + 1);
      }
      throw err; // exhausted retries
    }
  };

  const handleLogin = async () => {
    if (!username || !password) {
      setServerError("⚠️ Please fill in all fields!");
      return;
    }
    setServerError("");
    setLoading(true);
    setStatusMsg("Logging in...");

    try {
      const response = await attemptLogin();
      const data = await response.json();

      if (response.ok) {
        setStatusMsg("✅ Login successful! Redirecting...");
        localStorage.setItem("token", data.access_token);
        setTimeout(() => {
          if (from === "chatbot") navigate("/chatbot");
          else if (from === "recommendation") navigate("/recom-dashboard");
          else navigate("/");
        }, 400);
      } else {
        setStatusMsg("");
        setServerError(`❌ ${data.detail || "Incorrect username or password"}`);
      }
    } catch (error) {
      if (error.name === "AbortError") {
        setServerError("⏱️ Login timed out after 3 attempts. Please try again in a moment.");
      } else {
        setServerError("⚠️ Network error. Check your connection and try again.");
      }
      console.error("Login Error:", error);
    } finally {
      setLoading(false);
      if (!serverReady) setStatusMsg("");
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
            onChange={(e) => { setUsername(e.target.value); setServerError(""); }}
            disabled={loading}
            onKeyPress={(e) => e.key === "Enter" && !loading && handleLogin()}
          />

          <div className="password-container">
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Enter your password"
              value={password}
              onChange={(e) => { setPassword(e.target.value); setServerError(""); }}
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

          {/* Server warm-up / progress status */}
          {statusMsg && (
            <p className="status-msg" style={{ color: "#888", fontSize: "0.85rem", margin: "6px 0" }}>
              {statusMsg}
            </p>
          )}

          {/* Inline error message (replaces alert popups) */}
          {serverError && (
            <p style={{ color: "#e74c3c", fontSize: "0.85rem", margin: "6px 0", fontWeight: 500 }}>
              {serverError}
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
