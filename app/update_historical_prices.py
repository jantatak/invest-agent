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
    existing_data = None

    if os.path.exists(file_path):
        try:
            existing_data = pd.read_csv(file_path, parse_dates=['Date'])
            print(f"📄 Načteno {len(existing_data)} řádků ze souboru {file_path}")
            last_date = pd.to_datetime(existing_data['Date'].max())
            if pd.isna(last_date):
                raise ValueError("Neplatné datum v CSV")
            start_date = last_date.date() + timedelta(days=1)
            print(f"🔄 Aktualizuji {ticker} od {start_date} (poslední v CSV: {last_date.date()})")
        except Exception as e:
            print(f"⚠️ Chyba při načítání {file_path}: {e}")
            existing_data = None
            start_date = (datetime.today() - timedelta(days=365 * 50)).date()
    else:
        print(f"📄 Soubor {file_path} neexistuje, stahuji kompletní historii")
        start_date = (datetime.today() - timedelta(days=365 * 50)).date()

    end_date = (datetime.today() + timedelta(days=1)).date()
    print(f"📅 {ticker} – Stahuji od {start_date} do {end_date}")

    if start_date >= end_date:
        print(f"✅ {ticker} je aktuální. Žádná nová data.\n")
        return

    df_new = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if df_new.empty:
        print(f"⚠️ Žádná nová data pro {ticker}.")
        not_updated_tickers.append(ticker)
        return

    df_new.reset_index(inplace=True)
    df_new.rename(columns={df_new.columns[0]: "Date"}, inplace=True)

    newest_new = pd.to_datetime(df_new["Date"].max()).date()
    print(f"📈 Nová data pro {ticker}: {len(df_new)} řádků (nejnovější: {newest_new})")

    if existing_data is not None:
        before = len(existing_data)
        combined = pd.concat([existing_data, df_new], ignore_index=True)
        combined = combined.drop_duplicates(subset="Date").sort_values("Date")
        removed = before + len(df_new) - len(combined)
        print(f"🧹 Odstraněno {removed} duplicitních řádků.")
    else:
        combined = df_new

    try:
        combined.to_csv(file_path, index=False)
        newest = pd.to_datetime(combined["Date"].max()).date()
        print(f"✅ Data pro {ticker} uložena. Poslední datum: {newest}")

        if newest < datetime.today().date():
            print(f"ℹ️ Upozornění: Data končí {newest} – nejsou aktuální.")
            not_updated_tickers.append(ticker)
        else:
            print(f"✅ {ticker} je aktuální.")

    except PermissionError:
        print(f"❌ Nelze zapsat do souboru {file_path} – soubor je pravděpodobně otevřený.")
        not_updated_tickers.append(ticker)

def main(tickers):
    start_time = datetime.now()
    print(f"🧪 TEST: Spouštím aktualizaci pro tickery: {', '.join(tickers)}")

    for ticker in tickers:
        update_prices(ticker)

    if not_updated_tickers:
        print(f"⚠️ Tickery bez aktuálních dat: {', '.join(not_updated_tickers)}")
    else:
        print("✅ Všechna data jsou aktuální.")

    duration = datetime.now() - start_time
    print(f"🏁 Hotovo za {duration.seconds} sekund.")

if __name__ == "__main__":
    print("🧪 VERZE skriptu: 2025-05-01 ✅")
    try:
        from app.config_assets import ASSETS_TO_WATCH
        tickers = ASSETS_TO_WATCH["etf"] + ASSETS_TO_WATCH["stocks"]
        main(tickers)
    except Exception as e:
        print("⚠️ Tento skript očekává seznam tickerů jako argument.")
        print(f"❌ Chyba: {e}")
