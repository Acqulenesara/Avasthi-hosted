import React, { useState, useEffect } from "react";
// Import BrowserRouter and alias it as Router
import { Link } from "react-router-dom";

// --- Helper Functions ---

// Gets auth headers from localStorage
const getAuthHeaders = () => {
  const token = localStorage.getItem("token");
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
};

// Base API URL
const API_URL = "http://127.0.0.1:8000";

// --- Styles ---
// Using inline styles for simplicity, but you can move to App.css
const styles = {
  container: {
    padding: "2rem",
    maxWidth: "1000px",
    margin: "0 auto",
    fontFamily: "Arial, sans-serif",
    color: "#333",
  },
  header: {
    fontSize: "2.5rem",
    color: "#2c3e50",
    borderBottom: "2px solid #ecf0f1",
    paddingBottom: "1rem",
    marginBottom: "2rem",
  },
  section: {
    marginBottom: "2.5rem",
  },
  sectionTitle: {
    fontSize: "1.8rem",
    color: "#34495e",
    marginBottom: "1rem",
  },
  loading: {
    fontSize: "1.2rem",
    color: "#7f8c8d",
  },
  error: {
    color: "white",
    backgroundColor: "#e74c3c",
    padding: "1rem",
    borderRadius: "8px",
  },
  list: {
    display: "flex",
    flexDirection: "column",
    gap: "1rem",
  },
  profCard: {
    backgroundColor: "#ffffff",
    padding: "1.5rem",
    borderRadius: "8px",
    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.05)",
    border: "1px solid #ecf0f1",
  },
  profName: {
    fontSize: "1.4rem",
    color: "#2980b9",
    margin: "0 0 0.5rem 0",
  },
  profSpecialty: {
    fontSize: "1rem",
    color: "#7f8c8d",
    fontStyle: "italic",
    marginBottom: "0.5rem",
  },
  profBio: {
    fontSize: "1rem",
    lineHeight: "1.5",
    marginBottom: "1rem",
  },
  button: {
    backgroundColor: "#3498db",
    color: "white",
    border: "none",
    padding: "0.75rem 1.25rem",
    borderRadius: "5px",
    fontSize: "1rem",
    cursor: "pointer",
    transition: "background-color 0.3s ease",
  },
  buttonDisabled: {
    backgroundColor: "#bdc3c7",
    cursor: "not-allowed",
  },
  slotList: {
    marginTop: "1rem",
    display: "flex",
    flexWrap: "wrap",
    gap: "0.5rem",
  },
  slotButton: {
    backgroundColor: "#2ecc71",
    color: "white",
    border: "none",
    padding: "0.5rem 1rem",
    borderRadius: "5px",
    cursor: "pointer",
    fontSize: "0.9rem",
  },
  appointmentCard: {
    backgroundColor: "#f9f9f9",
    padding: "1rem",
    borderRadius: "8px",
    border: "1px solid #ddd",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  appointmentInfo: {
    fontSize: "1rem",
  },
  meetingLink: {
    color: "#2980b9",
    textDecoration: "none",
    fontWeight: "bold",
  },
  backLink: {
    display: "inline-block",
    margin: "2rem 0",
    color: "#3498db",
    textDecoration: "none",
    fontSize: "1rem",
  }
};

// --- Component ---

