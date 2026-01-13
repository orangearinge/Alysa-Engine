import os
import joblib
import language_tool_python
from sentence_transformers import SentenceTransformer, util

# ===== LOAD =====
tool = language_tool_python.LanguageTool("en-US")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Get absolute path to model file
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, "model.pkl")
model = joblib.load(model_path)


def extract_features(question, answer):
    grammar_errors = len(tool.check(answer))

    words = answer.split()
    word_count = len(words)
    lexical_ratio = len(set(words)) / max(1, word_count)

    q_emb = embedder.encode(question)
    a_emb = embedder.encode(answer)
    relevance = util.cos_sim(q_emb, a_emb).item()

    content_score = min(1.0, word_count / 60)

    features = [
        grammar_errors,
        word_count,
        lexical_ratio,
        relevance,
        content_score
    ]

    diagnostics = {
        "grammar_errors": grammar_errors,
        "lexical_ratio": lexical_ratio,
        "relevance": relevance,
        "word_count": word_count
    }

    return features, diagnostics


def generate_feedback(score, d):
    feedback = []

    if d["relevance"] < 0.35:
        feedback.append("The response is not relevant to the question.")
    elif d["relevance"] < 0.6:
        feedback.append("The response is partially relevant but lacks focus.")

    if d["grammar_errors"] > 6:
        feedback.append("Frequent grammatical errors affect clarity.")
    elif d["grammar_errors"] > 2:
        feedback.append("Some grammatical errors are present.")

    if d["lexical_ratio"] < 0.4:
        feedback.append("Vocabulary usage is limited.")

    if d["word_count"] < 40:
        feedback.append("The response is underdeveloped.")

    if score >= 4:
        feedback.append("The task is addressed effectively.")
    elif score <= 2:
        feedback.append("The response needs significant improvement.")

    return feedback


def evaluate(question, answer):
    features, diag = extract_features(question, answer)

    raw_score = model.predict([features])[0]
    score = round(raw_score)
    score = max(0, min(5, score))

    return {
        "model": "ALYSA",
        "score": score,
        "feedback": generate_feedback(score, diag)
    }