import React, { useEffect, useState } from 'react';
import axios from 'axios';

function EntryList() {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    const fetchEntries = async () => {
      try {
        const token = localStorage.getItem("token"); // get JWT token
        if (!token) return;

        const res = await axios.get("http://127.0.0.1:8000/journal/entries", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        setEntries(res.data);
      } catch (err) {
        console.error("Failed to fetch entries:", err);
      }
    };

    fetchEntries();
  }, []);

  return (
    <div style={{ backgroundColor: '#ede7f6', minHeight: '100vh', padding: '40px 20px', fontFamily: 'Poppins, sans-serif', color: '#4a148c' }}>
      <div style={{ backgroundColor: '#fff', borderRadius: '20px', boxShadow: '0 6px 12px rgba(0,0,0,0.1)', padding: '32px', maxWidth: '700px', margin: '0 auto' }}>
        <h2 style={{ fontSize: '28px', fontWeight: '800', marginBottom: '24px', textAlign: 'center' }}>📄 Your Recent Entries</h2>
        {entries.length === 0 ? (
          <p style={{ textAlign: 'center' }}>No entries found.</p>
        ) : (
          entries.map((entry, index) => (
            <div key={index} style={{ marginBottom: '24px', padding: '16px', borderRadius: '12px', backgroundColor: '#f3e5f5', boxShadow: '0 2px 6px rgba(0,0,0,0.1)' }}>
              <p><strong>Date:</strong> {entry.entry_date}</p>
              <p><strong>Mood:</strong> {entry.mood}</p>
              <p><strong>Sentiment Score:</strong> {entry.sentiment.toFixed(2)}</p>
              <p><strong>Entry:</strong> {entry.entry_text}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default EntryList;
