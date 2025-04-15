import requests

MISTRAL_API_KEY = "mRu9GUqTjWOZa7eyuramuqkU20nDuk7U"
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

def analyze_emotion(text):
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistral-medium",
        "messages": [
            {"role": "system", "content": "You are an AI that detects emotions from user messages."},
            {"role": "user", "content": f"Analyze the emotion of this text: {text}"}
        ],
        "max_tokens": 10
    }

    response = requests.post(MISTRAL_API_URL, json=data, headers=headers)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return "neutral"
