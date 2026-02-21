import React, { useState } from 'react';
import axios from 'axios';

function JournalForm({ userId }) {
  const [entry, setEntry] = useState('');
  const [response, setResponse] = useState(null);

  const handleSubmit = async () => {
    if (!entry.trim()) return;

    try {
      const res = await axios.post(`${process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000'}/journal/submit`, {
  entry: entry
}, {
  headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
});
      setResponse(res.data);
      setEntry('');
    } catch (err) {
      console.error("Submission failed:", err);
    }
  };

  return (
    <div>
      <textarea
        placeholder="Write your thoughts here..."
        value={entry}
        onChange={e => setEntry(e.target.value)}
        style={{ width: '100%', height: '150px', padding: '12px', fontSize: '16px', borderRadius: '10px', border: '1px solid #ccc' }}
      />
      <button onClick={handleSubmit} style={{ marginTop: '16px', padding: '12px 24px', backgroundColor: '#6a1b9a', color: '#fff', border: 'none', borderRadius: '10px', fontSize: '16px', fontWeight: '600', cursor: 'pointer' }}>
        Submit
      </button>
      {response && (
        <div style={{ marginTop: '20px', fontSize: '16px' }}>
          <p>🧠 Detected Emotion: <strong>{response.mood}</strong></p>
          <p>📊 Confidence Score: {response.sentiment.toFixed(2)}</p>
        </div>
      )}
    </div>
  );
}

export default JournalForm;