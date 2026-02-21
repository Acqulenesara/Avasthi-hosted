import React, { useState } from 'react';
import './EmotionMusicPlayer.css'; // Import CSS

const EmotionMusicPlayer = () => {
  const [hoveredEmotion, setHoveredEmotion] = useState(null);

  const songCollections = {
    happy: [
      "https://music.youtube.com/watch?v=ZbZSe6N_BXs",
      "https://music.youtube.com/watch?v=y6Sxv-sUYtM",
      "https://music.youtube.com/watch?v=nfWlot6h_JM",
      "https://music.youtube.com/watch?v=ru0K8uYEZWw",
      "https://music.youtube.com/watch?v=fLexgOxsZu0",
      "https://music.youtube.com/watch?v=aJOTlE1K90k",
      "https://music.youtube.com/watch?v=kYtGl1dX5qI",
      "https://music.youtube.com/watch?v=WbN0nX61rIs"
    ],
    sad: [
      "https://music.youtube.com/watch?v=4NRXx6U8ABQ",
      "https://music.youtube.com/watch?v=8AHCfZTRGiI",
      "https://music.youtube.com/watch?v=n4RjJKxsamQ",
      "https://music.youtube.com/watch?v=FB3ptjiNJsY",
      "https://music.youtube.com/watch?v=hTWKbfoikeg",
      "https://music.youtube.com/watch?v=5anLPw0Efmo",
      "https://music.youtube.com/watch?v=vt1Pwfnh5pc",
      "https://music.youtube.com/watch?v=3MB8C1npOhI"
    ],
    angry: [
      "https://music.youtube.com/watch?v=xO1TScQwu6g",
      "https://music.youtube.com/watch?v=04F4xlWSFh0",
      "https://music.youtube.com/watch?v=WsSCjIWFmyY",
      "https://music.youtube.com/watch?v=CSvFpBOe8eY",
      "https://music.youtube.com/watch?v=qeMFqkcPYcg",
      "https://music.youtube.com/watch?v=j_QLzthSkfM",
      "https://music.youtube.com/watch?v=7qrRzNidzIc",
      "https://music.youtube.com/watch?v=L397TWLwrUU"
    ],
    relaxed: [
      "https://music.youtube.com/watch?v=UnPMoAb4y8U",
      "https://music.youtube.com/watch?v=HEuKbwyQbEs",
      "https://music.youtube.com/watch?v=hHW1oY26kxQ",
      "https://music.youtube.com/watch?v=9jK-NcRmVcw",
      "https://music.youtube.com/watch?v=NvryolGa19A",
      "https://music.youtube.com/watch?v=J7HIxqDpJ0Q",
      "https://music.youtube.com/watch?v=RDF_Tyqq4zI",
      "https://music.youtube.com/watch?v=MElfYleGIVU"
    ],
    anxious: [
      "https://music.youtube.com/watch?v=YQHsXMglC9A",
      "https://music.youtube.com/watch?v=ktvTqknDobU",
      "https://music.youtube.com/watch?v=gH476CxJxfg",
      "https://music.youtube.com/watch?v=hLQl3WQQoQ0",
      "https://music.youtube.com/watch?v=u9Dg-g7t2l4",
      "https://music.youtube.com/watch?v=ScNNfyq3d_w",
      "https://music.youtube.com/watch?v=PVjiKRfKpPI",
      "https://music.youtube.com/watch?v=JkK8g6FMEXE"
    ]
  };

  const emotions = [
    { id: 'happy', emoji: '😊', label: 'Happy', description: 'Upbeat & Energetic' },
    { id: 'sad', emoji: '😢', label: 'Sad', description: 'Melancholic & Soothing' },
    { id: 'angry', emoji: '😠', label: 'Angry', description: 'Intense & Powerful' },
    { id: 'relaxed', emoji: '😌', label: 'Relaxed', description: 'Calm & Peaceful' },
    { id: 'anxious', emoji: '😨', label: 'Anxious', description: 'Calming & Comforting' }
  ];

  const redirectToYouTube = (mood) => {
    const songs = songCollections[mood];
    if (songs && songs.length > 0) {
      const randomIndex = Math.floor(Math.random() * songs.length);
      const randomSong = songs[randomIndex];
      window.open(randomSong, '_blank');
    } else {
      alert("No songs found for this mood!");
    }
  };

  return (
    <div className="player-container">
      <header className="player-header">
        <div className="emoji-icon">🎵</div>
        <h1>How are you feeling today?</h1>
        <p>Choose your mood and discover a new song every time you click!</p>
      </header>

      <div className="emotions-grid">
        {emotions.map((emotion) => (
          <div
            key={emotion.id}
            className={`emotion-card ${hoveredEmotion === emotion.id ? 'hovered' : ''}`}
            onClick={() => redirectToYouTube(emotion.id)}
            onMouseEnter={() => setHoveredEmotion(emotion.id)}
            onMouseLeave={() => setHoveredEmotion(null)}
            tabIndex={0}
            role="button"
            aria-label={`Play ${emotion.label} playlist`}
          >
            <div className="emoji">{emotion.emoji}</div>
            <h3>{emotion.label}</h3>
            <p>{emotion.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EmotionMusicPlayer;
