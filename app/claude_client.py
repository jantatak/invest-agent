import os
import requests
from dotenv import load_dotenv

# Načteme .env soubor
load_dotenv()

# Načteme CLAUDE_API_KEY
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

# Funkce pro odeslání promptu do Claude
def ask_claude(prompt, model="claude-3-haiku-20240307", max_tokens=3000):
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    data = {
        "model": model,
        "max_tokens": 3000,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(CLAUDE_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()['content'][0]['text']
    else:
        return f"❌ Chyba: {response.status_code} - {response.text}"

# Interaktivní promptování do Claude
def interactive_prompt():
    print("Zadej svůj prompt pro Claude (nebo napiš 'exit' pro ukončení):")
    while True:
        user_input = input("Tvoje otázka: ")
        if user_input.lower() == 'exit':
            print("Ukončuji...")
            break
        else:
            print("\n📨 Odesílám do Claude...")
            response = ask_claude(user_input)
            print(f"\n🤖 Claude odpověděl:\n{response}")

if __name__ == "__main__":
    interactive_prompt()
