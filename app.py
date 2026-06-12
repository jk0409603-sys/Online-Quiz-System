import os
from collections import Counter
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS

load_dotenv()

try:
    from openai import AzureOpenAI
    _oai_client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY", ""),
        api_version="2024-02-01",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
    )
    OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    OPENAI_OK = bool(os.getenv("AZURE_OPENAI_KEY"))
except Exception:
    _oai_client = None
    OPENAI_OK = False

try:
    from azure.ai.textanalytics import TextAnalyticsClient
    from azure.core.credentials import AzureKeyCredential
    _lang_client = TextAnalyticsClient(
        endpoint=os.getenv("AZURE_LANGUAGE_ENDPOINT", ""),
        credential=AzureKeyCredential(os.getenv("AZURE_LANGUAGE_KEY", "")),
    )
    LANGUAGE_OK = bool(os.getenv("AZURE_LANGUAGE_KEY"))
except Exception:
    _lang_client = None
    LANGUAGE_OK = False

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "questions_db.txt"
HISTORY_FILE = BASE_DIR / "history.txt"
RESULTS_FILE = BASE_DIR / "results.txt"

@app.get("/")
def index():
    return "<h1>Adaptive IT Learning Hub</h1><p>API is running!</p>"

@app.get("/api/health")
def health():
    q = sum(1 for _ in DATA_FILE.open("r", encoding="utf-8")) if DATA_FILE.exists() else 0
    return jsonify({"status": "ok", "questions": q, "azure_openai": OPENAI_OK, "azure_language": LANGUAGE_OK})

@app.get("/api/demo")
def demo():
    return jsonify({"message": "Adaptive mode ready: revisit loops, functions, and reasoning before next quiz.", "focus": "Python basics + problem solving", "difficulty": "medium", "source": "fallback"})

@app.post("/api/analyze")
def analyze():
    data = request.get_json(silent=True) or {}
    answers = data.get("answers", [])
    text = " ".join(answers).lower()
    detected = [k for k in ["recursion","loop","function","variable","array","class","algorithm","mathematics","sorting"] if k in text]
    advice = f"Review these topics: {', '.join(detected)}." if detected else "Keep practising regularly."
    return jsonify({"weak_topics": detected, "advice": advice, "source": "fallback"})

@app.get("/api/analytics")
def analytics():
    question_count = sum(1 for _ in DATA_FILE.open("r", encoding="utf-8")) if DATA_FILE.exists() else 0
    history_lines = [l.strip() for l in HISTORY_FILE.open("r", encoding="utf-8") if l.strip()] if HISTORY_FILE.exists() else []
    results_lines = [l.strip() for l in RESULTS_FILE.open("r", encoding="utf-8") if l.strip()] if RESULTS_FILE.exists() else []
    return jsonify({"sessions": len(history_lines) + len(results_lines), "questions": question_count, "topics": "Python, Loops, Functions"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
