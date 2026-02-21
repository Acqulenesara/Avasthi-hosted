// Chatbot.js - Full Updated Code

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from "react-router-dom";
import './Chatbot.css';
import logo from "../assets/logo.png";
import heroImage from "../assets/image.png";

// --- Speech Recognition & Synthesis Setup ---
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.continuous = false;
recognition.interimResults = false;
const synth = window.speechSynthesis;

const greetings = {
    'ml-IN': "നമസ്കാരം! നിങ്ങൾക്ക് ഇന്ന് എങ്ങനെയുണ്ട്?",
    'en-US': "Hi, I'm Aarohi! How are you feeling today?",
    'hi-IN': "नमस्ते ! आज आप कैसा महसूस कर रहे हैं?",
};

function ChatbotPage() {
  // --- KEY CHANGE: Added state for language ---
  const [language, setLanguage] = useState('en-US');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const navigate = useNavigate();
  const chatEndRef = useRef(null);

  useEffect(() => {
    // Set initial greeting based on the default language
    const initialBotMessage = { sender: 'bot', text: greetings[language] };
    setMessages([initialBotMessage]);
    setTimeout(() => speak(initialBotMessage.text, language), 500);

    // Setup speech recognition listeners
    recognition.onresult = (event) => {
      const voiceText = event.results[0][0].transcript;
      setInput(voiceText);
      sendMessage(voiceText);
    };
    recognition.onend = () => setIsListening(false);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // This effect runs only once

  useEffect(() => {
    // Auto-scroll to the latest message
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // --- KEY CHANGE: speak() now accepts a language code ---
 const speak = (text, lang) => {
  // Stop any currently speaking utterance
  if (synth.speaking) synth.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  const voices = window.speechSynthesis.getVoices();

  // Set the language for the utterance (important for pronunciation)
  utterance.lang = lang;

  let selectedVoice = null;

  // --- KEY CHANGE ---
  // If the language is English, specifically look for the preferred "Emma" voice first.
  if (lang === 'en-US') {
    selectedVoice = voices.find(
      voice => voice.name === "Microsoft Emma Online (Natural) - English (United States)"
    );
  }

  // If the preferred voice wasn't found, OR if the language isn't English,
  // fall back to finding the first available voice for the selected language.
  if (!selectedVoice) {
    selectedVoice = voices.find(v => v.lang === lang) || voices.find(v => v.lang.startsWith(lang.split('-')[0]));
  }

  // Assign the determined voice to the utterance
  utterance.voice = selectedVoice;

  synth.speak(utterance);
};

  // --- KEY CHANGE: sendMessage() is now completely updated for streaming ---
  const sendMessage = async (text) => {
    const messageText = (text || input).trim();
    if (!messageText) return;

    setMessages(prev => [...prev, { sender: 'user', text: messageText }]);
    setInput('');
    setLoading(true);

    // AbortController gives a 60-second timeout before showing error
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000);

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000'}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({ query: messageText, language: language }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.status === 401) {
        localStorage.removeItem("token");
        navigate("/login");
        return;
      }

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error ${response.status}`);
      }

      const data = await response.json();
      const botText = data.response || "I'm sorry, I didn't get a response.";

      setMessages(prev => [...prev, { sender: 'bot', text: botText }]);
      speak(botText, language);

    } catch (error) {
      clearTimeout(timeoutId);
      console.error('Error sending message:', error);
      const isTimeout = error.name === 'AbortError';
      const errorMsg = isTimeout
        ? "It's taking longer than expected. Please try again in a moment."
        : `Something went wrong: ${error.message}`;
      setMessages(prev => [...prev, { sender: 'bot', text: errorMsg }]);
    } finally {
      setLoading(false);
    }
  };

  // --- KEY CHANGE: handleMicClick() now sets the language for recognition ---
  const handleMicClick = () => {
    if (isListening) {
      recognition.stop();
    } else {
      recognition.lang = language; // Set language before listening
      synth.cancel(); // Stop bot from talking
      recognition.start();
    }
    setIsListening(!isListening);
  };

  const handleLanguageChange = (e) => {
    const newLang = e.target.value;
    setLanguage(newLang);
    const newGreeting = { sender: 'bot', text: greetings[newLang] };
    setMessages(prev => [...prev, newGreeting]);
    speak(newGreeting.text, newLang);
  };

  return (
    <div className="app">
      {/* Navbar and Hero sections remain the same */}
      <nav className="navbar">
        <div className="logo-container">
          <img src={logo} alt="Aarohi AI Logo" className="logo-img" />
          <div className="logo-text">Aarohi AI</div>
        </div>
        <div className="nav-links">
          <a href="#home">HOME</a>
          <a href="#about">ABOUT US</a>
          <a href="#resources">RESOURCES</a>
          <a href="#contact">CONTACT</a>
        </div>
      </nav>

      <section className="hero">
        <div className="hero-content">
          <div className="hero-text">
            <h1>Welcome to Aarohi AI</h1>
            <p className="intro-text">
              Hi, I'm Aarohi, your AI psychologist. Here to listen, guide, and support you.
              Available 24/7, everything you share stays private and secure.
            </p>
            <p className="lets-talk">Let’s talk and unwind together!</p>
          </div>
          <div className="hero-image">
            <img src={heroImage} alt="Chatbot Illustration" />
          </div>
        </div>
      </section>

      <section className="chat-section">
        <div className="chat-history">
          {messages.map((msg, index) => (
            <div key={index} className={`chat-bubble ${msg.sender}`}>{msg.text}</div>
          ))}
          {loading && (
            <div className="chat-bubble bot">
              <span style={{opacity: 0.6}}>Aarohi is thinking...</span>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
        
        {/* --- KEY CHANGE: Added Language Selector UI --- */}
        <div className="language-selector">
          <label htmlFor="lang-select">Language: </label>
          <select id="lang-select" value={language} onChange={handleLanguageChange}>
            <option value="en-US">English</option>
            <option value="ml-IN">മലയാളം (Malayalam)</option>
            <option value="hi-IN">हिन्दी (Hindi)</option>
          </select>
        </div>

        <div className="chat-input">
          <input
            type="text"
            placeholder="Type your thoughts here..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            disabled={loading}
          />
          <button className="mic-btn" onClick={handleMicClick} disabled={loading}>
            {isListening ? "🎤" : "🎙️"}
          </button>
          <button className="send-btn" onClick={() => sendMessage()} disabled={!input.trim() || loading}>
            Send
          </button>
        </div>
      </section>
    </div>
  );
}

export default ChatbotPage;

