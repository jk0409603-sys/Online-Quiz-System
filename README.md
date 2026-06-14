# 🎓 Adaptive IT Learning Hub — Online Quiz System

> **Microsoft Hackathon 2026 Submission**  
> Built by **Wajiha Imran** · Bahauddin Zakariya University · BS IT 1st Year (Completed) · GPA 4.0  
> 🏆 Built solo in just **4 days**

🌐 **Live Demo:** [https://online-quiz-system-jr8q.onrender.com](https://online-quiz-system-jr8q.onrender.com)

---

## 📸 Screenshots

###LOGIN page
![LOGIN page](docs/images/![alt text](<Screenshot 2026-06-14 114251.png>))

### Main Dashboard
![Main Dashboard](docs/images/![alt text](<Screenshot 2026-06-14 114315.png>))

### Quiz Section — Choose Subject & Level
![Quiz Section](docs/images/![alt text](<Screenshot 2026-06-14 114334.png>))

### Analyse Your Answers — AI Weak Topic Detection
![Analyse Answers](docs/images/![alt text](<Screenshot 2026-06-14 114354.png>))

---

## DEMO 

![demo](https://<video controls src="bandicam 2026-06-14 11-34-23-339.mp4" title="Title"></video>))



## 🚩 The Problem

Students in Pakistan — especially in smaller cities — have **no access to personalised exam prep**. Coaching is expensive, and generic quizzes don't tell you *what* to fix. This project solves that.

---

## 💡 The Solution

**Adaptive IT Learning Hub** is an AI-powered quiz platform that:
- 🧠 Generates **personalised study recommendations** using Azure OpenAI
- 🔍 Detects **weak topics** from student answers using Azure AI Language
- 📝 Offers **4 subjects × 3 difficulty levels × 10 questions** each
- 🌐 Supports **Urdu and English** so no student is left behind
- 📊 Shows **teacher analytics** — sessions, questions, weak topic patterns

---

## 🤖 Microsoft Azure AI Integration

| Service | How it's used |
|---|---|
| **Azure OpenAI (gpt-4o-mini)** | Generates adaptive study insights personalised per student |
| **Azure AI Language** | Extracts key phrases from answers to detect weak topics |

---

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat-square&logo=flask)
![Azure OpenAI](https://img.shields.io/badge/Azure_OpenAI-gpt--4o--mini-0078d4?style=flat-square&logo=microsoftazure)
![Azure AI Language](https://img.shields.io/badge/Azure_AI-Language-0078d4?style=flat-square&logo=microsoftazure)
![C++](https://img.shields.io/badge/C++-Core_Engine-00599C?style=flat-square&logo=cplusplus)
![Render](https://img.shields.io/badge/Deployed-Render-46E3B7?style=flat-square&logo=render)

---

## ✨ Features

- 🧠 **AI-generated adaptive insights** — tells students exactly what to revise
- 🔍 **Weak topic detection** — paste your answers, get instant AI feedback
- 📝 **Quiz system** — 4 subjects, 3 difficulty levels, 10 questions each
  - Python (Beginner / Intermediate / Advanced)
  - Programming Basics (Beginner / Intermediate / Advanced)
  - Mathematics (Beginner / Intermediate / Advanced)
  - Data Structures (Beginner / Intermediate / Advanced)
- 📊 **Teacher analytics dashboard** — sessions, questions, top weak topics
- 🌐 **Urdu / English toggle** — full bilingual UI
- ⚡ **Fallback mode** — works even without API keys (no crashes)
- 📁 **C++ quiz engine** — core logic built from scratch

---

## 🚀 Setup & Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/jk0409603-sys/Online-Quiz-System.git
cd Online-Quiz-System

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env
# Add your Azure keys to .env

# 4. Run the app
python app.py

# 5. Open in browser
http://localhost:5000
```

---

## 🔑 Environment Variables

Create a `.env` file in the root directory:

```env
AZURE_OPENAI_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_LANGUAGE_KEY=your_key_here
AZURE_LANGUAGE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
```

> ⚠️ Never commit your `.env` file. It is already in `.gitignore`.

---

## 📁 Project Structure

```
Online-Quiz-System/
├── app.py                  # Flask app + Azure AI routes + Quiz system
├── generate_questions.py   # Question generator
├── Code.cpp                # Core C++ quiz engine
├── data/                   # Question bank
├── docs/images/            # Screenshots
├── history.txt             # Session history
├── results.txt             # Quiz results
├── requirements.txt        # Python dependencies
└── README.md
```

---

## 🧪 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Main UI with quiz system |
| `/api/health` | GET | Check Azure connection status |
| `/api/demo` | GET | Get AI-generated adaptive insight |
| `/api/analyze` | POST | Detect weak topics from answers |
| `/api/analytics` | GET | Teacher analytics snapshot |

---

## 👩‍💻 About the Developer

**Wajiha Imran**  
BS Information Technology — 1st Year (Completed)  
Bahauddin Zakariya University, Pakistan  

- 🏆 GPA 4.0 in OOP and C++ (First Year) | know javascript very well | learning pyton |
- 💻 Built this entire project solo in just **4 days**
- 🎯 Passionate about using AI to make education accessible in Pakistan

---

## 🎯 Impact

> *"Every student in Pakistan deserves personalised learning — not just those who can afford coaching."*

This tool is built for the **millions of IT students** across Pakistan who prepare for exams without guidance, without mentors, and without feedback on what they're actually getting wrong.

---

## 📄 License

MIT License — free to use, build on, and share.
