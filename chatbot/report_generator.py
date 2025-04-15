import matplotlib.pyplot as plt
import os
import requests
import json
from datetime import datetime

# Mistral AI API details
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_API_KEY = "mRu9GUqTjWOZa7eyuramuqkU20nDuk7U"  # Replace with your actual key

def fetch_mood_suggestions(mood):
    """
    Calls Mistral AI to get suggestions for uplifting the given mood.
    """
    prompt = f"Provide 4 effective ways to uplift someone's mood if they are feeling {mood}."

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistral-medium",
        "messages": [{"role": "system", "content": "You are an expert mental health therapist."},
                     {"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post(MISTRAL_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        suggestions = result["choices"][0]["message"]["content"].split("\n")
        return [s.strip() for s in suggestions if s.strip()]
    else:
        print(f"❌ Error fetching suggestions: {response.text}")
        return ["No suggestions available at the moment."]

def generate_overall_mood_report(conversation):
    """
    Generates an overall summary and visual mood analysis based on the conversation.
    """
    if not conversation:
        return "No conversation data available for analysis."

    # Ensure 'static' directory exists for saving files
    os.makedirs("static", exist_ok=True)

    # Extract conversation data
    moods = []
    user_texts = []

    for entry in conversation:
        mood = entry.get("emotion", "Neutral")
        text = entry.get("text", "Unknown message")

        moods.append(mood)
        user_texts.append(text)

    # 🔹 Determine Dominant Mood
    mood_counts = {mood: moods.count(mood) for mood in set(moods)}
    dominant_mood = max(mood_counts, key=mood_counts.get, default="Neutral")

    # 🔹 Generate a structured text report
    summary = "📜 **Overall Mood Analysis Report**\n\n"
    summary += f"🕒 **Session Date & Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    summary += f"💬 **Total Messages Exchanged:** {len(conversation)}\n\n"

    summary += f"🎭 **Dominant Mood:** {dominant_mood}\n\n"

    summary += "## **Mood Breakdown:**\n"
    for mood, count in mood_counts.items():
        summary += f"🔹 **{mood}** appeared frequently in the conversation.\n"

    # Fetch uplifting suggestions based on the dominant mood
    summary += "\n✨ **Suggestions to Improve Mood:**\n"
    suggestions = fetch_mood_suggestions(dominant_mood)
    for step in suggestions:
        summary += f"✔ {step}\n"

    # Save summary to a file
    report_path = "static/overall_chat_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"✅ Overall chat report saved as '{report_path}'")

    # 🔹 Generate Mood Trend Line Chart
    plt.figure(figsize=(10, 5))
    plt.plot(range(len(moods)), moods, marker='o', linestyle='-', color='b', label='Mood Trend')
    plt.xlabel("Conversation Step")
    plt.ylabel("Mood")
    plt.title("📈 Mood Changes Throughout Conversation")
    plt.legend()
    plt.grid(True)
    plt.savefig("static/mood_trend.png")
    print("📊 Mood trend chart saved as 'static/mood_trend.png'")

    # 🔹 Generate Mood Distribution Pie Chart
    plt.figure(figsize=(7, 7))
    plt.pie(mood_counts.values(), labels=mood_counts.keys(), autopct='%1.1f%%', startangle=140, 
            colors=['lightblue', 'lightcoral', 'gold', 'lightgreen'])
    plt.title("📊 Mood Distribution Over Conversation")
    plt.savefig("static/mood_distribution.png")
    print("📊 Mood distribution chart saved as 'static/mood_distribution.png'")

    return "Chat summary and mood charts have been successfully generated!"
