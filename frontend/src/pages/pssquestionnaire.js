import React, { useState } from "react";
import "./pss.css";

// PSS questions (with reverse scoring notes)
const questions = [
  { text: "In the last month, how often have you been upset because of something that happened unexpectedly?", reverse: false },
  { text: "In the last month, how often have you felt that you were unable to control the important things in your life?", reverse: false },
  { text: "In the last month, how often have you felt nervous and stressed?", reverse: false },
  { text: "In the last month, how often have you felt confident about your ability to handle your personal problems?", reverse: true },
  { text: "In the last month, how often have you felt that things were going your way?", reverse: true },
  { text: "In the last month, how often have you found that you could not cope with all the things that you had to do?", reverse: false },
  { text: "In the last month, how often have you been able to control irritations in your life?", reverse: true },
  { text: "In the last month, how often have you felt that you were on top of things?", reverse: true },
  { text: "In the last month, how often have you been angered because of things that happened that were outside of your control?", reverse: false },
  { text: "In the last month, how often have you felt difficulties were piling up so high that you could not overcome them?", reverse: false }
];

// Answer options
const options = [
  { value: 0, label: "Never" },
  { value: 1, label: "Almost Never" },
  { value: 2, label: "Sometimes" },
  { value: 3, label: "Fairly Often" },
  { value: 4, label: "Very Often" }
];

const PSSQuestionnaire = () => {
  const [responses, setResponses] = useState({});
  const [score, setScore] = useState(null);

  // Handle answer change
  const handleChange = (qIndex, value) => {
    setResponses((prev) => ({
      ...prev,
      [qIndex]: parseInt(value)
    }));
  };

  // Handle submit
  const handleSubmit = (e) => {
    e.preventDefault();

    if (Object.keys(responses).length < questions.length) {
      alert("Please answer all questions!");
      return;
    }

    let total = 0;

    questions.forEach((q, index) => {
      let val = responses[index];
      // Reverse scoring for Q4, Q5, Q7, Q8
      if (q.reverse) {
        val = 4 - val;
      }
      total += val;
    });

    setScore(total);
  };

  // Interpret the result
  const getResultText = () => {
    if (score <= 13) return "Low Stress";
    if (score <= 26) return "Moderate Stress";
    return "High Stress";
  };

  return (
    <div className="container">
      <section className="resources">
        <h2>Perceived Stress Scale (PSS)</h2>
        <p className="hero-text">
          This questionnaire asks about your feelings and thoughts during the last month.
          Answer quickly — choose the option that best reflects how often you felt that way.
        </p>

        <form className="questionnaire" onSubmit={handleSubmit}>
          {questions.map((q, index) => (
            <div className="question-card" key={index}>
              <p>{index + 1}. {q.text}</p>
              <div className="options">
                {options.map((opt) => (
                  <label key={opt.value}>
                    <input
                      type="radio"
                      name={`q${index}`}
                      value={opt.value}
                      onChange={(e) => handleChange(index, e.target.value)}
                      required
                    />
                    {/* The text is now wrapped in a span for individual styling */}
                    <span>{opt.label}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}

          <div style={{ textAlign: "center", marginTop: "20px" }}>
            <button type="submit" className="button">Submit</button>
          </div>
        </form>

        {score !== null && (
          <div className="result-card">
            <h3>Your Score: {score}</h3>
            <p>{getResultText()}</p>
            <small>
              (0–13 = Low Stress, 14–26 = Moderate Stress, 27–40 = High Stress)
            </small>
          </div>
        )}
      </section>
    </div>
  );
};

export default PSSQuestionnaire;