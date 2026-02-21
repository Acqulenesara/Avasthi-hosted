import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  useNavigate
} from "react-router-dom";
import "./App.css";
import ChatbotPage from "./pages/Chatbot";
import Recom from "./pages/recom";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import PSSQuestionnaire from "./pages/pssquestionnaire";
import { jwtDecode } from "jwt-decode";
import CBT from "./pages/cbt";
import Breathing from "./pages/breathing";
import EmotionMusicPlayer from "./pages/EmotionMusicPlayer";
import JournalFormPage from "./pages/journal/JournalFormPage";
import MoodChartsPage from "./pages/journal/MoodChartsPage";
import EntryList from "./pages/journal/EntryList";
import ResourceLibrary from "./pages/ResourceLibrary";
import ExerciseCam from "./pages/ExerciseCam";
import Diet from "./pages/Diet";
//import OnlineConsultationPage from "./pages/OnlineConsultationPage";


// ProtectedRoute wrapper
function ProtectedRoute({ children }) {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!token) {
      navigate("/login"); // No token → redirect
      return;
    }

    try {
      const decoded = jwtDecode(token);
      const now = Date.now() / 1000; // current time in seconds

      if (decoded.exp && decoded.exp < now) {
        // Token expired
        localStorage.removeItem("token");
        navigate("/login");
      }
    } catch (err) {
      console.error("Invalid token:", err);
      localStorage.removeItem("token");
      navigate("/login");
    }
  }, [navigate]);

  return children;
}




function HomePage() {
  return (
    <div className="page">
      {/* Navbar */}
      <nav className="nav">
        <h1 className="logo">AVASTHI</h1>
        <ul className="nav-links">
          <li>HOME</li>
          <li>ABOUT US</li>
          <li><Link to="/resources">RESOURCES</Link></li>
          <li>CONTACT</li>
        </ul>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-text">
          <p><span>Aspire</span> to</p>
          <p><span>Vibrance</span>, embrace</p>
          <p><span>Adaptability</span> with strength</p>
          <p><span>Support</span> balance,</p>
          <p><span>Tranquility</span>, compassion</p>
          <p><span>Heal</span> through hope and instill</p>
          <p><span>Independence</span></p>
        </div>

        <div className="hero-img">
          <img src="/meditation.png" alt="Meditation" />
        </div>
      </section>

      {/* Feature Buttons */}
      <section className="button-row">
        <div className="feature-card">
          <img src="/chat.png" alt="Chat" />
          <h3>
            <Link className="link-no-underline" to="/chatbot">
              Chat with Me!
            </Link>
          </h3>
          <p>Instantly connect for emotional support and guidance.</p>
        </div>

        <div className="feature-card">
          <img src="/tips.png" alt="Tips" />
          <h3>
            <Link className="link-no-underline" to="/recom">
              Get Tips
            </Link>
          </h3>
          <p>Receive personalized mental health tips and practices.</p>
        </div>



        <div className="feature-card">
          <img src="/diet.png" alt="Healthy Diet" />
          <h3>
            <Link className="link-no-underline" to="/diet">
              Healthy Diet
            </Link>
          </h3>
          <p>Explore diet plans that boost mental and physical wellness.</p>
        </div>

        <div className="feature-card">
          <img src="/exercise.png" alt="ExerciseCam" /> {/* Using placeholder */}
          <h3>
            <Link className="link-no-underline" to="/ExerciseCam">
              Fitness Coach
            </Link>
          </h3>
          <p>Train smarter with real-time AI-powered exercise and posture feedback.</p>
        </div>



      </section>

      {/* Explore Resources */}
      <section className="resources">
        <h2>Explore Resources</h2>
        <div className="resource-grid">
        <div className="resource-card">
          <img src="/cbt.png" alt="CBT" />
          <h3>
            <Link className="link-no-underline" to="/cbt">
              CBT
            </Link>
          </h3>
          <p>Practice cognitive behavioral therapy techniques.</p>
        </div>
        <div className="resource-card">
          <img src="/meditation1.png" alt="Guided Meditation" />
          <h3>
            <Link className="link-no-underline" to="/breathing">
              Guided Breathing
            </Link>
          </h3>
          <p>Relax your mind with calming breathing exercises.</p>
        </div>
        <div className="resource-card">
          <img src="/music.png" alt="Music Therapy" />
          <h3>
            <Link className="link-no-underline" to="/EmotionMusicPlayer">
              Music Therapy
            </Link>
          </h3>
          <p>Heal with soothing and uplifting music therapy.</p>
        </div>
        <div className="resource-card">
          <img src="/journal.png" alt="Journal" />
          <h3>
            <Link className="link-no-underline" to="/journal">
              Journal
            </Link>
          </h3>
          <p>Express thoughts and track your emotional progress.</p>
        </div>
        </div>

      </section>
    </div>
  );
}

function App() {
  const [, setToken] = useState(localStorage.getItem("token") || "");

  // Ping backend on app load to wake up Render free tier
  useEffect(() => {
    const apiUrl = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';
    fetch(`${apiUrl}/`, { method: 'GET' })
      .catch(() => {}); // silently ignore errors - just waking up the server
  }, []);

  // Keep token in sync with localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    if (storedToken) {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';
      fetch(`${apiUrl}/verify-token`, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${storedToken}` },
      }).then(res => {
        if (res.status === 401) {
          localStorage.removeItem("token");
        }
      }).catch(() => localStorage.removeItem("token"));
    }
  }, []);


  return (
    <Router>
      <Routes>
        {/* Login route */}
        <Route path="/login" element={<Login setToken={setToken} />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/pssquestionnaire" element={<PSSQuestionnaire />} />

        {/* Protected routes */}
        <Route
          path="/chatbot"
          element={
            <ProtectedRoute>
              <ChatbotPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/recom"
          element={
            <ProtectedRoute>
              <Recom />
            </ProtectedRoute>
          }
        />
        <Route
          path="/diet"
          element={

              <Diet />

          }
        />
        {/* --- THIS IS THE ROUTE FOR THE NEW PAGE --- */}
        <Route
            path="/ExerciseCam"
            element={<ExerciseCam />}
        />



        <Route path="/cbt" element={<CBT />} />
        <Route path="/breathing" element={<Breathing />} />
        <Route path="/EmotionMusicPlayer" element={<EmotionMusicPlayer />} />
        <Route path="/resources" element={<ResourceLibrary />} />

        <Route
  path="/journal"
  element={
    <ProtectedRoute>
      <JournalFormPage />
    </ProtectedRoute>
  }
/>

<Route
  path="/journal/entries"
  element={
    <ProtectedRoute>
      <EntryList />
    </ProtectedRoute>
  }
/>

<Route
  path="/journal/charts"
  element={
    <ProtectedRoute>
      <MoodChartsPage />
    </ProtectedRoute>
  }
/>




        {/* Public route */}
        <Route path="/" element={<HomePage />} />
      </Routes>
    </Router>
  );
}

export default App;
