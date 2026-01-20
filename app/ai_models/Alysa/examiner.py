import os

import joblib
import language_tool_python
from sentence_transformers import SentenceTransformer, util

# ===== LOAD TOOLS =====
tool = language_tool_python.LanguageTool("en-US")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ===== LOAD MODEL =====
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, "model.pkl")
model = joblib.load(model_path)


# FEATURE EXTRACTION
def extract_features(question, answer):
    grammar_errors = len(tool.check(answer))

    words = answer.split()
    word_count = len(words)
    lexical_ratio = len(set(words)) / max(1, word_count)

    q_emb = embedder.encode(question)
    a_emb = embedder.encode(answer)
    relevance = util.cos_sim(q_emb, a_emb).item()

    content_score = min(1.0, word_count / 60)

    features = [grammar_errors, word_count, lexical_ratio, relevance, content_score]

    diagnostics = {
        "grammar_errors": grammar_errors,
        "lexical_ratio": lexical_ratio,
        "relevance": relevance,
        "word_count": word_count,
    }

    return features, diagnostics


# SCORING FEEDBACK (DIAGNOSTIC)
def generate_feedback(score, d):
    evaluation = {
        "relevance": (
            "The response stays on topic and addresses the prompt directly."
            if d["relevance"] >= 0.6
            else "The response is partially relevant but could focus more on the key points."
            if d["relevance"] >= 0.35
            else "The response deviates significantly from the prompt."
        ),
        "coherence": (
            "Ideas are logically connected and the flow is clear."
            if d["word_count"] >= 50
            else "The response has a basic structure but could benefit from better transitions."
            if d["word_count"] >= 30
            else "The response lacks sufficient depth for a coherent evaluation."
        ),
        "vocabulary": (
            "A good variety of words is used appropriately."
            if d["lexical_ratio"] >= 0.5
            else "Vocabulary is adequate, though some repetition is noted."
            if d["lexical_ratio"] >= 0.3
            else "Vocabulary usage is quite limited and repetitive."
        ),
        "grammar": (
            "Grammatical accuracy is generally good with few errors."
            if d["grammar_errors"] <= 2
            else "There are some grammatical mistakes, but they do not hinder comprehension."
            if d["grammar_errors"] <= 5
            else "Frequent grammatical errors impact the readability of the text."
        ),
    }

    feedback_list = [
        f"Relevance: {evaluation['relevance']}",
        f"Coherence: {evaluation['coherence']}",
        f"Vocabulary: {evaluation['vocabulary']}",
        f"Grammar: {evaluation['grammar']}",
    ]

    return evaluation, feedback_list


# SUGGESTED CORRECTION (RULE-BASED NLG)
PHRASE_CORRECTIONS = {
    "a lot of": "a significant amount of",
    "very important": "critically important",
    "big problem": "major issue",
    "really hard": "challenging",
    "don't have borders": "transcend national boundaries",
}


def generate_suggested_correction(answer: str):
    corrected = answer
    applied = False

    for informal, formal in PHRASE_CORRECTIONS.items():
        if informal in corrected.lower():
            corrected = corrected.replace(informal, formal)
            applied = True

    if applied:
        return corrected

    return (
        "The response is generally clear. To improve academic quality, "
        "consider using more formal vocabulary and expanding key ideas "
        "with specific examples."
    )


# REFERENCE ANSWER (RETRIEVAL-BASED)
REFERENCE_BANK = {
    "default": {
        "agree": (
            "Many global issues require international cooperation because their "
            "impact extends beyond national borders. However, effective solutions "
            "also depend on individual responsibility and strong local policies."
        ),
        "balanced": (
            "While international collaboration is essential for addressing global "
            "challenges, individuals and governments at the local level also play "
            "a crucial role in implementing practical solutions."
        ),
        "disagree": (
            "Although global cooperation is beneficial, many problems can still be "
            "effectively addressed through national policies and individual action."
        ),
    }
}


def detect_stance(answer: str):
    a = answer.lower()
    if "however" in a or "but" in a:
        return "balanced"
    if "disagree" in a:
        return "disagree"
    return "agree"


def get_reference_answer(answer: str):
    stance = detect_stance(answer)
    return REFERENCE_BANK["default"].get(
        stance, "A suitable reference answer is not available."
    )


# MAIN EVALUATION FUNCTION
def evaluate(question, answer):
    features, diag = extract_features(question, answer)

    raw_score = model.predict([features])[0]

    # Scale from 0–5 → IELTS 0–9
    ielts_score = (raw_score / 5.0) * 9.0
    score = round(ielts_score * 2) / 2
    score = max(0.0, min(9.0, score))

    evaluation, feedback = generate_feedback(raw_score, diag)

    suggested_correction = generate_suggested_correction(answer)
    reference_answer = get_reference_answer(answer)

    pro_tips = []
    if diag["word_count"] < 150:
        pro_tips.append("Increase your response length to at least 150 words.")
    if diag["lexical_ratio"] < 0.5:
        pro_tips.append("Use a wider range of vocabulary to avoid repetition.")
    if diag["grammar_errors"] > 3:
        pro_tips.append("Review grammar rules such as subject–verb agreement.")

    return {
        "score": score,
        "feedback": feedback,
        "suggested_correction": suggested_correction,
        "evaluation": evaluation,
        "pro_tips": pro_tips,
        "reference_answer": reference_answer,
    }
