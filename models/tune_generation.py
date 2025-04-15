import json
import requests
import sys
import os

# Ensure Flask finds fal_client
sys.path.append(os.path.abspath("myenv/Lib/site-packages"))

import fal_client

# Set Fal.ai API Key
os.environ["FAL_KEY"] = "8cd74779-263d-408c-b570-9519d9ef9c6a:f3e53e5c191e04e7bb630939787743c4"

# Load the generated music prompt from 'static' folder
def load_music_prompt():
    json_path = "static/music_prompt.json"  # Updated path
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        return data.get("music_prompt", "Generate an ambient tune.")
    except FileNotFoundError:
        print(f"Error: {json_path} not found.")
        return "Generate an ambient tune."

# Callback function to handle queue updates
def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            print(log["message"])

# Generate tune using Fal.ai
def generate_tune():
    music_prompt = load_music_prompt()

    result = fal_client.subscribe(
        "fal-ai/stable-audio",
        arguments={
            "prompt": music_prompt,
            "seconds_total": 30,  # Duration of the audio clip
            "steps": 100          # Number of denoising steps
        },
        with_logs=True,
        on_queue_update=on_queue_update,
    )

    # The result contains the generated audio file information
    audio_file = result.get("audio_file", {})
    audio_url = audio_file.get("url", None)

    if audio_url:
        print(f"🎵 Generated Tune URL: {audio_url}")
        
        # Ensure 'static' directory exists
        os.makedirs("static", exist_ok=True)

        # Download and save the audio file in 'static' folder
        audio_path = "static/generated_tune.wav"  # Updated path
        audio_response = requests.get(audio_url)
        if audio_response.status_code == 200:
            with open(audio_path, "wb") as f:
                f.write(audio_response.content)
            print(f"✅ Tune saved as '{audio_path}'")
        else:
            print("Error downloading the generated audio.")
    else:
        print("Error: No audio URL found in the result.")

# Run tune generation
if __name__ == "__main__":
    generate_tune()
