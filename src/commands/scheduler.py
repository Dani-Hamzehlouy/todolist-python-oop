import time
from datetime import datetime

import schedule

from src.commands.autoclose_overdue import main as autoclose_main


def run_autoclose() -> None:
    """Runs the auto-close command and prints a timestamp."""
    autoclose_main()
    print(f"[{datetime.utcnow().isoformat()}] Auto-close job executed.")


def main() -> None:
    schedule.every(60).seconds.do(run_autoclose)
    print("Scheduler started. Running auto-close job every 60 seconds.")

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
