import { useContext, useState } from "react";
import { UserContext } from "../context/UserContext";
import MentalSlider from "./MentalSlider";

export default function ProfileForm() {
  const { setUser } = useContext(UserContext);
  const [saved, setSaved] = useState(false);

  const [form, setForm] = useState({
    name: "",
    email: "",
    age: 25,
    height: 170,
    weight: 70,
    gender: "Male",
    stress_relief: 5,
    mood_boost: 5,
    anxiety_reduction: 5,
    sleep_improvement: 5,
    cognitive_function: 5,
    diet: "None",
    activity: 3,
  });

  function handleChange(e) {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  }

function saveProfile() {
  const activityLabels = [
    "Sedentary",
    "Light",
    "Moderate",
    "Active",
    "Very Active",
  ];

  setUser({
    ...form,
    bmi, // ✅ STORE BMI
    bmiLabel, // ✅ optional but useful
    activityLabel: activityLabels[form.activity - 1],
  });

  setSaved(true);

  setTimeout(() => setSaved(false), 3000);
}


  // ✅ BMI calculation (correct)
  const heightM = form.height / 100;
  const bmi =
    heightM > 0 ? (form.weight / (heightM * heightM)).toFixed(1) : 0;

  const bmiLabel =
    bmi < 18.5 ? "Underweight" :
    bmi < 25 ? "Normal" :
    bmi < 30 ? "Overweight" : "Obese";

  return (
    <div className="profile-wrapper">

      {/* HERO */}
      <div className="profile-hero">
        <h1>👤 Build Your Personal Profile</h1>
        <p>Help us understand you better to create the perfect meal plan</p>
      </div>

      {/* BASIC INFO */}
      <section className="card-section">
        <h2>📋 Basic Information</h2>

        <div className="two-col">
          <input
            name="name"
            placeholder="Full Name *"
            value={form.name}
            onChange={handleChange}
          />

          <input
            name="email"
            placeholder="Email (Optional)"
            value={form.email}
            onChange={handleChange}
          />

          <input
            name="age"
            type="number"
            value={form.age}
            onChange={handleChange}
          />

          <input
            name="height"
            type="number"
            placeholder="Height (cm)"
            value={form.height}
            onChange={handleChange}
          />

          <input
            name="weight"
            type="number"
            placeholder="Weight (kg)"
            value={form.weight}
            onChange={handleChange}
          />

          <select
            name="gender"
            value={form.gender}
            onChange={handleChange}
          >
            <option>Male</option>
            <option>Female</option>
            <option>Other</option>
          </select>
        </div>

        {/* ✅ BMI now dynamic */}
        <div className="info-box">
          📊 Your BMI: <strong>{bmi} ({bmiLabel})</strong>
        </div>
      </section>

      {/* MENTAL HEALTH */}
      <section className="card-section">
  <h2>🎯 Mental Health & Wellness Goals</h2>
  <p className="muted">
    Rate each area based on your current needs (1 = Low Priority, 10 = High Priority)
  </p>

  <div className="mental-grid">

    <MentalSlider
      icon="🧘"
      label="Stress Relief & Relaxation"
      name="stress_relief"
      value={form.stress_relief}
      onChange={handleChange}
    />

    <MentalSlider
      icon="😴"
      label="Sleep Quality"
      name="sleep_improvement"
      value={form.sleep_improvement}
      onChange={handleChange}
    />

    <MentalSlider
      icon="😊"
      label="Mood Enhancement"
      name="mood_boost"
      value={form.mood_boost}
      onChange={handleChange}
    />

    <MentalSlider
      icon="🧠"
      label="Focus & Mental Clarity"
      name="cognitive_function"
      value={form.cognitive_function}
      onChange={handleChange}
    />

    <MentalSlider
      icon="🌊"
      label="Anxiety Management"
      name="anxiety_reduction"
      value={form.anxiety_reduction}
      onChange={handleChange}
    />

  </div>
</section>


      {/* LIFESTYLE */}
      <section className="card-section">
        <h2>🏃 Lifestyle & Preferences</h2>

        <div className="two-col">
          <select
            className="diet-select"
            name="diet"
            value={form.diet}
            onChange={handleChange}
          >

            <option>None</option>
            <option>Vegetarian</option>
            <option>Vegan</option>
          </select>

          <div className="activity-slider">
  <label className="activity-label">
    Physical Activity Level
  </label>

  <div className="activity-scale">
    <span>Sedentary</span>
    <span>Light</span>
    <span>Moderate</span>
    <span>Active</span>
    <span>Very Active</span>
  </div>

  <div className="slider-wrapper">
    <div
      className="slider-value"
      style={{ left: `${(form.activity - 1) * 25}%` }}
    >
      {["Sedentary", "Light", "Moderate", "Active", "Very Active"][form.activity - 1]}
    </div>

    <input
      type="range"
      min="1"
      max="5"
      step="1"
      name="activity"
      value={form.activity}
      onChange={handleChange}
      style={{ "--val": form.activity * 2 }}
    />
  </div>
</div>

        </div>
      </section>
      {saved && (
  <div className="success-box">
    ✅ Profile saved successfully!
    <br />
    Go to the <strong>Recommendations</strong> tab to see your meal plan.
  </div>
)}

      {/* CTA */}
      <button className="cta-btn" onClick={saveProfile}>
        💾 Save Profile & Continue
      </button>

    </div>
  );
}
