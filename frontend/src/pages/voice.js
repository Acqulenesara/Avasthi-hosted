import React, { useState, useEffect } from "react";
import axios from "axios";

const App = () => {
    const [query, setQuery] = useState("");
    const [response, setResponse] = useState("");
    const [isListening, setIsListening] = useState(false);
    const [loading, setLoading] = useState(false);
    const [voices, setVoices] = useState([]);

    useEffect(() => {
        const synth = window.speechSynthesis;

        // Ensure voices are loaded before using them
        const loadVoices = () => {
            const availableVoices = synth.getVoices();
            setVoices(availableVoices);
        };

        if (synth.onvoiceschanged !== undefined) {
            synth.onvoiceschanged = loadVoices;
        } else {
            setTimeout(loadVoices, 1000); // Fallback if voices don’t load
        }

        return () => synth.cancel(); // Stop speech synthesis on unmount
    }, []);

    // Speech Recognition (Voice Input)
    const startListening = () => {
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = "en-US";
        recognition.start();

        recognition.onstart = () => setIsListening(true);
        recognition.onend = () => setIsListening(false);

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            setQuery(transcript);
            sendQuery(transcript);
        };
    };

    // Send query to FastAPI backend
    const sendQuery = async (text) => {
        if (!text.trim()) return; // Prevent empty queries

        setLoading(true);
        try {
            const res = await axios.post(`${process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000'}/query`, { query: text });
            setResponse(res.data.response);
            speakResponse(res.data.response);
        } catch (error) {
            console.error("Error:", error);
            const errorMessage = "Oops! Something went wrong.";
            setResponse(errorMessage);
            speakResponse(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    // Text-to-Speech (Voice Output)
    const speakResponse = (text) => {
        if (!text.trim()) return; // Prevent speaking empty responses

        const synth = window.speechSynthesis;
        synth.cancel(); // Stop previous speech before speaking a new response

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "en-US";

        // Use the first available voice or default
        utterance.voice = voices.length > 0 ? voices[0] : null;

        console.log("Using voice:", utterance.voice?.name || "Default voice");
        synth.speak(utterance);
    };

    return (
        <div style={{ textAlign: "center", padding: "20px", fontFamily: "Arial, sans-serif" }}>
            <h1>🎙️ Voice-Enabled AI Chatbot</h1>

            <button onClick={startListening}
                style={{ margin: "10px", padding: "12px 20px", fontSize: "16px", cursor: "pointer" }}>
                {isListening ? "🎤 Listening..." : "🎙️ Speak"}
            </button>

            <p><strong>Query:</strong> {query}</p>

            <button onClick={() => sendQuery(query)}
                style={{ margin: "10px", padding: "10px 15px", fontSize: "16px", cursor: "pointer" }}
                disabled={!query.trim()}>
                ➡ Send
            </button>

            <p><strong>Response:</strong> {loading ? "⏳ Bot is thinking..." : response}</p>
        </div>
    );
};

export default App;