function OnlineConsultationPage() {
  const [professionals, setProfessionals] = useState([]);
  const [myAppointments, setMyAppointments] = useState([]);
  const [selectedProfId, setSelectedProfId] = useState(null);
  const [slots, setSlots] = useState([]);

  const [loadingProfs, setLoadingProfs] = useState(true);
  const [loadingAppts, setLoadingAppts] = useState(true);
  const [loadingSlots, setLoadingSlots] = useState(false);

  const [error, setError] = useState(null);

  // Fetch professionals and user's appointments on mount
  useEffect(() => {
    fetchProfessionals();
    fetchMyAppointments();
  }, []);

  // Fetch all professionals
  const fetchProfessionals = async () => {
    setLoadingProfs(true);
    try {
      const res = await fetch(`${API_URL}/consult/professionals`, {
        headers: getAuthHeaders(),
      });
      if (!res.ok) throw new Error("Failed to fetch professionals.");
      const data = await res.json();
      setProfessionals(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingProfs(false);
    }
  };

  // Fetch user's existing appointments
  const fetchMyAppointments = async () => {
    setLoadingAppts(true);
    try {
      const res = await fetch(`${API_URL}/consult/my-appointments`, {
        headers: getAuthHeaders(),
      });
      if (!res.ok) throw new Error("Failed to fetch appointments.");
      const data = await res.json();
      setMyAppointments(data);
    } catch (err)
 {
      setError(err.message);
    } finally {
      setLoadingAppts(false);
    }
  };

  // Fetch slots for a specific professional
  const handleShowSlots = async (profId) => {
    if (selectedProfId === profId) {
      // Toggle off
      setSelectedProfId(null);
      setSlots([]);
      return;
    }

    setSelectedProfId(profId);
    setLoadingSlots(true);
    try {
      const res = await fetch(`${API_URL}/consult/professionals/${profId}/slots`, {
        headers: getAuthHeaders(),
      });
      if (!res.ok) throw new Error("Failed to fetch slots.");
      const data = await res.json();
      setSlots(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingSlots(false);
    }
  };

  // Book a new appointment
  const handleBookSlot = async (slotId) => {
    setError(null);
    try {
      const res = await fetch(`${API_URL}/consult/book`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ slot_id: slotId }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Booking failed.");
      }

      // Booking successful
      alert("Booking successful!");

      // Refresh data
      fetchMyAppointments();

      // Reset slots view
      setSelectedProfId(null);
      setSlots([]);

    } catch (err) {
      setError(err.message);
    }
  };

  // Helper to format date
  const formatDateTime = (dateTimeString) => {
    return new Date(dateTimeString).toLocaleString("en-US", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  };

  return (


      <div style={styles.container}>
        <Link to="/" style={styles.backLink}>&larr; Back to Home</Link>
        <h1 style={styles.header}>Online Consultation</h1>

        {error && <p style={styles.error}>{error}</p>}

        {/* Section 1: My Appointments */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>My Upcoming Appointments</h2>
          {loadingAppts ? (
            <p style={styles.loading}>Loading appointments...</p>
          ) : myAppointments.length === 0 ? (
            <p>You have no upcoming appointments.</p>
          ) : (
            <div style={styles.list}>
              {myAppointments.map((appt) => (
                <div key={appt.id} style={styles.appointmentCard}>
                  <div style={styles.appointmentInfo}>
                    <strong>{appt.professional.full_name}</strong> ({appt.professional.specialty})
                    <br />
                    {formatDateTime(appt.slot.start_time)}
                  </div>
                  {appt.meeting_link ? (
                    <a href={appt.meeting_link} style={styles.meetingLink} target="_blank" rel="noopener noreferrer">
                      Join Meeting
                    </a>
                  ) : (
                    <span>Meeting link pending</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Section 2: Book a New Appointment */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>Book a New Appointment</h2>
          {loadingProfs ? (
            <p style={styles.loading}>Loading professionals...</p>
          ) : (
            <div style={styles.list}>
              {professionals.map((prof) => (
                <div key={prof.id} style={styles.profCard}>
                  <h3 style={styles.profName}>{prof.full_name}</h3>
                  <p style={styles.profSpecialty}>{prof.specialty}</p>
                  <p style={styles.profBio}>{prof.bio}</p>

                  <button
                    style={styles.button}
                    onClick={() => handleShowSlots(prof.id)}
                  >
                    {selectedProfId === prof.id ? "Hide Slots" : "Show Available Slots"}
                  </button>

                  {/* Show slots if this professional is selected */}
                  {selectedProfId === prof.id && (
                    <div style={styles.slotList}>
                      {loadingSlots ? (
                        <p style={styles.loading}>Loading slots...</p>
                      ) : slots.length === 0 ? (
                        <p>No available slots for this professional.</p>
                      ) : (
                        slots.map(slot => (
                          <button
                            key={slot.id}
                            style={styles.slotButton}
                            onClick={() => handleBookSlot(slot.id)}
                          >
                            Book {formatDateTime(slot.start_time)}
                          </button>
                        ))
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

  );
}

export default OnlineConsultationPage;