import os

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from analysis import analyze_answers
from generate_questions import generate_quiz_questions


app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "online-quiz-system"})


@app.get("/api/demo")
def demo():
    return jsonify({"message": "Azure quiz system ready", "focus": "personalized prep"})


@app.post("/start")
def start():
    data = request.get_json(silent=True) or {}
    topic = (data.get("topic") or "General Knowledge").strip() or "General Knowledge"
    level = (data.get("level") or "Beginner").strip() or "Beginner"
    rounds = max(1, int(data.get("rounds") or 5))
    count = max(1, int(data.get("count") or 10))

    rounds_payload = []
    for round_index in range(rounds):
        rounds_payload.append({
            "round": round_index + 1,
            "level": level,
            "questions": generate_quiz_questions(topic, level=level, count=count),
        })

    return jsonify({"topic": topic, "level": level, "rounds": rounds_payload})


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
    port = int(os.getenv("PORT", 5000))
    token = os.getenv("NGROK_AUTH_TOKEN")

    if not token:

    print(f"Public URL: {public_url}")

    app.run(debug=True, host="0.0.0.0", port=port)
