# 🎓 Adaptive IT Learning Hub — Online Quiz System

A quiz and learning-support project developed to help students practice programming, computer science, and academic topics through interactive quizzes and performance feedback.

This repository contains two implementations:

- A **C++ terminal-based quiz application**
- A **Python Flask web-based quiz application**

## 📌 Project Overview

The Online Quiz System provides students with an interactive way to practice multiple-choice questions, check their performance, and identify topics that need further revision.

The project explores how programming fundamentals, file handling, web development, and AI services can be combined to support learning.

## ✨ Features

### C++ Terminal Quiz Application

- Student registration and login
- Admin login and management menu
- Multiple quiz categories
- Multiple-choice questions
- Score calculation and result display
- Student result history
- Recent performance chart
- Diagnostic feedback on incorrect answers
- Question hints
- Optional AI-generated hints and personalized study roadmap

### Flask Web Application

- Browser-based quiz interface
- Subject and difficulty selection
- Quiz questions with multiple-choice options
- Score calculation and feedback
- Urdu / English interface toggle
- Quiz generation through the Flask backend
- Answer analysis and study feedback
- Student account and dashboard API
- Analytics snapshot

## 📚 Quiz Categories

The C++ terminal version includes:

- Python Programming
- Mathematics
- Programming Basics
- Calculus
- English

The web interface includes practice quizzes for:

- Python
- Programming Basics
- Mathematics
- Data Structures

The web interface provides Beginner, Intermediate, and Advanced levels, with 10 questions in each displayed quiz.

## 🤖 AI Integration

The project includes optional AI integrations:

| Service | Purpose |
|---|---|
| Azure OpenAI | Generates quiz questions when configured |
| Azure AI Language | Extracts key phrases from submitted answers for analysis |
| Groq API | Supports AI-generated hints and study-roadmap features in the C++ application |

The web question generator includes fallback questions when Azure OpenAI is unavailable.

Some analysis and demo endpoints currently use fallback logic, so AI-based feedback may vary depending on the configured service and endpoint.

## 🛠️ Technologies Used

- C++
- Python
- Flask
- HTML
- CSS
- JavaScript
- Azure OpenAI
- Azure AI Language
- Groq API
- File-based data storage

## 🚀 Run the Flask Web Application

### Prerequisites

- Python 3
- pip
- Git

### 1. Clone the repository

```bash
git clone https://github.com/jk0409603-sys/Online-Quiz-System.git
cd Online-Quiz-System
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file using `.env.example` as a template.

Add your own Azure credentials if you want to use the Azure AI features.

Never upload API keys or passwords to GitHub.

### 5. Start the application

```bash
python app.py
```

Open your browser at:

```text
http://127.0.0.1:5000
```

## 🔑 Environment Variables

The web application can use the following environment variables:

```text
AZURE_OPENAI_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT=

AZURE_LANGUAGE_KEY=
AZURE_LANGUAGE_ENDPOINT=
```

The C++ application also supports:

```text
GROQ_API_KEY=
```

Use your own credentials locally. Do not include real keys in this README.

### C++ Admin Login Configuration

The C++ console application reads its admin credentials from `admin.conf` in the
repository root. Copy `admin.conf.example` to `admin.conf` and set a local
username and password. The example's active values are blank, so admin login
remains disabled until configured. `admin.conf` is ignored by Git. If the file
is missing or malformed, admin login is disabled while student features remain
available. Run the application from the repository root so it can find this
file and the quiz data.

## 📁 Project Structure

```text
Online-Quiz-System/
│
├── Code.cpp
├── app.py
├── app_flask.py
├── index.html
│
├── analysis.py
├── generate_questions.py
│
├── data/
│   └── questions_db.txt
│
├── static/
├── template/
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🔌 Flask API

The web backend includes endpoints for:

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Check application status |
| `/start` | POST | Generate quiz questions |
| `/answer` | POST | Evaluate submitted answers |
| `/api/signup` | POST | Register a student |
| `/api/login` | POST | Authenticate a student |
| `/api/dashboard` | GET | Retrieve student progress |
| `/api/analyze` | POST | Analyze submitted answers |
| `/api/study-plan` | POST | Generate study guidance |
| `/api/analytics` | GET | Retrieve analytics data |

## 🎯 Learning Outcomes

Through this project, I practiced:

- C++ object-oriented programming
- File handling and data management
- User authentication logic
- Quiz and scoring logic
- Python backend development
- Flask routes and JSON APIs
- HTML, CSS, and JavaScript integration
- Working with external AI APIs
- Debugging and project organization

## 👩‍💻 Developer

**Wajiha Imran**

BS Information Technology  
Bahauddin Zakariya University, Pakistan

Interested in software development, problem-solving, and building technology that supports education.

## 🌱 Future Improvements

- Improve the connection between the frontend and backend quiz APIs
- Strengthen authentication and password security
- Improve persistent student progress tracking
- Add more quiz categories and question banks
- Improve AI feedback and weak-topic recommendations
- Add automated tests and clearer setup instructions
