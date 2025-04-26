
from notifications.notifier import send_telegram_message, send_email

if __name__ == "__main__":
    message = "✅ Test notifikace z Investičního Agenta!\nRozhodnutí: BUY TSLA @ 170 USD"
    
    print("Posílám Telegram zprávu...")
    if send_telegram_message(message):
        print("Telegram OK ✅")
    else:
        print("Telegram FAILED ❌")
    
    print("Posílám Email...")
    if send_email("Investiční Agent - TEST", message):
        print("Email OK ✅")
    else:
        print("Email FAILED ❌")
