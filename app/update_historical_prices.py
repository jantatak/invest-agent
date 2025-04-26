import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(BASE_DIR, "data", "prices")
LOG_FOLDER = os.path.join(BASE_DIR, "logs")
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

LOG_FILE = os.path.join(LOG_FOLDER, "price_update_log.txt")
not_updated_tickers = []

def write_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def update_prices(ticker):
    file_path = os.path.join(DATA_FOLDER, f"{ticker}.csv")

    if os.path.exists(file_path):
        existing_data = pd.read_csv(file_path, parse_dates=['Date'])
        try:
            last_date = pd.to_datetime(existing_data['Date'].max())
            if pd.isna(last_date):
                raise ValueError("Neplatné datum")
            start_date = last_date + timedelta(days=1)
            print(f"🔄 Aktualizuji {ticker} od {start_date.date()}")
        except Exception as e:
            print(f"⚠️ Problém s datem v {ticker} ({e}). Stahuji kompletní data.")
            write_log(f"{ticker}: Problém s datem ({e}). Stahuji kompletní data.")
            existing_data = None
            start_date = datetime.today() - timedelta(days=365 * 50)
    else:
        existing_data = None
        start_date = datetime.today() - timedelta(days=365 * 50)
        print(f"📥 Stahuji kompletní data pro {ticker} (50 let)")
        write_log(f"{ticker}: Stahuji kompletní data (50 let)")

    end_date = datetime.today()

    if start_date >= end_date:
        print(f"✅ {ticker} je aktuální. Žádná nová data.\n")
        write_log(f"{ticker}: Žádná nová data, již aktuální.")
        return

    df_new = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), progress=False)

    if df_new.empty:
        print(f"⚠️ Žádná nová data pro {ticker}. Možná nejsou dostupná.\n")
        write_log(f"{ticker}: Žádná nová data – pravděpodobně ještě nejsou dostupná.")
        not_updated_tickers.append(ticker)
        return

    df_new.reset_index(inplace=True)
    df_new.rename(columns={df_new.columns[0]: 'Date'}, inplace=True)

    if existing_data is None:
        full_data = df_new
    else:
        full_data = pd.concat([existing_data, df_new], ignore_index=True)
        full_data = full_data.drop_duplicates(subset=['Date']).sort_values('Date')

    try:
        full_data.to_csv(file_path, index=False)
        oldest_date = full_data['Date'].min().date()
        newest_date = full_data['Date'].max().date()
        delta = newest_date - oldest_date
        years = delta.days // 365

        print(f"✅ Data pro {ticker} uložena/aktualizována.")
        print(f"🗓️ Historie pro {ticker}: {years} let ({delta.days} dní) od {oldest_date} do {newest_date}")

        write_log(f"{ticker}: Aktualizováno – {years} let ({delta.days} dní) od {oldest_date} do {newest_date}.")

        if newest_date < (datetime.today().date() - timedelta(days=1)):
            print(f"ℹ️ Upozornění: Poslední datum je {newest_date} – data NEJSOU aktuální.\n")
            write_log(f"{ticker}: Upozornění – data nejsou aktuální (poslední datum {newest_date}).")
            not_updated_tickers.append(ticker)
        else:
            print(f"✅ {ticker} je aktuální.\n")
            write_log(f"{ticker}: Data jsou aktuální.")

    except PermissionError:
        print(f"❌ Nelze zapsat do souboru {file_path} – soubor je otevřený!\n")
        write_log(f"{ticker}: Chyba – nelze zapsat do souboru (otevřený soubor).")

def main(tickers):
    start_time = datetime.now()
    write_log(f"🚀 Spuštění aktualizace pro {len(tickers)} tickerů.")

    for ticker in tickers:
        update_prices(ticker)

    if not_updated_tickers:
        msg = f"⚠️ Tickery bez aktuálních dat: {', '.join(not_updated_tickers)}"
        print(msg)
        write_log(msg)
    else:
        print("✅ Všechna data jsou aktuální.")
        write_log("✅ Všechna data jsou aktuální.")

    duration = datetime.now() - start_time
    write_log(f"🏁 Aktualizace dokončena za {duration.seconds} sekund.\n{'-'*50}\n")

if __name__ == "__main__":
    print("⚠️ Tento skript očekává seznam tickerů jako argument.")
