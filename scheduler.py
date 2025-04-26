from apscheduler.schedulers.background import BackgroundScheduler
from app.agent import run_investment_agent
import datetime
import threading

def scheduled_task():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n⏰ [AUTO] Spouštím Investičního Agenta ({now})")
    run_investment_agent()

def manual_trigger():
    while True:
        command = input("💻 Napiš 'run' nebo zmáčkni ENTER pro ruční spuštění agenta:\n")
        if command.strip() == "" or command.strip().lower() == "run":
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n⚡ [MANUAL] Ruční spuštění Agenta ({now})")
            run_investment_agent()

if __name__ == "__main__":
    scheduler = BackgroundScheduler()

    scheduler.add_job(scheduled_task, 'cron', hour=9, minute=0)
    scheduler.add_job(scheduled_task, 'cron', hour=15, minute=0)

    scheduler.start()
    print("🕒 Scheduler běží... (plán: 9:00 a 15:00 každý den)")

    now = datetime.datetime.now()
    if now.hour >= 15:
        print("⚡ PC spuštěno po 15:00 – spouštím Agenta ihned.")
        scheduled_task()

    # Spustíme posluchače na manuální příkazy
    threading.Thread(target=manual_trigger, daemon=True).start()

    # Udržíme hlavní vlákno živé
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler ukončen.")
