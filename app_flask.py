import json
import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from analysis import analyze_answers
from generate_questions import generate_quiz_questions


app = Flask(__name__)
CORS(app)


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "online-quiz-system"})


@app.get("/api/demo")
def demo():
    return jsonify({"message": "Azure quiz system ready", "focus": "personalized prep"})


@app.post("/start")
def start():
    data = request.get_json(silent=True) or {}
    topic = (data.get("topic") or "General Knowledge").strip()
    level = (data.get("level") or "Beginner").strip()
    count = int(data.get("count") or 5)
    questions = generate_quiz_questions(topic, level=level, count=count)
    return jsonify({"topic": topic, "level": level, "questions": questions})


@app.post("/answer")
def answer():
    data = request.get_json(silent=True) or {}
    answers = data.get("answers", [])
    feedback = analyze_answers(answers)
    return jsonify({"feedback": feedback, "answers": answers})


@app.get("/result")
def result():
    return jsonify({"score": 0, "feedback": "Complete the quiz to see your result."})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
