# feedback-model-gemini.py
import json

from google import genai


def ai_toefl_feedback(essay_text, mode="learning"):
    """
    English evaluator for mobile app with separate modes for learning and testing.

    Args:
        essay_text (str): The text to evaluate
        mode (str): Either "learning" or "test" to determine evaluation style
                   - "learning": Friendly educational feedback with corrections
                   - "test": Strict TOEFL iBT evaluation (0-5 scale, objective feedback)

    Returns:
        dict: Evaluation results in format appropriate for the mode
              Learning mode: {status, title, feedback, corrected_text}
              Test mode: {score, feedback}
    """

    try:
        client = genai.Client()

        if mode == "test":
            prompt = f"""
Act as a TOEFL iBT evaluator for Speaking/Writing.
Task: Evaluate response strictly (0–5 scale) based on rubric.
Tone: Neutral, objective, formal. No corrections or teaching.

Rubric:
5: Excellent. Clear, effective, minimal errors.
4: Good. Solid, some minor issues.
3: Fair. Noticeable issues, generally understandable.
2: Limited. Frequent errors, insufficient development.
1: Weak. Hard to understand, serious errors.
0: Off-topic or unintelligible.

Response: "{essay_text}"

Output JSON ONLY:
{{
  "score": <int 0-5>,
  "feedback": ["Grammar/Language", "Content Relevance", "Organization", "Vocabulary"]
}}
"""
        else:  # learning mode
            prompt = f"""
Act as an English writing evaluator for a learning app. 
Evaluate short student sentences. Use JSON output only.

Output Format:
{{
  "status": "correct|almost|incorrect",
  "title": "short title + emoji",
  "feedback": "short friendly EN feedback + ID translation",
  "corrected_text": "corrected version or original"
}}

Rules:
- Correct (status: correct, title: Benar 👍)
- Small mistake (status: almost, title: Kurang Tepat 🥹)
- Wrong (status: incorrect, title: Perlu Perbaikan ❗)
- Keep feedback VERY SHORT.

Student Sentence: "{essay_text}"
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        response_text = response.text.strip()

        # Extract JSON
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        json_text = response_text[json_start:json_end]

        result = json.loads(json_text)

        # Safety defaults and validation based on mode
        if mode == "test":
            # Validate and ensure proper test mode response format
            if "score" not in result:
                result["score"] = 0
            else:
                # Ensure score is valid integer between 0-5
                try:
                    score = int(result["score"])
                    result["score"] = max(0, min(5, score))
                except (ValueError, TypeError):
                    result["score"] = 0

            if "feedback" not in result or not isinstance(result["feedback"], list):
                result["feedback"] = ["Unable to evaluate response due to processing error."]

            # Ensure feedback is a list of strings
            if isinstance(result["feedback"], list):
                result["feedback"] = [str(item) for item in result["feedback"] if item]
                if not result["feedback"]:
                    result["feedback"] = ["No specific feedback available."]

        else:  # learning mode
            if "corrected_text" not in result:
                result["corrected_text"] = essay_text
            if "feedback" not in result:
                result["feedback"] = "Feedback unavailable."
            if "status" not in result:
                result["status"] = "unknown"
            if "title" not in result:
                result["title"] = "Info"

        return result

    except json.JSONDecodeError as e:
        # Handle JSON parsing errors specifically
        if mode == "test":
            return {
                "score": 0,
                "feedback": ["Response format error: Unable to parse evaluation results."]
            }
        else:
            return {
                "status": "error",
                "title": "Error ❗",
                "feedback": "Unable to process response format.",
                "corrected_text": essay_text
            }

    except Exception as e:
        # Handle all other errors
        error_msg = str(e)[:100]  # Limit error message length
        if mode == "test":
            return {
                "score": 0,
                "feedback": [f"Processing error: {error_msg}"]
            }
        else:  # learning mode
            return {
                "status": "error",
                "title": "Error ❗",
                "feedback": f"Unable to process: {error_msg}",
                "corrected_text": essay_text
            }


if __name__ == "__main__":
    # Test with different types of responses for both modes

    # Test 1: Learning mode with simple sentence
    learning_text = "I have an apple"
    print("=== LEARNING MODE TEST (Simple Sentence) ===")
    print(json.dumps(ai_toefl_feedback(learning_text, mode="learning"), indent=2))

    # Test 2: Test mode with TOEFL-style speaking response
    speaking_text = "I believe that studying abroad is beneficial for students because it exposes them to different cultures and helps them develop independence. When students live in a foreign country, they must adapt to new situations and solve problems on their own."
    print("\n=== TEST MODE TEST (Speaking Task) ===")
    print(json.dumps(ai_toefl_feedback(speaking_text, mode="test"), indent=2))

    # Test 3: Test mode with TOEFL-style writing response
    writing_text = "In my opinion, technology has significantly improved our daily lives. First, smartphones allow us to communicate instantly with people around the world. Second, the internet provides access to vast amounts of information and educational resources. Finally, medical technology has increased life expectancy and improved treatment options for many diseases. While some argue that technology creates social isolation, I believe the benefits outweigh the drawbacks when used responsibly."
    print("\n=== TEST MODE TEST (Writing Task) ===")
    print(json.dumps(ai_toefl_feedback(writing_text, mode="test"), indent=2))

    # Test 4: Error handling test
    print("\n=== ERROR HANDLING TEST ===")
    print(json.dumps(ai_toefl_feedback("", mode="test"), indent=2))
