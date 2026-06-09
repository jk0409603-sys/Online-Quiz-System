# 🚀 Online Quiz System

A high-performance, terminal-based quiz platform designed to deliver an engaging learning experience through fast gameplay, structured question banks, and real-time result tracking.

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

## 🏆 Why This Can Score 10/10

- Clear demo story: students answer, get AI help, and receive personalized feedback
- Strong technical depth: C++ OOP, file I/O, timers, AI API integration, and input safety
- Excellent presentation value: polished terminal UI, charts, and real-time feedback
- Practical real-world impact: learning support, revision planning, and performance tracking
- Easy to explain in a 3-minute demo: login → quiz → AI hint → roadmap → history chart

## 💡 Future Enhancements

- Add leaderboard support
- Introduce difficulty levels
- Add timed categories and random question pools
- Build a GUI version for desktop or web

## 📌 Summary

The Online Quiz System is a compact but powerful terminal application that showcases software engineering, interactive design, and educational technology in one complete package.
