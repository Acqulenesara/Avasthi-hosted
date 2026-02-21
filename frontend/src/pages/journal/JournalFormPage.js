import React from 'react';
import { useNavigate } from 'react-router-dom';
import JournalForm from './JournalForm';

function JournalFormPage() {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Clear both token and userId if present
    localStorage.removeItem('access_token');
    localStorage.removeItem('userId');
    navigate('/');
  };

  return (
    <div
      style={{
        backgroundColor: '#ede7f6',
        minHeight: '100vh',
        padding: '40px 20px',
        fontFamily: 'Poppins, sans-serif',
        color: '#4a148c',
      }}
    >
      <div
        style={{
          backgroundColor: '#fff',
          borderRadius: '20px',
          boxShadow: '0 6px 12px rgba(0,0,0,0.1)',
          padding: '32px',
          maxWidth: '700px',
          margin: '0 auto',
        }}
      >
        <h2
          style={{
            fontSize: '28px',
            fontWeight: '800',
            marginBottom: '24px',
            textAlign: 'center',
          }}
        >
          ✍️ Write Your Journal Entry
        </h2>

        {/* ✅ Journal form */}
        <JournalForm />

        {/* ✅ Navigation buttons */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '24px',
            marginTop: '32px',
          }}
        >
          <button
            style={{
              padding: '14px 28px',
              backgroundColor: '#6a1b9a',
              color: '#fff',
              border: 'none',
              borderRadius: '12px',
              fontSize: '18px',
              fontWeight: '700',
              cursor: 'pointer',
            }}
            onClick={() => navigate('/journal/entries')}
          >
            📄 View Recent Entries
          </button>

          <button
            style={{
              padding: '14px 28px',
              backgroundColor: '#6a1b9a',
              color: '#fff',
              border: 'none',
              borderRadius: '12px',
              fontSize: '18px',
              fontWeight: '700',
              cursor: 'pointer',
            }}
            onClick={() => navigate('/journal/charts')}
          >
            📊 View Mood Charts
          </button>
        </div>

        {/* ✅ Logout */}
        <div style={{ textAlign: 'center', marginTop: '32px' }}>
          <button
            onClick={handleLogout}
            style={{
              padding: '12px 24px',
              backgroundColor: '#d32f2f',
              color: '#fff',
              border: 'none',
              borderRadius: '10px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
            }}
          >
            🔓 Logout
          </button>
        </div>
      </div>
    </div>
  );
}

export default JournalFormPage;
