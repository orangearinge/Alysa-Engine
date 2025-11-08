# feedback-model-gemini.py
from google import genai
import json
import os
from config import Config

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
You are an official TOEFL iBT test evaluation assistant for SPEAKING and WRITING sections.

Your job is to:
- Evaluate individual TOEFL iBT task responses (this is ONE task out of 6 total)
- Score the performance strictly using TOEFL iBT scoring rubrics (0–5 scale)
- Provide concise, objective evaluator-style feedback
- Be stateless - evaluate ONLY this specific task response

Focus on:
- Grammar accuracy and language use
- Idea development and content relevance
- Coherence and organization
- Lexical range and vocabulary appropriateness
- Speaking tasks: fluency, clarity, pronunciation (evaluate as if spoken)
- Writing tasks: cohesion, structure, clarity, academic development

IMPORTANT RULES:
- This is a FORMAL TEST EVALUATION, NOT A LEARNING SESSION
- Do NOT rewrite or correct the user's answer
- Do NOT give step-by-step teaching or suggestions for improvement
- Do NOT be friendly, encouraging, or overly positive
- Stay neutral, objective, and evaluator-like in tone
- Output must be based ONLY on the provided text
- Do NOT reference other tasks or overall performance

Evaluate this individual task response:
"{essay_text}"

OUTPUT FORMAT (JSON only, no other text):
{{
  "score": <integer 0-5>,
  "feedback": [
      "Objective assessment of grammar and language use",
      "Evaluation of content development and relevance", 
      "Assessment of organization and coherence",
      "Comments on vocabulary and lexical range"
  ]
}}

TOEFL iBT Scoring Rubric:
5 = Excellent: Well-developed, clear, effective communication, minimal errors
4 = Good: Generally well-developed, clear, some minor issues but solid overall
3 = Fair: Somewhat developed, generally understandable, noticeable issues
2 = Limited: Insufficient development, unclear communication, frequent errors
1 = Weak: Very limited development, difficult to understand, serious errors
0 = Off-topic: No response, completely off-topic, or unintelligible

Provide ONLY the JSON response.
"""
        else:  # learning mode
            prompt = f"""
You are an English writing evaluator for a mobile learning app.
Your task is to evaluate VERY SHORT English sentences from beginner and intermediate learners.

Analyze the student's sentence below:
"{essay_text}"

Return feedback ONLY in this JSON format, nothing else:

{{
  "status": "correct_or_incorrect",
  "title": "short_title_with_emoji",
  "feedback": "one short friendly English sentence + Indonesian translation",
  "corrected_text": "the corrected sentence or the same sentence if correct"
}}

Rules:
1. If the sentence is correct:
   - status: "correct"
   - title: "Benar 👍"
   - feedback: short positive note + Indonesian version
   - corrected_text: original sentence

2. If it has a small mistake:
   - status: "almost"
   - title: "Kurang Tepat 🥹"
   - feedback: short improvement note + Indonesian version
   - corrected_text: corrected version

3. If it's wrong:
   - status: "incorrect"
   - title: "Perlu Perbaikan ❗"
   - feedback: short explanation + Indonesian version
   - corrected_text: corrected version

4. Keep feedback VERY SHORT, suitable for a mobile UI bottom sheet.
5. Output only valid JSON.
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
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
