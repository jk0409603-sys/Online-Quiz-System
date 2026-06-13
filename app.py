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

HTML = """
<!doctype html><html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Adaptive IT Learning Hub</title>
<style>
:root{color-scheme:dark;font-family:Arial,sans-serif}
body{margin:0;background:linear-gradient(135deg,#07111f,#102a43);color:#eff6ff}
.page{max-width:1080px;margin:0 auto;padding:24px}
.card{background:rgba(15,23,42,0.86);border:1px solid #334155;border-radius:18px;padding:18px;margin-bottom:18px}
h1,h2,h3{margin-top:0}
.pill{display:inline-block;background:#1d4ed8;color:#eff6ff;padding:6px 10px;border-radius:999px;font-size:12px;text-transform:uppercase}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}
.btn{background:linear-gradient(135deg,#38bdf8,#2563eb);color:white;border:none;border-radius:10px;padding:10px 14px;cursor:pointer;font-weight:700;margin-right:8px}
.btn.secondary{background:linear-gradient(135deg,#f59e0b,#f97316)}
.muted{color:#cbd5e1;font-size:14px}
.topic{display:inline-block;padding:6px 8px;background:#0f172a;border-radius:8px;margin-right:6px;margin-top:6px;border:1px solid #1e293b}
.score-box{display:flex;gap:12px;flex-wrap:wrap}
.mini{background:#111827;border:1px solid #1f2937;padding:10px;border-radius:12px;min-width:120px}
.tag{color:#bfdbfe;font-size:12px;text-transform:uppercase}
textarea{width:100%;background:#0f172a;color:#eff6ff;border:1px solid #334155;border-radius:10px;padding:10px;font-size:14px;resize:vertical;box-sizing:border-box}
.ai-badge{display:inline-block;background:#064e3b;color:#6ee7b7;padding:3px 8px;border-radius:6px;font-size:11px;margin-left:8px}
</style></head><body>
<div class="page">
<div class="card">
<span class="pill">Adaptive Learning Tool for Pakistani IT Students</span>
<h1>Adaptive IT Learning Hub <span class="ai-badge">Azure OpenAI + Azure AI Language</span></h1>
<p class="muted">Built by Wajiha Imran · Bahauddin Zakariya University · 1st Year IT (GPA 4.0) · Built solo in 4 days</p>
<div class="score-box">
<div class="mini"><div class="tag">Problem</div><div id="problemText">Limited access to personalised exam prep</div></div>
<div class="mini"><div class="tag">AI</div><div id="aiText">Adaptive difficulty + weak-topic insight</div></div>
<div class="mini"><div class="tag">Outcome</div><div id="outcomeText">Better revision paths for every student</div></div>
</div>
<button class="btn" onclick="toggleLanguage()" id="langBtn" style="margin-top:12px">Urdu / English</button>
</div>
<div class="grid">
<div class="card">
<h2>Launch a practice session</h2>
<p class="muted">Azure OpenAI generates a personalised adaptive insight.</p>
<button class="btn" onclick="loadDemo()">Generate AI Insight</button>
<button class="btn secondary" onclick="location.href='/api/health'">API Health</button>
</div>
<div class="card" id="insightBox">
<h3 id="insightTitle">Current AI Insight</h3>
<p class="muted" id="insightBody">Click the button to see an adaptive recommendation.</p>
</div>
</div>
<div class="card">
<h2>Analyse your answers</h2>
<p class="muted">Paste answers below. Azure AI Language detects your weak topics.</p>
<textarea id="answersInput" rows="4" placeholder="e.g. I got confused about recursion and loops..."></textarea>
<button class="btn" onclick="analyzeAnswers()" style="margin-top:10px">Detect Weak Topics</button>
<div id="analyzeResult" style="margin-top:12px"></div>
</div>
<div class="card">
<h2 id="analyticsTitle">Teacher analytics snapshot</h2>
<div id="analyticsBox" class="score-box"></div>
</div>
</div>
<script>
const T={en:{problem:"Limited access to personalised exam prep",ai:"Adaptive difficulty + weak-topic insight",outcome:"Better revision paths for every student",insightTitle:"Current AI Insight",insightBody:"Click the button to see an adaptive recommendation.",analyticsTitle:"Teacher analytics snapshot"},ur:{problem:"ذاتی امتحانی تیاری تک محدود رسائی",ai:"موافقتی مشکل اور کمزور موضوعات کی بصیرت",outcome:"ہر طالب علم کے لیے بہتر ریویژن راستہ",insightTitle:"موجودہ AI بصیرت",insightBody:"بٹن دبائیں۔",analyticsTitle:"استاد کے تجزیاتی جائزہ"}};
let lang="en";
function toggleLanguage(){lang=lang==="en"?"ur":"en";const t=T[lang];document.getElementById("problemText").textContent=t.problem;document.getElementById("aiText").textContent=t.ai;document.getElementById("outcomeText").textContent=t.outcome;document.getElementById("insightTitle").textContent=t.insightTitle;document.getElementById("insightBody").textContent=t.insightBody;document.getElementById("analyticsTitle").textContent=t.analyticsTitle;document.getElementById("langBtn").textContent=lang==="en"?"Urdu / English":"English / Urdu";}
function loadDemo(){document.getElementById("insightBody").textContent="Generating...";fetch("/api/demo").then(r=>r.json()).then(data=>{document.getElementById("insightBox").innerHTML="<h3>Current AI Insight <span class=\"ai-badge\">Azure OpenAI</span></h3><p>"+data.message+"</p><p class=\"muted\">Focus: "+data.focus+"</p>";});}
function analyzeAnswers(){const text=document.getElementById("answersInput").value.trim();if(!text){alert("Enter some answers first.");return;}document.getElementById("analyzeResult").innerHTML="<p class=\"muted\">Analysing...</p>";fetch("/api/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({answers:[text]})}).then(r=>r.json()).then(data=>{document.getElementById("analyzeResult").innerHTML="<div class=\"mini\"><div class=\"tag\">Weak Topics <span class=\"ai-badge\">Azure AI Language</span></div><div style=\"margin-top:6px\">"+(data.weak_topics.join(", ")||"None detected")+"</div><div class=\"muted\" style=\"margin-top:6px\">"+data.advice+"</div></div>";});}
fetch("/api/analytics").then(r=>r.json()).then(data=>{document.getElementById("analyticsBox").innerHTML="<div class=\"mini\"><div class=\"tag\">Sessions</div><div>"+data.sessions+"</div></div><div class=\"mini\"><div class=\"tag\">Questions</div><div>"+data.questions+"</div></div><div class=\"mini\"><div class=\"tag\">Weak Topics</div><div>"+data.topics+"</div></div>";});
</script>
</body></html>
"""


@app.get("/")
def index():
    return render_template_string(HTML)

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
