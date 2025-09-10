import os
import requests
from datetime import datetime

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    print("[DEBUG] No OPENROUTER_API_KEY found → will use fallback tips only.")

def debug_log(msg):
    print(f"[DEBUG {datetime.now().strftime('%H:%M:%S')}] {msg}")

def build_coaching_prompt(user_data):
    if "follow_up_question" in user_data:
        return f"""
You are an empathetic corporate wellness coach continuing a conversation.

Previous Analysis:
- Burnout Score: {user_data['burn_rate']:.2f}
- Risk Category: {user_data['risk_category']}

User's follow-up question: {user_data['follow_up_question']}

Provide a helpful, concise response (under 150 words) addressing their specific question.
"""

    return f"""
You are an empathetic and highly knowledgeable corporate wellness coach. Your goal is to provide actionable advice.
Employee's Data:
- Designation Level: {user_data['Designation']}
- Resource Allocation: {user_data['Resource Allocation']}
- Mental Fatigue Score: {user_data['Mental Fatigue Score']:.1f}
- Days Since Joining: {user_data['Days_Since_Joining']}
- Company Type: {user_data['Company Type']}
- WFH Setup: {user_data['WFH Setup Available']}

Analysis Result:
- Predicted Burnout Score: {user_data['burn_rate']:.2f}
- Burnout Risk Category: {user_data['risk_category']}

Write a concise, encouraging coaching plan (<200 words) structured as:
1. Acknowledge & validate
2. Actionable steps
3. Positive outlook

act like you are chatting with the employee and you know them do not add placeholders for names or anything i want the conversation to be as natrual anf humane as possible
"""

def get_fallback_tips(risk_category):
    if risk_category == "High":
        return [
            "You're under significant pressure; prioritize your well-being.",
            "Speak with your manager about workload.",
            "Schedule a short break or vacation to recharge.",
            "Seeking support from HR or a professional is a strength."
        ]
    if risk_category == "Moderate":
        return [
            "Manageable but busy; keep balance.",
            "Try the Pomodoro Technique for focus.",
            "Review tasks for delegation or postponement.",
            "Protect personal time after hours."
        ]
    return [
        "You're proactively checking in on well-being!",
        "Maintain your good habits.",
        "Incorporate mindfulness or meditation.",
        "Monitor workload to stay healthy."
    ]

def get_wellness_advice(user_data):
    if not API_KEY:
        debug_log("No OpenRouter API key found → using fallback tips")
        return "* " + "\n* ".join(get_fallback_tips(user_data["risk_category"]))

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Burnout Coach",
    }
    prompt = build_coaching_prompt(user_data)
    messages = [
        {"role": "system", "content": "You are a mental health and wellness expert."},
        {"role": "user", "content": prompt}
    ]

    model_names = [
        "mistralai/mistral-7b-instruct:free"
    ]

    for model_name in model_names:
        data = {
            "model": model_name,
            "messages": messages,
            "max_tokens": 300,
            "temperature": 0.7
        }
        try:
            debug_log(f"Sending request to OpenRouter API with model: {model_name}...")
            response = requests.post(url, headers=headers, json=data, timeout=20)
            response.raise_for_status()
            
            result = response.json()
            text = result["choices"][0]["message"]["content"].strip()
            debug_log(f"Success with model: {model_name}")
            return text

        except requests.exceptions.RequestException as e:
            debug_log(f"API call with model {model_name} failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                debug_log(f"Response body: {e.response.text}")
            continue  # Try the next model in the list

    # If all models fail, use fallback tips
    debug_log("All API models failed → using fallback tips")
    return "* " + "\n* ".join(get_fallback_tips(user_data["risk_category"]))
