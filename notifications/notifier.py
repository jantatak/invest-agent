import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

# 📲 Telegram konfigurace
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 📧 Email konfigurace
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

def send_telegram_message(message):
    print("📬 Odesílám zprávu na Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Telegram zpráva úspěšně odeslána.")
            return True
        else:
            print(f"❌ Chyba při odesílání na Telegram: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Výjimka při odesílání na Telegram: {e}")
        return False

def send_telegram_document(file_path, caption="📄 Zde je tvůj log soubor:"):
    print("📬 Odesílám log soubor na Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as file:
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption
            }
            files = {
                "document": file
            }
            response = requests.post(url, data=payload, files=files)
        if response.status_code == 200:
            print("✅ Log soubor úspěšně odeslán na Telegram.")
            return True
        else:
            print(f"❌ Chyba při odesílání souboru: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Výjimka při odesílání souboru na Telegram: {e}")
        return False

def send_email(subject, message):
    recipients = [email.strip() for email in EMAIL_TO.split(',')]
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = ", ".join(recipients)

    try:
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, recipients, msg.as_string())
        print(f"✅ Email odeslán na: {', '.join(recipients)}")
        return True
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False

# ✅ Nová funkce pro odeslání e-mailu s přílohou
def send_email_with_attachment(subject, message, attachment_path):
    recipients = [email.strip() for email in EMAIL_TO.split(',')]
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = ", ".join(recipients)

    # Přidání textové části
    msg.attach(MIMEText(message, 'plain'))

    # Přidání přílohy
    try:
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(attachment_path)}",
        )
        msg.attach(part)
    except Exception as e:
        print(f"❌ Chyba při přidávání přílohy: {e}")
        return False

    # Odeslání e-mailu
    try:
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, recipients, msg.as_string())
        print(f"✅ Email s přílohou odeslán na: {', '.join(recipients)}")
        return True
    except Exception as e:
        print(f"❌ Email s přílohou error: {e}")
        return False
