import datetime
import os
import pandas as pd
from app import update_historical_prices
from app import best_buy_days
from app import best_days_summary
from app import best_months_summary
from app import claude_analysis
from app.config_assets import ASSETS_TO_WATCH
from notifications.notifier import send_telegram_message, send_email_with_attachment, send_telegram_document

def log_step(message):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {message}")

def clean_old_files(tickers, folders, patterns):
    log_step("🧹 Čistím staré soubory...")
    try:
        for folder, pattern in zip(folders, patterns):
            for filename in os.listdir(folder):
                match = False
                for ticker in tickers:
                    if pattern.format(ticker=ticker) == filename:
                        match = True
                        break
                if not match:
                    file_path = os.path.join(folder, filename)
                    os.remove(file_path)
                    log_step(f"🗑️ Smazán soubor: {file_path}")
    except Exception as e:
        log_step(f"❌ Chyba při čištění souborů: {e}")

def load_summary_overview(summary_folder):
    log_step("📥 Načítám souhrny nejlepších dnů...")
    summary_texts = []
    try:
        for filename in os.listdir(summary_folder):
            if filename.endswith("_day_summary.csv"):
                ticker = filename.replace("_day_summary.csv", "")
                df = pd.read_csv(os.path.join(summary_folder, filename))
                top_days = df.head(3)
                summary_texts.append(f"{ticker}: Nejčastější dny pro nákup:\n{top_days.to_string(index=False)}\n")
    except Exception as e:
        log_step(f"❌ Chyba při načítání dnů: {e}")
    return "\n".join(summary_texts)

def load_months_overview(months_folder):
    log_step("📥 Načítám souhrny nejlevnějších měsíců...")
    summary_texts = []
    try:
        for filename in os.listdir(months_folder):
            if filename.endswith("_month_summary.csv"):
                ticker = filename.replace("_month_summary.csv", "")
                df = pd.read_csv(os.path.join(months_folder, filename))
                top_months = df.head(3)
                summary_texts.append(f"{ticker}: Nejčastější měsíce:\n{top_months.to_string(index=False)}\n")
    except Exception as e:
        log_step(f"❌ Chyba při načítání měsíců: {e}")
    return "\n".join(summary_texts)

def load_lowest_days_last_year(folder):
    log_step("📥 Načítám nejnižší dny za poslední rok...")
    summary_texts = []
    try:
        for filename in os.listdir(folder):
            if filename.endswith("_lowest_days_last_1_years.csv"):
                ticker = filename.replace("_lowest_days_last_1_years.csv", "")
                df = pd.read_csv(os.path.join(folder, filename))
                summary_texts.append(f"{ticker}: Nejnižší dny:\n{df.to_string(index=False)}\n")
    except Exception as e:
        log_step(f"❌ Chyba při načítání nejnižších dnů: {e}")
    return "\n".join(summary_texts)

def run_investment_agent():
    log_step("🚀 Spuštění investičního agenta")

    tickers = ASSETS_TO_WATCH["etf"] + ASSETS_TO_WATCH["stocks"]

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prices_folder = os.path.join(BASE_DIR, "data", "prices")
    best_days_folder = os.path.join(BASE_DIR, "data", "best_buy_days")
    days_summary_folder = os.path.join(BASE_DIR, "data", "best_buy_days_summary")
    months_summary_folder = os.path.join(BASE_DIR, "data", "best_buy_months_summary")
    lowest_days_folder = os.path.join(BASE_DIR, "data", "best_buy_months_extended_summary")
    logs_folder = os.path.join(BASE_DIR, "logs")

    os.makedirs(logs_folder, exist_ok=True)

    try:
        clean_old_files(
            tickers,
            folders=[prices_folder, best_days_folder, days_summary_folder, months_summary_folder, lowest_days_folder],
            patterns=["{ticker}.csv", "{ticker}_best_days.csv", "{ticker}_day_summary.csv", "{ticker}_month_summary.csv", "{ticker}_lowest_days_last_1_years.csv"]
        )

        log_step("🔄 Aktualizace dat...")
        update_historical_prices.main(tickers)

        log_step("📊 Výpočet nejlepších dnů...")
        best_days_report = best_buy_days.main(tickers)

        log_step("📈 Souhrn dnů...")
        best_days_summary.main(tickers)

        log_step("🗓️ Souhrn měsíců...")
        best_months_summary.main(tickers)

        days_overview = load_summary_overview(days_summary_folder)
        months_overview = load_months_overview(months_summary_folder)
        lowest_days_last_year = load_lowest_days_last_year(lowest_days_folder)

        log_step("🤖 Spouštím Claude analýzu...")
        claude_report = claude_analysis.run_claude_analysis(extra_summary=days_overview + "\n" + months_overview)

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"📅 Report - {now}\n\n"
        message += f"✅ Nejlepší dny:\n{best_days_report}\n\n"
        message += f"📈 Dny k nákupu:\n{days_overview}\n"
        message += f"🗓️ Měsíce:\n{months_overview}\n"
        message += f"📉 Nejnižší dny:\n{lowest_days_last_year}\n"
        message += f"🤖 Claude:\n{claude_report}"

        log_filename = f"claude_report_{datetime.datetime.today().strftime('%Y-%m-%d')}.txt"
        log_path = os.path.join(logs_folder, log_filename)

        if send_email_with_attachment("Investiční Agent - Report", message, log_path):
            log_step("✅ Email s přílohou odeslán.")
        else:
            log_step("❌ Chyba při odesílání emailu.")

        telegram_msg = f"📊 Report vygenerován ({now})."
        send_telegram_message(telegram_msg.strip())
        send_telegram_document(log_path, caption="📄 Log soubor.")

        log_step("✅ Agent dokončil všechny úlohy.")

    except Exception as e:
        log_step(f"❌ Neočekávaná chyba: {e}")

if __name__ == "__main__":
    run_investment_agent()
