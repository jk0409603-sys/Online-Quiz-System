# Online Quiz System

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-green.svg)](https://flask.palletsprojects.com/)
[![Azure OpenAI](https://img.shields.io/badge/Azure%20OpenAI-Enabled-0078D4.svg)](https://azure.microsoft.com/products/ai-services/openai-service/)
[![Azure AI Language](https://img.shields.io/badge/Azure%20AI%20Language-Enabled-0078D4.svg)](https://azure.microsoft.com/products/ai-services/text-analytics/)

A hackathon-ready quiz platform that uses Azure OpenAI to generate personalized multiple-choice questions and Azure AI Language to identify weak topics from student answers.

## Problem Statement
Students often study without personalized guidance, which makes exam prep inefficient and discouraging. This project addresses that gap with AI-generated quizzes and feedback tailored to each learner.

## Features
- AI-generated quizzes on any topic
- Three difficulty levels with 5 rounds and 10 questions per round
- Instant answer analysis with weak-topic suggestions
- Simple HTML front end and Flask API wrapper
- Easy Azure deployment

## Tech Stack
- Python + Flask
- Azure OpenAI
- Azure AI Language
- HTML/CSS/JavaScript

## Setup
1. Create a virtual environment and install dependencies:
   pip install -r requirements.txt
2. Copy the sample environment file and fill in your Azure credentials:
   cp .env.example .env
3. Run the app:
   python app_flask.py

## Environment Variables
- AZURE_OPENAI_ENDPOINT
- AZURE_OPENAI_KEY
- AZURE_OPENAI_DEPLOYMENT
- AZURE_LANGUAGE_ENDPOINT
- AZURE_LANGUAGE_KEY

## Screenshot Placeholder
![Demo Screenshot](https://via.placeholder.com/800x450?text=Online+Quiz+System)

## Live Demo
Coming soon: https://your-demo-link-here
