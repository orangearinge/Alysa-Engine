import sys
import os

# Add the project root to sys.path
sys.path.append('/home/ahmadsaif/project/capstone/Alysa-Engine')

from app.utils.sentiment_analyzer import analyze_sentiment

print("Testing Sentiment Analysis Utility...")
test_texts = [
    "I love this app, it is so helpful!",
    "This is the worst experience ever.",
    "The app is okay, could be better.",
    "Hello!!",
]

for text in test_texts:
    sentiment = analyze_sentiment(text)
    print(f"Text: '{text}' -> Sentiment: {sentiment}")

print("\nVerification complete.")
