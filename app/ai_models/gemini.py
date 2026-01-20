# feedback-model-gemini.py
import json
from google import genai

def ai_toefl_feedback(essay_text, mode="learning"):
    """
    English evaluator for mobile app with separate modes for learning and testing.
    """

    try:
        client = genai.Client()

        if mode == "test":
            prompt = f"""
Act as an official IELTS/TOEFL Examiner. 
Evaluate the following student response and provide feedback that is scannable and educational.

User Response: "{essay_text}"

Output JSON ONLY with the following structure:
{{
  "score": <float 0.0-9.0>,
  "suggested_correction": "Re-write the sentence with polished grammar and flow",
  "evaluation": {{
    "relevance": "Short feedback on relevance",
    "coherence": "Short feedback on flow/logic",
    "vocabulary": "Feedback on word choice & variety",
    "grammar": "Feedback on accuracy & range"
  }},
  "pro_tips": [
    "Specific tip 1 to reach higher band",
    "Specific tip 2 to reach higher band"
  ],
  "reference_answer": "A high-scoring (Band 8+) version of this response"
}}

Rules:
- Keep feedback points concise.
- Ensure 'suggested_correction' is a complete, improved version of the response.
- Score MUST be between 0.0 and 9.0 (IELTS band scale).
"""
        else:  # learning mode
            prompt = f"""
Act as a friendly English Tutor for a learning app. 
Focus on immediate correction and encouragement.

Student Sentence: "{essay_text}"

Output ONLY a JSON object:
{{
  "status": "correct|almost|incorrect",
  "title": "short title + emoji (e.g., 'Mantap! 🌟' or 'Sedikit lagi! 💡')",
  "feedback_id": "Penjelasan singkat dalam Bahasa Indonesia",
  "feedback_en": "Brief explanation in English",
  "corrected_text": "The corrected version"
}}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )

        response_text = response.text.strip()
        print(f"Gemini Response: {response_text[:100]}...") # Debug log

        # Extract JSON logic
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        
        if json_start == -1 or json_end <= json_start:
             raise ValueError(f"Invalid JSON response from Gemini: {response_text}")

        json_text = response_text[json_start:json_end]
        result = json.loads(json_text)

        # Safety defaults for TEST mode
        if mode == "test":
            if "score" not in result:
                result["score"] = 0.0
            if "suggested_correction" not in result:
                result["suggested_correction"] = ""
            if "evaluation" not in result or not isinstance(result["evaluation"], dict):
                result["evaluation"] = {
                    "relevance": "N/A",
                    "coherence": "N/A",
                    "vocabulary": "N/A",
                    "grammar": "N/A"
                }
            if "pro_tips" not in result or not isinstance(result["pro_tips"], list):
                result["pro_tips"] = []
            if "reference_answer" not in result:
                result["reference_answer"] = ""
            
            # Legacy compatibility for parts of the app expecting a flat list of feedback
            if "feedback" not in result or not result["feedback"]:
                eval_dict = result.get("evaluation", {})
                result["feedback"] = [
                    f"Relevance: {eval_dict.get('relevance', 'N/A')}",
                    f"Coherence: {eval_dict.get('coherence', 'N/A')}",
                    f"Vocabulary: {eval_dict.get('vocabulary', 'N/A')}",
                    f"Grammar: {eval_dict.get('grammar', 'N/A')}"
                ]
            
            # Ensure score is within range
            try:
                result["score"] = max(0.0, min(9.0, float(result.get("score", 0))))
            except:
                result["score"] = 0.0

        return result

    except Exception as e:
        print(f"ERROR in ai_toefl_feedback: {e}") # Print to terminal for debugging
        error_msg = str(e)[:100]
        if mode == "test":
            return {
                "score": 0, 
                "error": f"Error: {error_msg}",
                "suggested_correction": f"Evaluation error: {error_msg}",
                "evaluation": {"relevance": "Error", "coherence": "Error", "vocabulary": "Error", "grammar": "Error"},
                "pro_tips": ["System was unable to generate feedback."],
                "reference_answer": ""
            }
        else:
            return {"status": "error", "title": "Error ❗", "feedback_id": "Gagal memproses."}


if __name__ == "__main__":
    # Test Simulasi sesuai gambar yang kamu kirim
    user_input = "I agree with that because teach students manage their money from the young age so later they can wisely to use money."
    
    print("\n=== HASIL FEEDBACK TEST MODE (BARU) ===")
    feedback = ai_toefl_feedback(user_input, mode="test")
    print(json.dumps(feedback, indent=2))