# 🚀 AI-Powered Online Quiz System

![Build Status](https://img.shields.io/badge/build-passing-brightgreen) ![C%2B%2B](https://img.shields.io/badge/C%2B%2B-17-blue) ![AI](https://img.shields.io/badge/AI-Groq%20Hint%2FRoadmap-orange)

A professional, terminal-based quiz platform that combines C++ logic, file-driven question banks, and AI-generated study guidance for a polished hackathon demo experience.

**One-line pitch:** "An AI-assisted quiz system that turns mistakes into personalized learning paths in real time."

---

## 1. Project Title

**AI-Powered Online Quiz System**

This project is designed as a live demo-ready learning assistant where students can answer quizzes, get AI-powered hints, and receive personalized study roadmaps based on weak topics and mistakes.

---

## 2. Core Agentic Architecture Diagram

```text
+-------------------+      +------------------------+      +-------------------+
| Student Input      | ---> | Quiz Engine / Timer    | ---> | Answer Evaluation  |
| (A/B/C/D, hint)   |      | Randomized Questions   |      | Correct/Wrong Logic|
+-------------------+      +------------------------+      +-------------------+
           |                              |                              |
           v                              v                              v
+-------------------+      +------------------------+      +-------------------+
| Diagnostic Agent   |      | Weak Topic Tracker     |      | AI Coach Layer     |
| Speed + Accuracy   |      | Error Categories       |      | Hint + Roadmap     |
+-------------------+      +------------------------+      +-------------------+
           \                               /                             /
            \-----------------------------------------------------------/
                                      |
                                      v
                          +------------------------------+
                          | Console Output + History Chart |
                          | Results, Roadmaps, Analytics   |
                          +------------------------------+
```

---

## 3. Features Matrix

| Feature | Description | Highlight |
|---|---|---|
| Randomization | Question order is shuffled for each session | ✅ Engaging replay value |
| File DB | Questions are loaded from `questions_db.txt` | ✅ Easy content expansion |
| Personalized Roadmaps | AI-generated guidance based on weak topics | ✅ Strong judge appeal |
| Timed Quizzes | 30-second rounds with real-time feedback | ✅ Competitive UX |
| Diagnostics | Tracks answer speed, incorrect patterns, and hint usage | ✅ Analytics-ready |

---

## 4. Video Demo Embedded Link


## ✨ Judge-Facing Showcase

### What makes the demo impressive
- The user answers in real time, gets an AI hint on demand, and receives a study roadmap from weak topics.
- The terminal UI feels polished, interactive, and demo-ready for live judging.
- The system combines education + AI + analytics in one compact C++ application.

### Demo Script (30 seconds)
1. Launch the app and show the login flow.
2. Start a quiz and type `hint` to demonstrate AI-assisted learning.
3. Finish the quiz and show the result + roadmap output.
4. Open the history chart to highlight user progress tracking.

---

## ✨ Why This Project Stands Out

This project combines:
- clean object-oriented C++ architecture
- dynamic question loading from a text database
- interactive timed quizzes
- AI-powered hints and personalized study roadmaps
- user authentication, result history, and score charts
- robust input validation for a stable demo experience
- a polished terminal interface suitable for live presentations

It is built to be simple to run, easy to extend, and impressive in live demonstrations.

## 🎯 Key Features

- Student login and admin access flow
- Multiple quiz categories:
  - Python Programming
  - Mathematics
  - Programming Basics
  - Calculus
  - English
- Dynamic quiz loading from `questions_db.txt`
- 30-second timed question rounds
- Score calculation, grading, and result persistence
- AI-generated hints for specific questions without revealing the answer
- AI-generated personalized study roadmaps from weak topics
- Past 5 quiz score chart for performance tracking
- Professional boxed terminal UI for a modern feel

## 🧱 Project Structure

- `Code.cpp` – Core application logic and quiz flow
- `questions_db.txt` – Dynamic question database
- `users.txt` – Registered user accounts
- `results.txt` – Quiz performance records
- `history.txt` – User score history and weak-topic tracking

## ⚙️ Quick Start

### 1. Compile
```bash
g++ -std=c++17 Code.cpp -o quiz_app -lssl -lcrypto -lz
```

### 2. Run
```bash
./quiz_app
```

## 🏆 Why Judges Like This Project

- Clear demo story: students answer, get AI help, and receive personalized feedback
- Strong technical depth: C++ OOP, file I/O, timers, AI API integration, and input safety
- Excellent presentation value: polished terminal UI, charts, and real-time feedback
- Practical real-world impact: learning support, revision planning, and performance tracking
- Easy to explain in a 3-minute demo: login → quiz → AI hint → roadmap → history chart

## 🎯 Problem We Solve

Many learners struggle not because they lack effort, but because they do not get immediate, personalized guidance after mistakes. This project solves that by turning quiz mistakes into actionable AI feedback and future study plans.

## 💡 Solution in One Line

An intelligent, interactive quiz app that helps students learn faster through instant AI hints, personalized roadmaps, and progress analytics.

## 📈 Impact

This project combines education, AI, and software engineering in one compact package, making it ideal for judges looking for novelty, usability, and real-world value.

## 💡 Future Enhancements

- Add leaderboard support
- Introduce difficulty levels
- Add timed categories and random question pools
- Build a GUI version for desktop or web

## 📌 Summary

The Online Quiz System is a compact but powerful terminal application that showcases software engineering, interactive design, and educational technology in one complete package.
