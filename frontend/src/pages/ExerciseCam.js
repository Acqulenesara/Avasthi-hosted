import React, { useRef, useEffect, useState, useCallback } from "react";
import * as poseDetection from "@mediapipe/pose";
import * as cam from "@mediapipe/camera_utils";

const ExerciseCam = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const lastCorrectionRef = useRef("");

  const [exercise, setExercise] = useState("arm_raise");
  const [instruction, setInstruction] = useState("Stand straight to begin...");
  const [correction, setCorrection] = useState("");
  const [timer, setTimer] = useState(0);
  const [holding, setHolding] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(false);

  const [resting, setResting] = useState(false);
  const [breakTimer, setBreakTimer] = useState(0);
  const [poseCorrect, setPoseCorrect] = useState(false);
  const [mlPrediction, setMlPrediction] = useState("");
  const [mlConfidence, setMlConfidence] = useState(0);
  const [repCount, setRepCount] = useState(0);
  // eslint-disable-next-line no-unused-vars
  const [postureScore, setPostureScore] = useState(100);
  const ML_EXERCISES = [
  "squats",
  "push_ups",
  "pull_ups",
  "russian_twists",
  "jumping_jacks",
];

const ML_EXERCISE_CONFIG = {
  squats: {
    instruction: "Lower into a squat and hold",
    corrections: (angles) => {
      const { knee, hip } = angles;

      if (knee > 130) return "⚠️ Bend your knees more";
      if (hip > 120) return "⚠️ Lower your hips";
      return "";
    },
  },

  push_ups: {
    instruction: "Lower your chest and keep elbows bent",
    corrections: (angles) => {
      const { elbow, shoulder } = angles;

      if (elbow > 150) return "⚠️ Bend your elbows more";
      if (shoulder < 60) return "⚠️ Keep shoulders stable";
      return "";
    },
  },

  pull_ups: {
    instruction: "Pull your body upward using your arms",
    corrections: (angles) => {
      const { elbow } = angles;

      if (elbow > 120) return "⚠️ Pull higher – bend elbows more";
      return "";
    },
  },

  russian_twists: {
    instruction: "Twist your torso side to side",
    corrections: (angles) => {
      const { hipGround } = angles;

      if (hipGround < 20) return "⚠️ Rotate your torso more";
      return "";
    },
  },

  jumping_jacks: {
    instruction: "Jump with arms and legs wide",
    corrections: (angles) => {
      const { shoulderGround, hipGround } = angles;

      if (shoulderGround < 30) return "⚠️ Raise arms wider";
      if (hipGround < 25) return "⚠️ Spread your legs wider";
      return "";
    },
  },
};



  const holdDuration = exercise === "Squats" ? 5 : 10;
  const breakDuration = 5;

  const holdIntervalRef = useRef(null);
  const breakIntervalRef = useRef(null);
  const lastPredictionTime = useRef(0);
  const repLocked = useRef(false);


  // Enable voice after first click
  useEffect(() => {
    const enableVoice = () => setVoiceEnabled(true);
    window.addEventListener("click", enableVoice);
    return () => window.removeEventListener("click", enableVoice);
  }, []);

  const speak = useCallback((text) => {
    if (!voiceEnabled) return;
    const synth = window.speechSynthesis;
    if (!synth) return;
    synth.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.pitch = 1;
    utter.rate = 1;
    utter.volume = 1;
    synth.speak(utter);
  }, [voiceEnabled]);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (instruction) speak(instruction);
  }, [instruction, speak]);

  // Setup MediaPipe Pose
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    const pose = new poseDetection.Pose({
      locateFile: (file) =>
        `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`,
    });
    pose.setOptions({
      modelComplexity: 1,
      smoothLandmarks: true,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5,
    });
    pose.onResults(onResults);

    let cameraInstance = null;

    if (typeof cam.Camera !== "undefined" && videoRef.current) {
      cameraInstance = new cam.Camera(videoRef.current, {
        onFrame: async () => {
          try {
            if (videoRef.current) await pose.send({ image: videoRef.current });
          } catch (e) {
            console.warn("pose.send error:", e);
          }
        },
        width: 640,
        height: 480,
      });
      cameraInstance.start();
    }

    return () => {
      try {
        if (cameraInstance && typeof cameraInstance.stop === "function") cameraInstance.stop();
      } catch (e) {
        console.warn("Error stopping camera:", e);
      }
      try {
        if (pose && typeof pose.close === "function") pose.close();
      } catch (e) {
        console.warn("Error closing pose:", e);
      }
    };
  }, [exercise]);

  const onResults = (results) => {
    // Guard against missing canvas or image (can happen if component unmounted)
    const canvas = canvasRef.current;
    if (!canvas || !results || !results.image) return;

    // Guard against missing pose landmarks
    if (!results.poseLandmarks || !Array.isArray(results.poseLandmarks) || results.poseLandmarks.length === 0) return;

    const ctx = canvas.getContext ? canvas.getContext("2d") : null;
    if (!ctx) return;

    try {
      ctx.save();
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height);

      drawSkeleton(ctx, results.poseLandmarks);
      checkExercisePose(results.poseLandmarks);

      // Send to ML model every 500ms
      const now = Date.now();
      if (now - lastPredictionTime.current > 500) {
        lastPredictionTime.current = now;

        if (ML_EXERCISES.includes(exercise)) {
          sendToMLModel(results.poseLandmarks);
        } else {
          setMlPrediction("");
          setMlConfidence(0);
        }
      }

      ctx.restore();
    } catch (err) {
      // In case something unexpected happens while drawing, don't crash the app
      console.warn("onResults draw error:", err);
    }
  };

  const drawSkeleton = (ctx, landmarks) => {
    if (!landmarks || !landmarks.length) return;

    const connections = [
      [11, 13], [13, 15],
      [12, 14], [14, 16],
      [11, 12],
      [11, 23], [12, 24],
      [23, 24],
      [23, 25], [25, 27],
      [24, 26], [26, 28],
    ];

    ctx.strokeStyle = poseCorrect ? "#00ff00" : "#ff0000";
    ctx.lineWidth = 3;

    connections.forEach(([start, end]) => {
      const startPoint = landmarks[start];
      const endPoint = landmarks[end];
      if (!startPoint || !endPoint) return;
      ctx.beginPath();
      ctx.moveTo(startPoint.x * 640, startPoint.y * 480);
      ctx.lineTo(endPoint.x * 640, endPoint.y * 480);
      ctx.stroke();
    });

    ctx.fillStyle = poseCorrect ? "#00ff00" : "#ff0000";
    landmarks.forEach((lm) => {
      if (!lm) return;
      ctx.beginPath();
      ctx.arc(lm.x * 640, lm.y * 480, 5, 0, 2 * Math.PI);
      ctx.fill();
    });
  };

  const getAngle = (a, b, c) => {
    const ab = [a.x - b.x, a.y - b.y];
    const cb = [c.x - b.x, c.y - b.y];
    const dot = ab[0] * cb[0] + ab[1] * cb[1];
    const magAB = Math.sqrt(ab[0] ** 2 + ab[1] ** 2);
    const magCB = Math.sqrt(cb[0] ** 2 + cb[1] ** 2);
    const angle = Math.acos(dot / (magAB * magCB));
    return (angle * 180) / Math.PI;
  };

  const getGroundAngle = (a, b) => {
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    return Math.abs(Math.atan2(dy, dx) * (180 / Math.PI));
  };


