# Investiční Agent

Projekt pro automatického investičního agenta napojeného na Claude API, který denně analyzuje trhy, sleduje vybraná aktiva, získává aktuální novinky a generuje investiční doporučení.

---

## 📂 Struktura projektu

```
Invest agent/
├── app/
│   ├── __init__.py                    # Inicializace balíčku
│   ├── agent.py                       # Hlavní logika investičního agenta
│   ├── best_buy_days.py               # Výpočet "nejlepších nákupních dnů"
│   ├── best_days_summary.py           # Shrnutí/statistiky k nejlepším dnům
│   ├── claude_client.py               # Klient pro komunikaci s Claude API
│   ├── claude_analysis.py             # Analýza trhů + doporučení přes Claude
│   ├── config_assets.py               # Konfigurace sledovaných ETF a akcií
│   ├── daily_analysis.py              # Denní analýzy trhu nebo portfolia
│   ├── decision_engine.py             # Logika rozhodování BUY/SELL/HOLD
│   ├── generate_statistics.py         # Generování statistik z dat
│   ├── investment_calendar_analysis.py# Analýza sezónnosti a kalendářních vzorců
│   ├── market_data.py                 # Práce s tržními daty
│   ├── prepare_data_structure.py      # Příprava datové struktury
│   └── update_historical_prices.py    # Stahování a aktualizace historických dat
│
├── data/
│   ├── prices/                         # Historická denní data tickerů
│   ├── best_buy_months_summary/        # Shrnutí nejlevnějších měsíců
│   └── extended_monthly_summaries/     # Detailní měsíční statistiky (Avg, Min, Max)
├── logs/                               # Uložené denní reporty z Claude
│
├── notifications/
│   └── notifier.py                    # Odesílání zpráv (Telegram, Email)
│
├── scheduler.py                       # Hlavní plánovač denních úloh
├── .env                               # API klíč pro Claude
└── requirements.txt                   # Seznam knihoven
```

---

## 🚀 Funkcionalita

- **Automatická aktualizace dat** z Yahoo Finance.
- Výpočet nejvhodnějších dnů pro nákup aktiv.
- Získání **aktuálních zpráv z trhů** (RSS).
- Analýza trhů a generování doporučení (BUY/HOLD/SELL) přes **Claude API**.
- Ukládání denních reportů do složky `logs`.
- Odesílání notifikací přes Telegram a Email.
- Generování statistik a kalendářních analýz.
- Logika rozhodování na základě dat a strategií.

---

## ⚙️ Spuštění projektu

1. Aktivace virtuálního prostředí:
```bash
cd "C:\Users\janta\Projects\Invest agent"
.\.venv\Scripts\activate
```

2. Instalace knihoven:
```bash
pip install -r requirements.txt
```

3. Spuštění denního scheduleru:
```bash
python scheduler.py
```

> Scheduler automaticky provede update dat, analýzu a odešle report.

---

## 📅 Denní workflow

1. **Update dat** (`update_historical_prices.py`).
2. **Analýza nejlepších dnů** (`best_buy_days.py`).
3. **Claude analýza** s aktuálními tržními zprávami.
4. **Decision engine** – zhodnocení strategie.
5. Uložení výsledků + odeslání notifikace.

---

## 🔮 Možnosti rozšíření

- [ ] Přidat pokročilé analytické nástroje (RSI, MA, volatilita).
- [ ] Automatické posílání logu jako přílohy do Telegramu.
- [ ] Webový dashboard pro vizualizaci dat.
- [ ] Pokročilé sledování strategie a vývoje portfolia.
- [ ] Docker kontejner pro snadnější nasazení.

---

## 🔐 .env soubor

Obsahuje citlivé údaje, např. API klíč pro Claude:
```
CLAUDE_API_KEY=tvuj_api_klic
```

---

## 📞 Kontakt

Pro interní potřeby uživatele. V případě rozšíření projektu přidat sekci s dokumentací API a dalšími instrukcemi.

