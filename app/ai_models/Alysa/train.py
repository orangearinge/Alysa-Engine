import pandas as pd
import joblib
import language_tool_python
import numpy as np

from sentence_transformers import SentenceTransformer, util
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error


# ===== INIT =====
tool = language_tool_python.LanguageTool("en-US")
embedder = SentenceTransformer("all-MiniLM-L6-v2")


def extract_features(question, answer):
    grammar_errors = len(tool.check(answer))

    words = answer.split()
    word_count = len(words)
    lexical_ratio = len(set(words)) / max(1, word_count)

    q_emb = embedder.encode(question)
    a_emb = embedder.encode(answer)
    relevance = util.cos_sim(q_emb, a_emb).item()

    content_score = min(1.0, word_count / 60)

    return [
        grammar_errors,
        word_count,
        lexical_ratio,
        relevance,
        content_score
    ]


# ===== LOAD DATA =====
df = pd.read_csv("dataset.csv")

X = df.apply(
    lambda r: extract_features(r["question"], r["answer"]),
    axis=1
).tolist()

y = df["score"]

# ===== SPLIT =====
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# ===== MODEL =====
model = RandomForestRegressor(
    n_estimators=300,
    max_depth=12,
    random_state=42
)

print("Training started...")

model.fit(X_train, y_train)

print("Training finished")

joblib.dump(model, "model.pkl")

print("Model saved as model.pkl")
print("Current dir:", os.getcwd())
print("Files:", os.listdir("."))