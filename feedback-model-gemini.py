from google import genai
import json
import os

def ai_toefl_feedback(essay_text):
    """
    AI TOEFL Feedback Generator using Gemini - Fully Dynamic Response
    """
    try:
        # The client gets the API key from the environment variable `GEMINI_API_KEY`.
        os.environ['GEMINI_API_KEY'] = 'AIzaSyCTTSl772mg76ExEmZ5DZeN-w1a-S5XD5g'
        
        client = genai.Client()
        
        # Create comprehensive prompt for dynamic TOEFL feedback
        prompt = f"""
You are an expert TOEFL iBT writing evaluator. Analyze the following essay and provide detailed, dynamic feedback.

Essay to analyze:
"{essay_text}"

Please provide your analysis in EXACTLY this JSON format (no additional text, just valid JSON):

{{
    "original": "{essay_text}",
    "corrected": "provide a grammatically corrected version of the entire text",
    "grammar_errors": count_of_grammar_errors_found,
    "avg_coherence": coherence_score_between_0_and_1_as_decimal,
    "score": overall_toefl_score_between_0_and_5_as_decimal,
    "feedback": [
        "provide 2-4 specific feedback messages about the writing",
        "focus on grammar, coherence, vocabulary, and structure",
        "make each message actionable and specific to this text"
    ],
    "detailed_corrections": [
        {{
            "error_text": "exact_incorrect_phrase_from_original",
            "suggestion": "corrected_version",
            "message": "explanation_of_the_grammar_rule_or_issue"
        }}
    ]
}}

IMPORTANT INSTRUCTIONS:
1. Analyze the actual content dynamically - don't use generic responses
2. Count real grammar errors you find in the text
3. Calculate coherence based on logical flow and connections between sentences
4. Provide specific corrections for actual errors found
5. Give a realistic TOEFL score (0-5) based on grammar, coherence, vocabulary, and task achievement
6. Make feedback specific to this particular essay's strengths and weaknesses
7. Return ONLY valid JSON, no extra text before or after
8. Ensure all string values are properly escaped for JSON
"""

        # Generate content using Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        # Get the response text
        response_text = response.text.strip()
        
        # Clean up response to extract JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        elif "{" in response_text and "}" in response_text:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            json_text = response_text[json_start:json_end]
        else:
            json_text = response_text
        
        # Parse JSON response
        try:
            result = json.loads(json_text)
            
            # Ensure required fields exist and have correct types
            if not isinstance(result.get('grammar_errors'), (int, float)):
                result['grammar_errors'] = 0
            if not isinstance(result.get('avg_coherence'), (int, float)):
                result['avg_coherence'] = 0.5
            if not isinstance(result.get('score'), (int, float)):
                result['score'] = 3.0
            if not isinstance(result.get('feedback'), list):
                result['feedback'] = ["Analysis completed using Gemini AI."]
            if not isinstance(result.get('detailed_corrections'), list):
                result['detailed_corrections'] = []
            
            # Ensure values are within valid ranges
            result['grammar_errors'] = max(0, int(result['grammar_errors']))
            result['avg_coherence'] = max(0.0, min(1.0, float(result['avg_coherence'])))
            result['score'] = max(0.0, min(5.0, float(result['score'])))
            
            # Ensure original and corrected text exist
            if not result.get('original'):
                result['original'] = essay_text.strip()
            if not result.get('corrected'):
                result['corrected'] = essay_text.strip()
            
            return result
            
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return error with Gemini's raw response
            return {
                "original": essay_text.strip(),
                "corrected": essay_text.strip(),
                "grammar_errors": 0,
                "avg_coherence": 0.0,
                "score": 0.0,
                "feedback": [
                    "❌ Gemini Response Parsing Error",
                    f"JSON Parse Error: {str(e)}",
                    f"Raw Gemini Response: {response_text[:200]}..."
                ],
                "detailed_corrections": []
            }
            
    except Exception as e:
        # Handle API errors
        return {
            "original": essay_text.strip(),
            "corrected": essay_text.strip(),
            "grammar_errors": 0,
            "avg_coherence": 0.0,
            "score": 0.0,
            "feedback": [
                "❌ Gemini API Error",
                f"Error: {str(e)}",
                "Please check your API key and internet connection."
            ],
            "detailed_corrections": []
        }

# ------------------------------------------------------------
# Example Test - Only runs when file is executed directly
# ------------------------------------------------------------
if __name__ == "__main__":
    test_essay = """
    Many students want study abroad because they believe it give them more opportunity. 
    Studying in another country help them learn different culture and language. 
    But sometimes they feel lonely and hard to adapt new environment. 
    In my view, studying abroad is good experience if student prepare well before go.
    """
    
    print("Testing Gemini TOEFL Feedback Model (Fully Dynamic)...")
    result = ai_toefl_feedback(test_essay)
    print("Result:")
    print(json.dumps(result, indent=2))
