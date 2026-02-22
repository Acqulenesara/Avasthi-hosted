import React, { useState } from 'react';
import axios from 'axios';

function JournalForm({ userId }) {
  const [entry, setEntry] = useState('');
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!entry.trim()) return;

    setError(null);
    setSubmitting(true);

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("You are not logged in. Please log in and try again.");
        setSubmitting(false);
        return;
      }

      const res = await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000'}/journal/submit`,
        { entry: entry },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setResponse(res.data);
      setEntry('');
    } catch (err) {
      console.error("Submission failed:", err);
      if (err.response?.status === 401) {
        setError("Session expired. Please log in again.");
      } else if (err.response?.data?.detail) {
        setError(`Error: ${err.response.data.detail}`);
      } else if (err.message === 'Network Error') {
        setError("Cannot reach the server. Please check your connection or try again later.");
      } else {
        setError("Failed to submit entry. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <textarea
        placeholder="Write your thoughts here..."
        value={entry}
        onChange={e => setEntry(e.target.value)}
        style={{ width: '100%', height: '150px', padding: '12px', fontSize: '16px', borderRadius: '10px', border: '1px solid #ccc', boxSizing: 'border-box' }}
      />
      <button
        onClick={handleSubmit}
        disabled={submitting}
        style={{ marginTop: '16px', padding: '12px 24px', backgroundColor: submitting ? '#aaa' : '#6a1b9a', color: '#fff', border: 'none', borderRadius: '10px', fontSize: '16px', fontWeight: '600', cursor: submitting ? 'not-allowed' : 'pointer' }}
      >
        {submitting ? '⏳ Submitting...' : 'Submit'}
      </button>

      {error && (
        <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#fdecea', borderRadius: '8px', color: '#c62828', fontSize: '15px' }}>
          ❌ {error}
        </div>
      )}

      {response && (
        <div style={{ marginTop: '20px', padding: '16px', backgroundColor: '#f3e5f5', borderRadius: '10px', fontSize: '16px' }}>
          <p>✅ Entry saved!</p>
          <p>🧠 Detected Emotion: <strong>{response.mood}</strong></p>
          <p>📊 Confidence Score: {typeof response.sentiment === 'number' ? response.sentiment.toFixed(2) : response.sentiment}</p>
        </div>
      )}
    </div>
  );
}

export default JournalForm;