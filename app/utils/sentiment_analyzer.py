from gradio_client import Client

def analyze_sentiment(text):
    """
    Analyzes the sentiment of the given text using the Hugging Face model.
    """
    try:
        client = Client("ahmdsaif/alysa-sentiment")
        result = client.predict(
            text=text,
            api_name="/predict_sentiment"
        )
        # Result is like {'sentiment': 'positive', 'confidence': 0.9189}
        if isinstance(result, dict) and 'sentiment' in result:
            label = result['sentiment'].capitalize()
            return label
        return str(result)
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return "Unknown"
