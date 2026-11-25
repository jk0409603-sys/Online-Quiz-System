# Online Quiz System – Adaptive IT Learning Hub

An educational quiz platform developed as a university project. The project began as a simple terminal-based quiz system in C++ and was gradually expanded with a Flask web application and AI-powered learning features.

The goal is to help students practice IT-related subjects, evaluate their performance, and identify areas that need improvement.

## Features

### C++ Terminal Application
- Student and administrator login
- Interactive quizzes
- Quiz score and result tracking
- Student performance history
- Hints and learning feedback

### Flask Web Application
- Browser-based quiz experience
- Subject and difficulty selection
- Score-based feedback
- Student dashboard and performance analytics
- API endpoints for application features

### AI-Based Learning Features
- AI-assisted question generation
- Answer analysis and learning feedback
- Study recommendations and learning support

Some AI features require valid Azure or other configured API credentials.

## Technologies Used

- **C++** – Quiz logic and terminal application
- **Python** – Backend and supporting modules
- **Flask** – Web application and API
- **HTML, CSS, JavaScript** – Web interface
- **Azure AI services** – AI-related features
- **Git and GitHub** – Version control

## Project Structure

```text
Online-Quiz-System/
│
├── Code.cpp
├── app.py
├── app_flask.py
├── analysis.py
├── generate_questions.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── data/
│   └── questions_db.txt
│
├── static/
├── templates/
└── README.md
```

*The structure above is a simplified overview. Update it to match the actual files and folders in the repository.*

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/jk0409603-sys/Online-Quiz-System.git
cd Online-Quiz-System
```

### 2. Run the C++ terminal application

Make sure a C++ compiler such as g++ is installed.

```bash
g++ Code.cpp -o quiz
```

Run the program:

**Windows:**
```bash
quiz.exe
```

**Linux / macOS:**
```bash
./quiz
```

### 3. Set up the Python web application

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file using `.env.example` as a template.

Example:

```env
AZURE_OPENAI_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

AZURE_LANGUAGE_KEY=your_key_here
AZURE_LANGUAGE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
```

Replace the placeholder values with your own Azure credentials if you want to use the AI features.

**Never upload real API keys, passwords, or private credentials to GitHub.**

### 5. Start the Flask application

Run the Python file that contains your Flask application entry point. For example:

```bash
python app.py
```

Then open the local address displayed in your terminal, usually:

```text
http://127.0.0.1:5000
```

If your Flask entry point is `app_flask.py`, use that filename instead.

## Learning Objectives

This project was developed to practice:

- C++ programming and object-oriented concepts
- Data handling and file operations
- Authentication and user management
- Python backend development
- Flask routes and API development
- Frontend and backend integration
- AI service integration
- Debugging, testing, and improving existing code

## Project Development

The project was initially created as a small terminal-based quiz application while learning programming with GitHub Copilot.

It was later expanded with additional features and a web-based interface. The project continues to evolve as part of my learning journey in software development and information technology.

## Security Note

This project is intended for educational and learning purposes. It is not yet intended for production use.

Authentication, password storage, API security, input validation, and deployment configuration should be reviewed and strengthened before using the application with real users or sensitive information.

## Future Improvements

- Improve authentication and password security
- Add stronger input validation and error handling
- Improve the user interface and accessibility
- Expand the quiz question database
- Add more personalized learning and analytics features
- Improve testing and deployment

## Author

Developed as a university learning project by a BS Information Technology student.

GitHub: [jk0409603-sys](https://github.com/jk0409603-sys)

---

*Built while learning, improved through practice, and continuously evolving.*
