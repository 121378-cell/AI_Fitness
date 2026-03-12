import csv
import os
from datetime import datetime, timedelta

from src.database import sync_csv_to_table
from src.http_utils import HttpRequestError, request_json
from src.runtime_checks import enforce_mount_safety, load_runtime_config

config = load_runtime_config(default_save=os.getcwd())
enforce_mount_safety(config)

API_KEY = os.getenv("HEVY_API_KEY")
CSV_FILE = os.path.join(config.save_path, "hevy_stats.csv")


def main():
    if not API_KEY:
        print("CRITICAL ERROR: 'HEVY_API_KEY' not found. Please create a .env file.")
        return

    headers = {
        "api-key": API_KEY,
        "Accept": "application/json"
    }

    existing_sets = set()

    folder = os.path.dirname(CSV_FILE)
    if folder and not os.path.exists(folder):
        try:
            os.makedirs(folder)
            print(f"Created directory: {folder}")
        except OSError:
            pass

    if os.path.isfile(CSV_FILE):
        try:
            with open(CSV_FILE, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if len(row) > 3:
                        signature = f"{row[0]}_{row[1]}_{row[2]}_{row[3]}"
                        existing_sets.add(signature)
        except Exception as e:
            print(f"Warning reading file: {e}")

    cutoff_date = datetime.now() - timedelta(days=2)
    print(f"Checking Hevy for workouts since {cutoff_date.date()}...")

    try:
        data = request_json(
            "GET",
            "https://api.hevyapp.com/v1/workouts",
            headers=headers,
            params={"page": 1, "pageSize": 10},
            timeout_s=20,
            retries=3,
        )

        workouts = data.get('workouts', [])

        if not workouts:
            print("No workouts found.")
            return

        new_rows = []
        skipped_count = 0

        for workout in workouts:
            w_date_str = workout.get('start_time')
            if not w_date_str:
                continue

            w_dt = datetime.fromisoformat(w_date_str).astimezone().replace(tzinfo=None)
            if w_dt < cutoff_date:
                continue

            w_date_clean = w_dt.strftime("%Y-%m-%d")
            w_title = workout.get('title', 'Unknown Workout')

            for exercise in workout.get('exercises', []):
                ex_name = exercise.get('title', 'Unknown')

                for i, s in enumerate(exercise.get('sets', [])):
                    set_num = str(i + 1)
                    signature = f"{w_date_clean}_{w_title}_{ex_name}_{set_num}"
                    if signature in existing_sets:
                        skipped_count += 1
                        continue

                    weight_kg = s.get('weight_kg', 0)
                    weight_lbs = round(weight_kg * 2.20462, 1) if weight_kg else 0
                    reps = s.get('reps', 0)

                    row = [
                        w_date_clean,
                        w_title,
                        ex_name,
                        set_num,
                        weight_lbs,
                        reps,
                        s.get('rpe', ''),
                        s.get('type', 'normal')
                    ]
                    new_rows.append(row)

        if new_rows:
            existing_rows = []
            if os.path.isfile(CSV_FILE):
                with open(CSV_FILE, mode='r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader, None)
                    existing_rows = list(reader)

            all_rows = existing_rows + new_rows
            all_rows.sort(key=lambda x: x[0] if x else '', reverse=True)

            with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Workout", "Exercise", "Set", "Weight (lbs)", "Reps", "RPE", "Type"])
                writer.writerows(all_rows)

            sqlite_rows = sync_csv_to_table("hevy_stats.csv")
            print(f"SUCCESS: Added {len(new_rows)} new sets. (Skipped {skipped_count} duplicates) [Sorted newest to oldest]")
            print(f"SQLite sync complete: {sqlite_rows} rows in hevy_stats")
        else:
            print(f"No *new* sets found. (Skipped {skipped_count} duplicates)")

    except HttpRequestError as e:
        print(f"Network/API error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
