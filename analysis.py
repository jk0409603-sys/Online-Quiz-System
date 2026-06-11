import os

from dotenv import load_dotenv
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential


load_dotenv()


def analyze_answers(answers):
    endpoint = os.getenv("AZURE_LANGUAGE_ENDPOINT", "").strip()
    key = os.getenv("AZURE_LANGUAGE_KEY", "").strip()
    if not endpoint or not key:
        return "You seem to struggle with: setup"

    client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    text = " ".join(answers)
    phrases = client.extract_key_phrases([text])[0]
    topics = [p for p in phrases if p]
    if topics:
        return f"You seem to struggle with: {topics[0]}"
    return "You seem to struggle with: general review"