const extractAngles = (lm) => {
  const leftShoulder = lm[11], leftElbow = lm[13], leftWrist = lm[15];
  const leftHip = lm[23], leftKnee = lm[25], leftAnkle = lm[27];

  return {
    shoulder: getAngle(leftElbow, leftShoulder, leftHip),
    elbow: getAngle(leftWrist, leftElbow, leftShoulder),
    hip: getAngle(leftShoulder, leftHip, leftKnee),
    knee: getAngle(leftHip, leftKnee, leftAnkle),
    shoulderGround: getGroundAngle(leftShoulder, lm[12]),
    hipGround: getGroundAngle(leftHip, lm[24]),
  };
};

  // Send angles to ML model
  const sendToMLModel = async (lm) => {
    try {
      // Calculate all 10 angles as per your training data
      const leftShoulder = lm[11], leftElbow = lm[13], leftWrist = lm[15];
      // eslint-disable-next-line no-unused-vars
      const rightShoulder = lm[12], rightElbow = lm[14], rightWrist = lm[16];
      const leftHip = lm[23], leftKnee = lm[25], leftAnkle = lm[27];
      // eslint-disable-next-line no-unused-vars
      const rightHip = lm[24], rightKnee = lm[26], rightAnkle = lm[28];

      const angles = [
        getAngle(leftElbow, leftShoulder, leftHip), // Shoulder_Angle
        getAngle(leftWrist, leftElbow, leftShoulder), // Elbow_Angle
        getAngle(leftShoulder, leftHip, leftKnee), // Hip_Angle
        getAngle(leftHip, leftKnee, leftAnkle), // Knee_Angle
        getAngle(leftKnee, leftAnkle, { x: leftAnkle.x, y: leftAnkle.y + 0.1 }), // Ankle_Angle
        getGroundAngle(leftShoulder, rightShoulder), // Shoulder_Ground_Angle
        getGroundAngle(leftElbow, leftWrist), // Elbow_Ground_Angle
        getGroundAngle(leftHip, rightHip), // Hip_Ground_Angle
        getGroundAngle(leftKnee, leftAnkle), // Knee_Ground_Angle
        getGroundAngle(leftAnkle, { x: leftAnkle.x + 0.1, y: leftAnkle.y }), // Ankle_Ground_Angle
      ];

      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000'}/exercise/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ angles }),
      });

      const data = await response.json();

        console.log("ML RESPONSE:", data);

      setMlPrediction(data.predicted_exercise);
      
      const prediction = data.predicted_exercise?.toLowerCase() || "";

      setMlPrediction(prediction);
      setMlConfidence(prediction === exercise ? 100 : 0);


    } catch (error) {
      console.error("ML prediction error:", error);
    }
  };

