import React, { useState } from "react";
import "./cbt.css"; // Import your CSS for styling

const CBT = () => {
  const [currentScenario, setCurrentScenario] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [responses, setResponses] = useState([]);
  const [currentResponse, setCurrentResponse] = useState("");
  const [completedScenarios, setCompletedScenarios] = useState([]);
  const [showReflection, setShowReflection] = useState(false);

  const scenarios = {
    exam_anxiety: {
      title: "Exam Anxiety",
      description: "Feeling overwhelmed and anxious before important exams",
      icon: "🧠",
      color: "blue",
      steps: [
        {
          therapist: "What thoughts go through your mind before an exam?",
          prompt: "Describe your anxious thoughts...",
        },
        {
          therapist: "Challenge these thoughts. Are they based on facts?",
          prompt: "Analyze your thoughts...",
        },
        {
          therapist: "Plan actions to feel more prepared.",
          prompt: "Write your action plan...",
        },
        {
          therapist: "What coping strategies can help you?",
          prompt: "List coping strategies...",
        },
      ],
    },
    social_anxiety: {
      title: "Social Anxiety",
      description: "Fear of social situations and being judged by others",
      icon: "💬",
      color: "green",
      steps: [
        {
          therapist: "Which social situations make you anxious?",
          prompt: "Describe your thoughts...",
        },
        {
          therapist:
            "Challenge these thoughts. How likely is the worst-case scenario?",
          prompt: "Write your analysis...",
        },
        {
          therapist: "Plan small social steps to build confidence.",
          prompt: "Write your action plan...",
        },
        {
          therapist: "What strategies help you manage social anxiety?",
          prompt: "List coping strategies...",
        },
      ],
    },
    perfectionism: {
      title: "Perfectionism",
      description: "Struggling with unrealistic standards and fear of failure",
      icon: "🎯",
      color: "purple",
      steps: [
        {
          therapist: "Describe a situation where perfectionism stressed you.",
          prompt: "Your example...",
        },
        {
          therapist: "Are your standards realistic? What is 'good enough'?",
          prompt: "Write your reflection...",
        },
        {
          therapist: "Plan small experiments to practice imperfection.",
          prompt: "Write your action plan...",
        },
        {
          therapist:
            "What strategies help you handle perfectionist thoughts?",
          prompt: "List coping strategies...",
        },
      ],
    },
    low_mood: {
      title: "Low Mood & Motivation",
      description:
        "Feeling down, unmotivated, or experiencing depressive thoughts",
      icon: "❤",
      color: "red",
      steps: [
        {
          therapist: "What thoughts occur when feeling low?",
          prompt: "Describe your thoughts...",
        },
        {
          therapist:
            "Challenge negative thoughts. Evidence for or against them?",
          prompt: "Analyze your thoughts...",
        },
        {
          therapist: "Plan small activities to improve mood.",
          prompt: "Write your action plan...",
        },
        {
          therapist: "Which coping strategies help lift your mood?",
          prompt: "List coping strategies...",
        },
      ],
    },
  };

  const startScenario = (key) => {
    setCurrentScenario(key);
    setCurrentStep(0);
    setResponses([]);
    setCurrentResponse("");
    setShowReflection(false);
  };

  const nextStep = () => {
    if (currentResponse.trim()) {
      setResponses([...responses, currentResponse]);
      setCurrentResponse("");
      if (currentStep < scenarios[currentScenario].steps.length - 1) {
        setCurrentStep(currentStep + 1);
      } else {
        completeScenario();
      }
    }
  };

  const completeScenario = () => {
    if (!completedScenarios.includes(currentScenario)) {
      setCompletedScenarios([...completedScenarios, currentScenario]);
    }
    setShowReflection(true);
  };

  const resetScenario = () => {
    setCurrentScenario(null);
    setCurrentStep(0);
    setResponses([]);
    setCurrentResponse("");
    setShowReflection(false);
  };

  if (!currentScenario) {
    return (
      <div className="container">
        <h1>🧠 CBT Therapist Simulation</h1>
        <p>
          Practice cognitive behavioral therapy techniques through guided
          scenarios.
        </p>
        <div className="scenario-grid">
          {Object.entries(scenarios).map(([key, scenario]) => (
            <div
              key={key}
              className="scenario-card"
              onClick={() => startScenario(key)}
            >
              <div className={`scenario-icon ${scenario.color}`}>
                {scenario.icon}
              </div>
              <h3>{scenario.title}</h3>
              <p>{scenario.description}</p>
              {completedScenarios.includes(key) && (
                <span className="completed">✔ Completed</span>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (showReflection) {
    return (
      <div className="session-container">
        <div className="session-box">
          <h2>Session Complete!</h2>
          <p>Insights from your session:</p>
          <p>
            <strong>Thoughts:</strong> {responses[0]}
          </p>
          <p>
            <strong>Challenged Thoughts:</strong> {responses[1]}
          </p>
          <p>
            <strong>Action Plan:</strong> {responses[2]}
          </p>
          <p>
            <strong>Coping Strategies:</strong> {responses[3]}
          </p>
          <button onClick={resetScenario} className="btn-secondary">
            Back to Scenarios
          </button>
        </div>
      </div>
    );
  }

  const stepData = scenarios[currentScenario].steps[currentStep];

  return (
    <div className="session-container">
      <div className="session-box">
        <h2>{scenarios[currentScenario].title} Session</h2>
        <span>
          Step {currentStep + 1} / {scenarios[currentScenario].steps.length}
        </span>
        <p>{stepData.therapist}</p>
        <textarea
          value={currentResponse}
          onChange={(e) => setCurrentResponse(e.target.value)}
          placeholder={stepData.prompt}
          className="response-box"
        />
        <div className="actions">
          <button onClick={resetScenario} className="btn-secondary">
            Back
          </button>
          <button
            onClick={nextStep}
            disabled={!currentResponse.trim()}
            className="btn-primary"
          >
            {currentStep ===
            scenarios[currentScenario].steps.length - 1
              ? "Complete"
              : "Next"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CBT;
