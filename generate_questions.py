import json
import os

from dotenv import load_dotenv
from openai import AzureOpenAI


load_dotenv()


def _azure_client():
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
    key = os.getenv("AZURE_OPENAI_KEY", "").strip()
    if not endpoint or not key:
        return None
    return AzureOpenAI(azure_endpoint=endpoint, api_key=key, api_version="2024-10-21")


def _fallback_questions(topic, level, count):
    templates = [
        ("What is the main idea of this topic?", ["Core concept", "Random fact", "A slogan", "A date"]),
        ("Which skill is most useful here?", ["Practice", "Guessing", "Skipping", "Hiding"]),
        ("What improves learning most?", ["Revision", "Ignoring notes", "Rushing", "Avoiding questions"]),
    ]
    return [
        {
            "question": f"{templates[(i + 1) % len(templates)][0]} ({topic}, {level})",
            "options": templates[(i + 1) % len(templates)][1],
            "answer": templates[(i + 1) % len(templates)][1][0],
            "difficulty": level,
        }
        for i in range(count)
    ]


def generate_quiz_questions(topic, level="Beginner", count=10):
    client = _azure_client()
    if client:
        try:
            prompt = (
                f"Create {count} multiple-choice quiz questions on '{topic}'. "
                f"Use level '{level}'. Return valid JSON as an array of objects with keys: "
                "question, options (4 strings), answer (the exact correct option text)."
            )
            response = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "You generate concise educational quiz JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.6,
            )
            text = response.choices[0].message.content or "[]"
            data = json.loads(text)
            if isinstance(data, list) and data:
                return [
                    {
                        "question": item.get("question", f"Question on {topic}"),
                        "options": item.get("options", ["A", "B", "C", "D"]),
                        "answer": item.get("answer", item.get("options", ["A"])[0]),
                        "difficulty": level,
                    }
                    for item in data[:count]
                ]
        except Exception:
            pass
    return _fallback_questions(topic, level, count)

