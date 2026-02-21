import React, { useState } from 'react';
import './App.css';
import {
    registerUser,
    loginUser,
    getRecommendations,
    sendFeedback,
    getHistory,
    sendChatMessage
} from './api';

// --- Components ---

const Auth = ({ onLoginSuccess }) => {
    const [isLogin, setIsLogin] = useState(true);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            let data;
            if (isLogin) {
                data = await loginUser(username, password);
            } else {
                data = await registerUser(username, password);
                alert('Registration successful! Please log in.');
                setIsLogin(true); // Switch to login view after registration
                return;
            }
            onLoginSuccess(data);
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="auth-container">
            <h2>{isLogin ? 'Login' : 'Register'}</h2>
            <form className="auth-form" onSubmit={handleSubmit}>
                {error && <p className="error-message">{error}</p>}
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <button type="submit">{isLogin ? 'Login' : 'Register'}</button>
            </form>
            <p className="auth-toggle" onClick={() => setIsLogin(!isLogin)}>
                {isLogin ? 'Need an account? Register' : 'Have an account? Login'}
            </p>
        </div>
    );
};

const Dashboard = ({ user, onLogout }) => {
    const [recommendations, setRecommendations] = useState([]);
    const [history, setHistory] = useState([]);
    const [messages, setMessages] = useState([]);
    const [chatInput, setChatInput] = useState('');
    const [view, setView] = useState('recs'); // 'recs' or 'history'

    const handleGetRecommendations = async () => {
        try {
            const data = await getRecommendations(user.username);
            setRecommendations(data.recommendations);
            setView('recs');
        } catch (error) {
            console.error("Failed to fetch recommendations", error);
        }
    };

    const handleGetHistory = async () => {
        try {
            const data = await getHistory(user.username);
            setHistory(data.history);
            setView('history');
        } catch (error) {
            console.error("Failed to fetch history", error);
        }
    };

    const handleFeedback = async (activityTitle, liked) => {
        try {
            await sendFeedback(user.username, activityTitle, liked);
            // Remove the item from the list after feedback is given
            setRecommendations(recs => recs.filter(r => r.activity !== activityTitle));
        } catch (error) {
            console.error("Failed to send feedback", error);
        }
    };

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!chatInput.trim()) return;

        const newUserMessage = { sender: 'user', text: chatInput };
        setMessages(msgs => [...msgs, newUserMessage]);

        try {
            const response = await sendChatMessage(chatInput);
            const newBotMessage = { sender: 'bot', text: response.response };
            setMessages(msgs => [...msgs, newUserMessage, newBotMessage]);
        } catch (error) {
            const errorMessage = { sender: 'bot', text: "Sorry, I couldn't get a response." };
            setMessages(msgs => [...msgs, newUserMessage, errorMessage]);
        }
        setChatInput('');
    };

    return (
        <div className="dashboard">
            <header className="header">
                <h2>Welcome, {user.username}!</h2>
                <div>
                    <button onClick={handleGetRecommendations}>Get Recommendations</button>
                    <button onClick={handleGetHistory} style={{ margin: '0 1rem' }}>View History</button>
                    <button onClick={onLogout}>Logout</button>
                </div>
            </header>

            <div className="panel chat-panel">
                <h3>Chat with Assistant</h3>
                <div className="chat-window">
                    <div className="chat-messages">
                        {messages.map((msg, index) => (
                            <div key={index} className={`chat-message ${msg.sender === 'user' ? 'user-message' : 'bot-message'}`}>
                                {msg.text}
                            </div>
                        ))}
                    </div>
                    <form className="chat-input" onSubmit={handleSendMessage}>
                        <input
                            type="text"
                            placeholder="Type your message..."
                            value={chatInput}
                            onChange={(e) => setChatInput(e.target.value)}
                        />
                        <button type="submit">Send</button>
                    </form>
                </div>
            </div>

            <div className="panel recommendations-panel">
                <h3>{view === 'recs' ? 'Your Recommendations' : 'Recommendation History'}</h3>
                {view === 'recs' ? (
                    <ul className="rec-list">
                        {recommendations.map((rec, index) => (
                            <li key={index} className="rec-item">
                                <h4>{rec.activity}</h4>
                                <p><strong>Rationale:</strong> {rec.rationale}</p>
                                <p><em>Score: {rec.score}</em></p>
                                <div className="feedback-buttons">
                                    <button onClick={() => handleFeedback(rec.activity, true)}>👍 Like</button>
                                    <button onClick={() => handleFeedback(rec.activity, false)}>👎 Dislike</button>
                                </div>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <ul className="rec-list">
                        {history.map((histItem, index) => (
                            <li key={index} className="rec-item">
                                <span className="history-timestamp">{new Date(histItem.timestamp).toLocaleString()}</span>
                                {histItem.recommendations.map((rec, recIndex) => (
                                    <div key={recIndex}><p>- {rec.activity}</p></div>
                                ))}
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
};


// --- Main App Component ---

function App() {
    const [user, setUser] = useState(null);

    const handleLoginSuccess = (userData) => {
        setUser(userData);
    };

    const handleLogout = () => {
        setUser(null);
    };

    return (
        <div className="container">
            {!user ? (
                <Auth onLoginSuccess={handleLoginSuccess} />
            ) : (
                <Dashboard user={user} onLogout={handleLogout} />
            )}
        </div>
    );
}

export default App;