const handleMLExerciseFeedback = (lm) => {
  const config = ML_EXERCISE_CONFIG[exercise];
  if (!config) return;

  const angles = extractAngles(lm);
  const correctionText = config.corrections(angles);

  setInstruction(config.instruction);
  setCorrection(correctionText);

  const correct = correctionText === "";
  setPoseCorrect(correct);

  // ✅ THIS WAS MISSING
  if (correct && !holding) {
    setHolding(true);
  }

  // Reset if form breaks
  if (!correct && holding) {
    setHolding(false);
    setTimer(0);
  }
};


  // Save posture data to backend
  const savePostureData = async () => {
    try {
      await fetch(`${process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000'}/exercise/posture`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "user_" + Date.now(),
          exercise: exercise,
          posture_score: postureScore,
          reps: repCount,
        }),
      });
    } catch (error) {
      console.error("Save posture error:", error);
    }
  };

  const checkExercisePose = (lm) => {

    if (resting) return;
    if (ML_EXERCISES.includes(exercise)) {
    handleMLExerciseFeedback(lm);
    return;
  }

    if (exercise === "arm_raise") checkArmRaise(lm);
    else if (exercise === "wall_push") checkWallPush(lm);
    else if (exercise === "Squats") checkSquats(lm);
    else if (exercise === "neck_rolls") checkNeckRolls(lm);
    else if (exercise === "shoulder_shrugs") checkShoulderShrugs(lm);
  };


  const checkArmRaise = (lm) => {
    const leftWrist = lm[15], leftElbow = lm[13], leftShoulder = lm[11], leftHip = lm[23];
    const rightWrist = lm[16], rightElbow = lm[14], rightShoulder = lm[12];
    
    const leftShoulderAngle = getAngle(leftElbow, leftShoulder, leftHip);
    const leftElbowAngle = getAngle(leftWrist, leftElbow, leftShoulder);
    const leftWristAboveShoulder = leftWrist.y < leftShoulder.y;
    const leftArmCorrect = leftShoulderAngle > 140 && leftElbowAngle > 160 && leftWristAboveShoulder;
    
    const rightShoulderAngle = getAngle(rightElbow, rightShoulder, leftHip);
    const rightElbowAngle = getAngle(rightWrist, rightElbow, rightShoulder);
    const rightWristAboveShoulder = rightWrist.y < rightShoulder.y;
    const rightArmCorrect = rightShoulderAngle > 140 && rightElbowAngle > 160 && rightWristAboveShoulder;
    // Unlock rep when both arms are lowered
    if (leftWrist.y > leftShoulder.y && rightWrist.y > rightShoulder.y) {
    repLocked.current = false;
    }

    const isCorrect = leftArmCorrect && rightArmCorrect;

    if (isCorrect) {
      setPoseCorrect(true);
      setCorrection("");
      if (!holding) {
        setInstruction("Perfect! Hold both arms up...");
        setHolding(true);
      }
    } else {
      setPoseCorrect(false);
      if (holding) {
        setHolding(false);
        setTimer(0);
      }
      setInstruction("Raise BOTH arms straight up");
      
      if (!leftWristAboveShoulder && !rightWristAboveShoulder) {
        setCorrection("⚠️ Raise both arms higher!");
      } else if (!leftWristAboveShoulder) {
        setCorrection("⚠️ Left arm: Raise higher!");
      } else if (!rightWristAboveShoulder) {
        setCorrection("⚠️ Right arm: Raise higher!");
      } else if (leftElbowAngle < 160 && rightElbowAngle < 160) {
        setCorrection("⚠️ Straighten both elbows!");
      } else if (leftElbowAngle < 160) {
        setCorrection("⚠️ Left arm: Straighten elbow!");
      } else if (rightElbowAngle < 160) {
        setCorrection("⚠️ Right arm: Straighten elbow!");
      }
    }
  };

  const checkWallPush = (lm) => {
    const leftWrist = lm[15], leftElbow = lm[13], leftShoulder = lm[11];
    const rightWrist = lm[16], rightElbow = lm[14], rightShoulder = lm[12];
    
    const leftElbowAngle = getAngle(leftWrist, leftElbow, leftShoulder);
    const rightElbowAngle = getAngle(rightWrist, rightElbow, rightShoulder);
    
    const elbowsBent = leftElbowAngle < 140 && rightElbowAngle < 140;
    
    const armsLevel = Math.abs(leftWrist.y - rightWrist.y) < 0.1;
    
    const isCorrect = elbowsBent && armsLevel && (leftElbowAngle > 60 && rightElbowAngle > 60);

    if (isCorrect) {
      setPoseCorrect(true);
      setCorrection("");
      if (!holding) {
        setInstruction("Perfect wall push position! Hold it...");
        setHolding(true);
      }
    } else {
      setPoseCorrect(false);
      if (holding) {
        setHolding(false);
        setTimer(0);
      }
      setInstruction("Bend elbows as if pushing against a wall");
      
      if (!elbowsBent) {
        setCorrection("⚠️ Bend your elbows more!");
      } else if (!armsLevel) {
        setCorrection("⚠️ Keep both arms at same height!");
      } else {
        setCorrection("⚠️ Position arms as if pushing a wall!");
      }
    }
  };

  const checkNeckRolls = (lm) => {
    const nose = lm[0], leftEar = lm[7], rightEar = lm[8];
    const leftShoulder = lm[11], rightShoulder = lm[12];
    
    // Calculate neck tilt (nose position relative to shoulders)
    const shoulderMidY = (leftShoulder.y + rightShoulder.y) / 2;
    const neckTilt = Math.abs(nose.y - shoulderMidY);
    
    // Check if head is tilted significantly
    const headTiltAngle = Math.abs(leftEar.y - rightEar.y);
    
    // For neck rolls, we want to see movement/tilt
    const isCorrect = neckTilt > 0.05 || headTiltAngle > 0.02;

    if (isCorrect) {
      setPoseCorrect(true);
      setCorrection("");
      if (!holding) {
        setInstruction("Great! Keep rolling your neck gently...");
        setHolding(true);
      }
    } else {
      setPoseCorrect(false);
      if (holding) {
        setHolding(false);
        setTimer(0);
      }
      setInstruction("Gently roll your head in circles");
      setCorrection("⚠️ Move your head more - tilt left, back, right, forward");
    }
  };

  const checkShoulderShrugs = (lm) => {
    const leftShoulder = lm[11], rightShoulder = lm[12];
    const leftEar = lm[7], rightEar = lm[8];
    
    // Calculate distance between shoulders and ears
    const leftDistance = Math.abs(leftShoulder.y - leftEar.y);
    const rightDistance = Math.abs(rightShoulder.y - rightEar.y);
    
    // Shoulders should be raised (closer to ears)
    const isCorrect = leftDistance < 0.15 && rightDistance < 0.15;

    if (isCorrect) {
      setPoseCorrect(true);
      setCorrection("");
      if (!holding) {
        setInstruction("Perfect shrug! Hold your shoulders up...");
        setHolding(true);
      }
    } else {
      setPoseCorrect(false);
      if (holding) {
        setHolding(false);
        setTimer(0);
      }
      setInstruction("Lift BOTH shoulders up towards your ears");
      setCorrection("⚠️ Raise your shoulders higher!");
    }
  };

  const checkSquats = (lm) => {

    const leftHip = lm[23], leftKnee = lm[25], leftAnkle = lm[27], leftShoulder = lm[11];
    const rightHip = lm[24], rightKnee = lm[26], rightAnkle = lm[28];

    const leftKneeAngle = getAngle(leftHip, leftKnee, leftAnkle);
    const rightKneeAngle = getAngle(rightHip, rightKnee, rightAnkle);
    const hipAngle = getAngle(leftShoulder, leftHip, leftKnee);

    const isCorrect = leftKneeAngle < 110 && rightKneeAngle < 110 && hipAngle < 100;
    // Detect standing position → unlock next rep
const standing =
  leftKneeAngle > 160 &&
  rightKneeAngle > 160 &&
  hipAngle > 160;

if (standing) {
  repLocked.current = false;
}


    if (isCorrect) {
      setPoseCorrect(true);
      setCorrection("");
      if (!holding) {
        setInstruction("Great Squat! Hold it there...");
        setHolding(true);
      }
    } else {
      setPoseCorrect(false);
      if (holding) {
        setHolding(false);
        setTimer(0);
      }
      setInstruction("Bend BOTH knees and lower into Squat");

      if (leftKneeAngle >= 110 && rightKneeAngle >= 110) {
        setCorrection("⚠️ Bend both knees more!");
      } else if (leftKneeAngle >= 110) {
        setCorrection("⚠️ Left knee: Bend more!");
      } else if (rightKneeAngle >= 110) {
        setCorrection("⚠️ Right knee: Bend more!");
      }
    }
  };

  useEffect(() => {
    if (holdIntervalRef.current) {
      clearInterval(holdIntervalRef.current);
    }
    
    if (holding && !resting && poseCorrect) {
      holdIntervalRef.current = setInterval(() => {
        setTimer((t) => {
          const next = t + 0.1;
          if (next >= holdDuration) {
            clearInterval(holdIntervalRef.current);
            setHolding(false);
            setTimer(holdDuration);
            
            // Set/Speak Rest Message Immediately
            setCorrection(""); 
            setPoseCorrect(false);

            const restMessage = "relax! take rest";
            setInstruction(restMessage); 
            speak(restMessage); 

            setResting(true);
            setBreakTimer(0);
            
            if (!repLocked.current) {
            setRepCount(prev => prev + 1);
            repLocked.current = true;
            savePostureData();
            }

            
            return holdDuration;
          }
          return next;
        });
      }, 100);
    } else if (!holding) {
      setTimer(0);
    }
    
    return () => {
      if (holdIntervalRef.current) {
        clearInterval(holdIntervalRef.current);
      }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [holding, resting, poseCorrect, exercise]);

  useEffect(() => {
    if (breakIntervalRef.current) {
      clearInterval(breakIntervalRef.current);
    }
    
    if (resting) {
      breakIntervalRef.current = setInterval(() => {
        setBreakTimer((t) => {
          const next = t + 1;
          if (next >= breakDuration) {
            clearInterval(breakIntervalRef.current);
            setResting(false);
            setBreakTimer(breakDuration);
            setTimer(0);
            setHolding(false);
            setCorrection("");
            
            // Set/Speak Next Instruction ONLY After Rest is Over
            if (exercise === "arm_raise") {
              setInstruction("Ready? Raise BOTH arms straight up");
            } else if (exercise === "wall_push") {
              setInstruction("Ready? Bend elbows like pushing a wall");
            } else if (exercise === "Squats") {
              setInstruction("Ready? Lower into Squat position");
            } else if (exercise === "neck_rolls") {
              setInstruction("Ready? Roll your head gently in circles");
            } else if (exercise === "shoulder_shrugs") {
              setInstruction("Ready? Lift your shoulders up");
            } 
            
            return breakDuration;
          }
          return next;
        });
      }, 1000);
    } else {
      setBreakTimer(0);
    }
    
    return () => {
      if (breakIntervalRef.current) {
        clearInterval(breakIntervalRef.current);
      }
    };
  }, [resting, exercise]);

  const handleExerciseChange = (newExercise) => {
    if (holdIntervalRef.current) {
      clearInterval(holdIntervalRef.current);
    }
    if (breakIntervalRef.current) {
      clearInterval(breakIntervalRef.current);
    }

    setExercise(newExercise);
    setInstruction("Get ready...");
    setTimer(0);
    setHolding(false);
    setResting(false);
    setBreakTimer(0);
    setPoseCorrect(false);
    setCorrection("");
    setRepCount(0);
    
    setTimeout(() => {
      if (newExercise === "arm_raise") {
        setInstruction("Raise BOTH arms straight up");
      } else if (newExercise === "wall_push") {
        setInstruction("Bend elbows as if pushing a wall");
      } else if (newExercise === "Squats") {
        setInstruction("Lower into Squat position");
      } else if (newExercise === "neck_rolls") {
        setInstruction("Gently roll your head in circles");
      } else if (newExercise === "shoulder_shrugs") {
        setInstruction("Lift your shoulders up towards ears");
      } 
    }, 500);
  };

const isMLActive = ML_EXERCISES.includes(exercise);

useEffect(() => {
  if (correction && correction !== lastCorrectionRef.current) {
    speak(correction);
    lastCorrectionRef.current = correction;
  }
// eslint-disable-next-line react-hooks/exhaustive-deps
}, [correction]);

  return (
    <div style={{ textAlign: "center", marginTop: 20, fontFamily: "Arial, sans-serif", color: "#222", backgroundColor: "#f5f5f5", padding: "20px", minHeight: "100vh" }}>
      <h1 style={{ color: "#2563eb" }}>🏋️ AI Fitness Coach (ML-Powered)</h1>
      {!voiceEnabled && <p style={{ color: "gray", fontSize: "0.9em" }}>🔊 Click anywhere to enable voice feedback</p>}
      
      <select
  value={exercise}
  onChange={(e) => handleExerciseChange(e.target.value)}
>
  <option value="arm_raise">🙌 Both Arms Raise</option>
  <option value="wall_push">💪 Wall Push</option>

  <option value="squats">🦵 Squats</option>
  <option value="push_ups">💪 Push-ups</option>
  <option value="pull_ups">🏋️ Pull-ups</option>
  <option value="russian_twists">🔄 Russian Twists</option>
  <option value="jumping_jacks">🤸 Jumping Jacks</option>

  <option value="neck_rolls">🔄 Neck Rolls</option>
  <option value="shoulder_shrugs">💆 Shoulder Shrugs</option>
</select>

      <div style={{ display: "flex", gap: "10px", justifyContent: "center", marginBottom: "15px" }}>
        <div style={{ backgroundColor: "#e0e7ff", padding: "10px 20px", borderRadius: "8px", border: "2px solid #4f46e5" }}>
          <p style={{ margin: 0, fontSize: "0.9em", color: "#4f46e5" }}>🎯 Reps: <strong>{repCount}</strong></p>
        </div>
        <div
  style={{
    backgroundColor: isMLActive ? "#dcfce7" : "#f3f4f6",
    padding: "10px 20px",
    borderRadius: "8px",
    border: `2px solid ${isMLActive ? "#16a34a" : "#9ca3af"}`,
    opacity: isMLActive ? 1 : 0.6,
  }}
>
  <p
    style={{
      margin: 0,
      fontSize: "0.9em",
      color: isMLActive ? "#16a34a" : "#6b7280",
    }}
  >
    🤖 ML Detection:{" "}
    {isMLActive
      ? mlPrediction || "Detecting..."
      : "Disabled for this exercise"}
    {isMLActive && mlConfidence > 0 && ` (${mlConfidence}%)`}
  </p>
</div>

      </div>

      <div style={{ backgroundColor: poseCorrect ? "#d1fae5" : resting ? "#dbeafe" : "#fef3c7", padding: "15px", borderRadius: "10px", marginBottom: "15px", border: `2px solid ${poseCorrect ? "#10b981" : resting ? "#3b82f6" : "#f59e0b"}` }}>
        <p style={{ fontSize: "1.3em", fontWeight: "bold", margin: "5px 0" }}>{instruction}</p>
        {correction && <p style={{ fontSize: "1.1em", color: "#dc2626", margin: "5px 0" }}>{correction}</p>}
      </div>

      {holding && !resting && (
        <div style={{ backgroundColor: "#dcfce7", padding: "15px", borderRadius: "10px", marginBottom: "10px", border: "2px solid #16a34a" }}>
          <p style={{ fontSize: "1.8em", color: "#16a34a", fontWeight: "bold" }}>⏱️ Hold: {timer.toFixed(1)}s / {holdDuration}s</p>
          <div style={{ width: "100%", backgroundColor: "#e5e7eb", borderRadius: "10px", height: "20px", overflow: "hidden" }}>
            <div style={{ width: `${(timer / holdDuration) * 100}%`, backgroundColor: "#16a34a", height: "100%" }} />
          </div>
        </div>
      )}

      {resting && (
        <div style={{ backgroundColor: "#dbeafe", padding: "15px", borderRadius: "10px", marginBottom: "10px", border: "2px solid #3b82f6" }}>
          {/* MODIFIED: Hardcoding the display text for the rest timer bar */}
          <p style={{ fontSize: "1.8em", color: "#3b82f6", fontWeight: "bold" }}>😌 RELAX! TAKE REST: {breakTimer}s / {breakDuration}s</p>
          <div style={{ width: "100%", backgroundColor: "#e5e7eb", borderRadius: "10px", height: "20px", overflow: "hidden" }}>
            <div style={{ width: `${(breakTimer / breakDuration) * 100}%`, backgroundColor: "#3b82f6", height: "100%" }} />
          </div>
        </div>
      )}

      <video ref={videoRef} style={{ display: "none" }}></video>
      <canvas ref={canvasRef} width="640" height="480" style={{ borderRadius: "12px", boxShadow: "0 6px 20px rgba(0,0,0,0.2)", maxWidth: "100%", height: "auto" }} />

      <div style={{ marginTop: "20px", padding: "15px", backgroundColor: "white", borderRadius: "10px", textAlign: "left", maxWidth: "640px", margin: "20px auto" }}>
        <h3 style={{ color: "#2563eb" }}>📋 Exercise Guide:</h3>
        <ul style={{ lineHeight: "1.8" }}>
          <li>**Both Arms Raise:** Raise BOTH arms straight up vertically</li>
          <li>**Wall Push:** Bend elbows and position arms as if pushing a wall - great for upper body strength</li>
          <li>**Squats:** Bend BOTH knees and lower your body into Squat position</li>
          <li>**Neck Rolls:** Gently roll your head in circles - perfect for desk work stress</li>
          <li>**Shoulder Shrugs:** Lift both shoulders towards ears - releases upper body tension</li>
        </ul>
        <p style={{ marginTop: "15px", color: "#6b7280" }}>
          💡 Hold each position correctly for {holdDuration === 5 ? "5" : "10"} seconds, then rest for {breakDuration} seconds. 
          The skeleton will turn <span style={{ color: "#16a34a", fontWeight: "bold" }}>green</span> when your pose is correct!
        </p>
        <p style={{ marginTop: "10px", color: "#2563eb", fontWeight: "bold" }}>
          ✨ Perfect combination of strength training and stress relief exercises!
        </p>
      </div>
    </div>
  );
};

export default ExerciseCam;
