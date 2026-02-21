from textblob import TextBlob

def analyze_emotion(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.3:
        mood = "positive"
    elif polarity < -0.3:
        mood = "negative"
    else:
        mood = "neutral"

    return mood, [{"label": mood, "score": abs(polarity)}]