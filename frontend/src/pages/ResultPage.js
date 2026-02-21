import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/ResultPage.css";
import runnerImg from "../assets/runner.png";
import farmerImg from "../assets/farmer.png";

const ResultPage = () => {
    const navigate = useNavigate();

    const questions = [
        "In the last month, how often have you been upset because of something that happened unexpectedly?",
        "In the last month, how often have you felt that you were unable to control important things in your life?",
        "In the last month, how often have you felt nervous and stressed?",
        "In the last month, how often have you felt confident about your ability to handle personal problems?",
        "In the last month, how often have you felt that things were going your way?",
        "In the last month, how often have you found that you could not cope with all the things you had to do?",
        "In the last month, how often have you been able to control irritations in your life?",
        "In the last month, how often have you felt that you were on top of things?",
        "In the last month, how often have you been angered because of things that happened that were outside of your control?",
        "In the last month, how often have you felt difficulties were piling up so high that you could not overcome them?"
    ];

    const options = [0, 1, 2, 3, 4];

    const [answers, setAnswers] = useState(Array(10).fill(0));
    const [stressLevel, setStressLevel] = useState(null);
    const [selectedInterests, setSelectedInterests] = useState([]);
    const [videos, setVideos] = useState([]);

    const interestsList = ["Music", "Exercise", "Reading", "Meditation", "Gaming", "Art", "Cooking"];

    const handleChange = (index, value) => {
        const newAnswers = [...answers];
        newAnswers[index] = value;
        setAnswers(newAnswers);
    };

    const calculateStressLevel = () => {
        const totalScore = answers.reduce((acc, curr) => acc + curr, 0);
        let level;

        if (totalScore <= 13) level = "Low";
        else if (totalScore <= 26) level = "Moderate";
        else level = "High";

        setStressLevel(level);
    };

    const handleInterestChange = (event) => {
        const selectedValues = Array.from(event.target.selectedOptions, option => option.value);
        setSelectedInterests(selectedValues);
    };

    const fetchRecommendations = async () => {
        if (!stressLevel) {
            alert("Please calculate your stress level first!");
            return;
        }

        if (selectedInterests.length === 0) {
            alert("Please select at least one area of interest!");
            return;
        }

        try {
            console.log("Fetching recommendations for:", selectedInterests, "Stress Level:", stressLevel);
            const params = new URLSearchParams();
selectedInterests.forEach(interest => params.append("interests", interest));
params.append("stress_level", stressLevel);

const res = await fetch(`http://127.0.0.1:8001/recommendations?${params.toString()}`);

            console.log("Response status:", res.status);
            if (!res.ok) {
                throw new Error(`Failed to fetch recommendations: ${res.statusText}`);
            }

            const data = await res.json();
            console.log("Fetched data:", data);
            setVideos(data);
        } catch (error) {
            console.error("Error fetching recommendations:", error);
        }
    };

    return (
        <div className="result-container">
            <nav className="navbar">
                <div className="logo">AVASTHI</div>
                <div className="nav-links">
                    <a href="/">HOME</a>
                    <a href="#about">ABOUT US</a>
                    <a href="#resources">RESOURCES</a>
                    <a href="#contact">CONTACT</a>
                </div>
            </nav>

            <div className="main-content">
                <img src={runnerImg} alt="Running Character" className="left-img" />
                <div className="text-content">
                    <h2>PSS Stress Test</h2>
                    <div className="questions">
                        {questions.map((question, index) => (
                            <div key={index} className="question">
                                <p>{question}</p>
                                <select onChange={(e) => handleChange(index, Number(e.target.value))}>
                                    {options.map((option) => (
                                        <option key={option} value={option}>{option}</option>
                                    ))}
                                </select>
                            </div>
                        ))}
                    </div>
                    <button className="btn" onClick={calculateStressLevel}>Find My Stress Level</button>
                    {stressLevel && (
                        <h3>Your Stress Level: <span className={stressLevel.toLowerCase().replace(" ", "-")}>{stressLevel}</span></h3>
                    )}
                </div>
                <img src={farmerImg} alt="Farmer Character" className="right-img" />
            </div>

            {stressLevel && (
                <div className="recommendations">
                    <h3>🎯 Select Your Areas of Interest:</h3>
                    <select className="interest-dropdown" multiple onChange={handleInterestChange}>
                        {interestsList.map((interestItem) => (
                            <option key={interestItem} value={interestItem}>{interestItem}</option>
                        ))}
                    </select>

                    <p>Selected Interests: {selectedInterests.join(", ") || "None"}</p>

                    <button className="btn" onClick={fetchRecommendations}>Get Recommendations</button>

                    <div className="video-grid">
                        {videos.length > 0 ? (
                            videos.map((video, i) => (
                                <div key={i} className="video-card">
                                    <img src={video.thumbnail} alt={video.title} className="video-thumbnail" />
                                    <p>{video.title}</p>
                                    <a href={video.url} target="_blank" rel="noopener noreferrer" className="watch-btn">Watch</a>
                                </div>
                            ))
                        ) : (
                            <p>No recommendations yet. Select an interest and click "Get Recommendations".</p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default ResultPage;
