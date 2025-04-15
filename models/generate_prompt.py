import json
import requests
import os

# Mistral AI API details
MISTRAL_API_KEY = "mRu9GUqTjWOZa7eyuramuqkU20nDuk7U"  # Replace with your actual API key
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"  # Correct API URL

# Load emotion and context from the JSON file in 'static' folder
def load_emotion_context():
    json_path = "static/emotion_context.json"  # Updated path
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        return data.get("emotion", "neutral"), ", ".join(data.get("context", []))  # Convert list to string
    except FileNotFoundError:
        print(f"Error: {json_path} not found. Make sure it exists.")
        return "neutral", "unknown background"

# Generate prompt using Mistral AI
def generate_prompt():
    detected_emotion, detected_context = load_emotion_context()

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }

    prompt_text = f"Generate a detailed music description based on the following:\n"\
                  f"Emotion: {detected_emotion}\n"\
                  f"Context: {detected_context}\n"\
                  f"Describe the music style, instruments, and mood."

    data = {
        "model": "mistral-medium",  # Ensure this model ID is correct
        "messages": [
            {"role": "system", "content": "You are an expert music composer."},
            {"role": "user", "content": prompt_text}
        ],
        "max_tokens": 100,
        "temperature": 0.7,
        "top_p": 0.9
    }

    response = requests.post(MISTRAL_API_URL, json=data, headers=headers)

    if response.status_code == 200:
        generated_text = response.json()["choices"][0]["message"]["content"]
        print("🎵 Generated Music Prompt:", generated_text)

        # Ensure 'static' directory exists
        os.makedirs("static", exist_ok=True)

        # Save to JSON file in 'static' folder
        output_data = {"music_prompt": generated_text}
        json_path = "static/music_prompt.json"  # Updated path
        with open(json_path, "w") as f:
            json.dump(output_data, f, indent=4)

        print(f"✅ Music prompt saved to '{json_path}'")
        return generated_text
    else:
        print("Error:", response.text)
        return None

# Run prompt generation
generate_prompt()
