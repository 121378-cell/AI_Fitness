import subprocess
import os
from datetime import datetime

# Define the scripts to run daily
SCRIPTS = [
    "history_garmin_import.py",
    "daily_garmin_health.py",
    "daily_garmin_activities.py",
    "daily_hevy_workouts.py",
    "Gemini_Hevy.py"
]

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def run_script(script_name):
    """Run a script and log its output."""
    log_file = os.path.join(LOG_DIR, f"{script_name}_{datetime.now().strftime('%Y-%m-%d')}.log")
    with open(log_file, "w") as log:
        subprocess.run(["python", script_name], stdout=log, stderr=log)

if __name__ == "__main__":
    for script in SCRIPTS:
        print(f"Running {script}...")
        run_script(script)
    print("All daily scripts executed.")