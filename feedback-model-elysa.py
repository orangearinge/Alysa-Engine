# AI TOEFL Feedback Generator
import language_tool_python
from sentence_transformers import SentenceTransformer, util
import torch
import re

def ai_toefl_feedback(essay_text):
    # ------------------------------------------------------------
    # 1. Grammar Check (LanguageTool)
    # ------------------------------------------------------------
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(essay_text)
    corrected = tool.correct(essay_text)
    grammar_errors = len(matches)

    detailed_corrections = []
    for match in matches:
        detailed_corrections.append({
            "context": match.context.strip(),
            "suggestion": match.replacements[0] if match.replacements else None,
            "message": match.message
        })

    # ------------------------------------------------------------
    # 2. Coherence Check (Semantic Similarity)
    # ------------------------------------------------------------
    # Split essay into sentences using regex
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', essay_text) if s.strip()]
    avg_coherence = 0.0

    if len(sentences) > 1:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(sentences, convert_to_tensor=True)

        sims = []
        for i in range(len(sentences) - 1):
            sim = util.cos_sim(embeddings[i], embeddings[i + 1]).item()
            sims.append(sim)

        avg_coherence = sum(sims) / len(sims)
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # ------------------------------------------------------------
    # 3. AI-Style Scoring (Heuristic)
    # ------------------------------------------------------------
    # Base score: 4.0, penalize grammar errors, reward coherence
    score = max(0, min(5, 4.0 - grammar_errors * 0.2 + avg_coherence * 1.0))

    # ------------------------------------------------------------
    # 4. Feedback Generation
    # ------------------------------------------------------------
    feedback = []
    if grammar_errors > 3:
        feedback.append(f"You have several grammar mistakes ({grammar_errors}). Focus on verb agreement, articles, and sentence structure.")
    elif grammar_errors > 0:
        feedback.append(f"Minor grammar issues detected ({grammar_errors}). Try to proofread more carefully.")
    if len(sentences) > 1 and avg_coherence < 0.5:
        feedback.append("Your essay could be more coherent. Add transitions between ideas (e.g., 'however', 'moreover').")
    if not feedback:
        feedback.append("Good job! Your writing is grammatically sound and well-connected.")

    # ------------------------------------------------------------
    # 5. Return Structured Output
    # ------------------------------------------------------------
    tool.close()
    return {
        "original": essay_text.strip(),
        "corrected": corrected.strip(),
        "grammar_errors": grammar_errors,
        "avg_coherence": round(avg_coherence, 3),
        "score": round(score, 2),
        "feedback": feedback,
        "detailed_corrections": detailed_corrections
    }

# ------------------------------------------------------------
# Example Test
# ------------------------------------------------------------
essay = """
Many students want study abroad because they believe it give them more opportunity. 
Studying in another country help them learn different culture and language. 
But sometimes they feel lonely and hard to adapt new environment. 
In my view, studying abroad is good experience if student prepare well before go.
"""

result = ai_toefl_feedback(essay)
print(result)
