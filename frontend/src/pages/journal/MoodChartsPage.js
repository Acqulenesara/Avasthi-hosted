import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

function MoodChartsPage({ userId }) {
  const [moodCounts, setMoodCounts] = useState({});

  useEffect(() => {
    const fetchEntries = async () => {
      try {
        const res = await axios.get(`http://127.0.0.1:8000/journal/entries`, {
  headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
});

        const moods = res.data.map(entry => entry.mood);
        const counts = moods.reduce((acc, mood) => {
          acc[mood] = (acc[mood] || 0) + 1;
          return acc;
        }, {});
        setMoodCounts(counts);
      } catch (err) {
        console.error("Failed to fetch mood data:", err);
      }
    };

    fetchEntries();
  }, [userId]);

  const data = {
    labels: Object.keys(moodCounts),
    datasets: [
      {
        data: Object.values(moodCounts),
        backgroundColor: ['#66bb6a', '#ffa726', '#ef5350'],
        borderColor: '#fff',
        borderWidth: 2
      }
    ]
  };

  return (
    <div style={{ backgroundColor: '#ede7f6', minHeight: '100vh', padding: '40px 20px', fontFamily: 'Poppins, sans-serif', color: '#4a148c' }}>
      <div style={{ backgroundColor: '#fff', borderRadius: '20px', boxShadow: '0 6px 12px rgba(0,0,0,0.1)', padding: '32px', maxWidth: '700px', margin: '0 auto' }}>
        <h2 style={{ fontSize: '28px', fontWeight: '800', marginBottom: '24px', textAlign: 'center' }}>📊 Your Mood Chart</h2>
        {Object.keys(moodCounts).length === 0 ? (
          <p style={{ textAlign: 'center' }}>No mood data available.</p>
        ) : (
          <Pie data={data} />
        )}
      </div>
    </div>
  );
}

export default MoodChartsPage;