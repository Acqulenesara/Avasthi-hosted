import React, { useState, useEffect, useRef } from "react";
import "./breathing.css";

const Breathing = () => {
  const [isActive, setIsActive] = useState(false);
  const [currentPhase, setCurrentPhase] = useState("inhale");
  const [sessionTime, setSessionTime] = useState(0);
  const [breathCount, setBreathCount] = useState(0);
  const [selectedDuration, setSelectedDuration] = useState(5);
  const [currentExercise, setCurrentExercise] = useState("breathing");

  const intervalRef = useRef(null);
  const phaseIntervalRef = useRef(null);

  const exercises = {
    breathing: {
      name: "4-7-8 Breathing",
      description: "Inhale for 4, hold for 7, exhale for 8",
      phases: [
        { name: "inhale", duration: 4000, text: "Breathe in slowly..." },
        { name: "hold", duration: 7000, text: "Hold your breath..." },
        { name: "exhale", duration: 8000, text: "Breathe out slowly..." },
        { name: "pause", duration: 1000, text: "Rest..." },
      ],
    },
    boxBreathing: {
      name: "Box Breathing",
      description: "Equal counts of inhale, hold, exhale, hold",
      phases: [
        { name: "inhale", duration: 4000, text: "Inhale..." },
        { name: "hold", duration: 4000, text: "Hold..." },
        { name: "exhale", duration: 4000, text: "Exhale..." },
        { name: "hold", duration: 4000, text: "Hold..." },
      ],
    },
    triangle: {
      name: "Triangle Breathing",
      description: "Inhale, exhale, pause in equal measures",
      phases: [
        { name: "inhale", duration: 4000, text: "Breathe in..." },
        { name: "exhale", duration: 4000, text: "Breathe out..." },
        { name: "pause", duration: 4000, text: "Rest and be present..." },
      ],
    },
  };

  const getCurrentPhase = () => {
    const exercise = exercises[currentExercise];
    return (
      exercise.phases.find((phase) => phase.name === currentPhase) ||
      exercise.phases[0]
    );
  };

  const startBreathingCycle = () => {
    const exercise = exercises[currentExercise];
    let phaseIndex = 0;

    const cyclePhases = () => {
      const phase = exercise.phases[phaseIndex];
      setCurrentPhase(phase.name);

      phaseIntervalRef.current = setTimeout(() => {
        phaseIndex = (phaseIndex + 1) % exercise.phases.length;
        if (phaseIndex === 0) {
          setBreathCount((prev) => prev + 1);
        }
        cyclePhases();
      }, phase.duration);
    };

    cyclePhases();
  };

  const startSession = () => {
    setIsActive(true);
    setSessionTime(0);
    setBreathCount(0);

    intervalRef.current = setInterval(() => {
      setSessionTime((prev) => prev + 1);
    }, 1000);

    startBreathingCycle();
  };

  const pauseSession = () => {
    setIsActive(false);
    if (intervalRef.current) clearInterval(intervalRef.current);
    if (phaseIntervalRef.current) clearTimeout(phaseIntervalRef.current);
  };

  const resetSession = () => {
    setIsActive(false);
    setSessionTime(0);
    setBreathCount(0);
    setCurrentPhase("inhale");
    if (intervalRef.current) clearInterval(intervalRef.current);
    if (phaseIntervalRef.current) clearTimeout(phaseIntervalRef.current);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (phaseIntervalRef.current) clearTimeout(phaseIntervalRef.current);
    };
  }, []);

  return (
    <div className="app-container">
      <h1 className="title">Mindful Meditation</h1>
      <p className="subtitle">Find peace in the present moment</p>

      {/* Exercise Selector */}
      <div className="exercise-selector">
        {Object.entries(exercises).map(([key, exercise]) => (
          <button
            key={key}
            onClick={() => {
              setCurrentExercise(key);
              resetSession();
            }}
            className={`exercise-btn ${
              currentExercise === key ? "active" : ""
            }`}
          >
            <h3>{exercise.name}</h3>
            <p>{exercise.description}</p>
          </button>
        ))}
      </div>

      {/* Meditation Circle */}
      <div className="circle-container">
        <div className={`circle ${currentPhase}`}></div>
        <div className="circle-text">
          <h2>{getCurrentPhase().text}</h2>
          <p>{exercises[currentExercise].name}</p>
        </div>
      </div>

      {/* Phase Label */}
      <div className="phase-label">
        <h3>{currentPhase === "pause" ? "Rest" : currentPhase}</h3>
        <p>Follow the circle's rhythm</p>
      </div>

      {/* Stats */}
      <div className="stats">
        <div className="stat">
          <div className="stat-value">{formatTime(sessionTime)}</div>
          <div className="stat-label">Session Time</div>
        </div>
        <div className="stat">
          <div className="stat-value">{breathCount}</div>
          <div className="stat-label">Breath Cycles</div>
        </div>
        <div className="stat">
          <div className="stat-value">{selectedDuration} min</div>
          <div className="stat-label">Target</div>
        </div>
        <div className="stat">
          <div className="stat-value">{currentPhase}</div>
          <div className="stat-label">Current Phase</div>
        </div>
      </div>

      {/* Controls */}
      <div className="controls">
        {isActive ? (
          <button className="control-btn pause" onClick={pauseSession}>
            Pause
          </button>
        ) : (
          <button className="control-btn start" onClick={startSession}>
            Start Session
          </button>
        )}
        <button className="control-btn reset" onClick={resetSession}>
          Reset
        </button>
      </div>

      {/* Duration Selector */}
      <div className="duration-selector">
        <h3>Session Duration</h3>
        <div className="duration-buttons">
          {[1, 3, 5, 10, 15, 20].map((duration) => (
            <button
              key={duration}
              onClick={() => setSelectedDuration(duration)}
              className={`duration-btn ${
                selectedDuration === duration ? "active" : ""
              }`}
            >
              {duration} min
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Breathing;
