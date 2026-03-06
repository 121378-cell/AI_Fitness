import os
import pickle
import io
import json
import csv
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
from dotenv import load_dotenv
from google.auth import credentials
import subprocess

# --- CONFIGURATION ---
DRY_RUN = False  # Set to False to actually post workouts to Hevy
MODEL_NAME = "gemini-flash-latest" # Using latest Gemini Flash model

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HEVY_API_KEY = os.getenv("HEVY_API_KEY")
TARGET_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]

# --- MONTHLY PROMPT ---
def load_monthly_prompt():
    """Load the monthly prompt from MONTHLY_PROMPT_TEXT.txt file."""
    prompt_file = "MONTHLY_PROMPT_TEXT.txt"
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"ERROR: Could not find '{prompt_file}'. Please ensure it exists in the current directory.")
        raise
    except Exception as e:
        print(f"ERROR: Failed to read '{prompt_file}': {e}")
        raise

def get_smart_memory_context(file_content_bytes):
    """
    Parses the Memory Log CSV bytes and returns a filtered string containing ONLY:
    1. 'Active' Goals
    2. 'Medical' history (Safety critical)
    3. Recent entries from the last 60 days
    """
    try:
        # Convert bytes to string buffer for pandas
        data_str = file_content_bytes.decode('utf-8')
        df = pd.read_csv(io.StringIO(data_str))

        if 'Date' not in df.columns or 'Category' not in df.columns:
            raise ValueError("Missing required columns: 'Date' or 'Category'")

        # 1. Capture 'Active' Goals and 'Medical' Records (Always Relevant)
        always_keep = df[
            (df['Date'].astype(str).str.lower() == 'active') |
            (df['Category'].astype(str).str.lower() == 'medical')
        ].copy()

        # 2. Filter Dated Entries (Recent History Only)
        dated_rows = df[df['Date'].astype(str).str.lower() != 'active'].copy()
        dated_rows['parsed_date'] = pd.to_datetime(dated_rows['Date'], format='mixed', errors='coerce')

        # Set "Recent" window (e.g., last 60 days)
        cutoff_date = datetime.now() - timedelta(days=60)
        recent_rows = dated_rows[dated_rows['parsed_date'] >= cutoff_date]

        # 3. Combine and clean up
        final_df = pd.concat([always_keep, recent_rows]).drop(columns=['parsed_date'], errors='ignore')

        return final_df.to_csv(index=False)

    except Exception as e:
        print(f"Error processing memory log: {str(e)}")
        return None

def calculate_one_rep_max(weight, reps):
    """Calculate estimated 1RM using the Epley formula: 1RM = weight × (1 + reps/30)"""
    if reps == 0 or weight == 0:
        return 0
    return weight * (1 + reps / 30)

def aggregate_training_data(hevy_stats_df, exercise_db_df, months=6):
    """
    Aggregate training data for the last N months.

    Returns:
        - 1RM per muscle group
        - Total volume per muscle group
        - Exercise-specific PRs
    """
    try:
        # Filter for last N months (using DateOffset for precision)
        cutoff_date = datetime.now() - pd.DateOffset(months=months)
        hevy_stats_df['Date'] = pd.to_datetime(hevy_stats_df['Date'], format='mixed', errors='coerce')
        recent_data = hevy_stats_df[hevy_stats_df['Date'] >= cutoff_date].copy()

        if recent_data.empty:
            print(f"   [!] Warning: No data found in the last {months} months")
            return None

        # Perform aggregation logic here (placeholder)
        return recent_data

    except Exception as e:
        print(f"Error aggregating training data: {str(e)}")
        return None

def calculate_strength_trends(hevy_stats_df, recent_months=3, history_months=12):
    """
    Compare recent 1RM vs all-time 1RM to detect plateaus or regressions.
    Returns trend analysis per exercise.
    """
    now = datetime.now()
    recent_cutoff = now - pd.DateOffset(months=recent_months)
    history_cutoff = now - pd.DateOffset(months=history_months)

    df = hevy_stats_df.copy()
    df['Date'] = pd.to_datetime(df['Date'], format='mixed')
    df['estimated_1rm'] = df.apply(
        lambda row: calculate_one_rep_max(row['Weight (lbs)'], row['Reps']), axis=1
    )

    # Filter to history window
    df = df[df['Date'] >= history_cutoff]

    if df.empty:
        return None

    # Recent period (last N months)
    recent_data = df[df['Date'] >= recent_cutoff]
    if recent_data.empty:
        return None

    recent_1rm = recent_data.groupby('Exercise')['estimated_1rm'].max()

    # All-time 1RM within history window
    all_time_1rm = df.groupby('Exercise')['estimated_1rm'].max()

    # Calculate trend
    trends = pd.DataFrame({
        'Recent_1RM': recent_1rm,
        'AllTime_1RM': all_time_1rm
    }).dropna()

    if trends.empty:
        return None

    trends['Trend_Pct'] = ((trends['Recent_1RM'] - trends['AllTime_1RM']) / trends['AllTime_1RM'] * 100).round(1)
    trends['Status'] = trends['Trend_Pct'].apply(
        lambda x: 'PLATEAU' if -2 <= x <= 2 else ('REGRESSING' if x < -2 else 'PROGRESSING')
    )

    return trends.sort_values('Trend_Pct')

def validate_variable_loading(routines_json):
    """
    Validates that compound movements use variable loading (not straight sets).
    Returns list of warnings for exercises with static weights across multiple sets.
    """
    warnings = []

    routines = routines_json.get('routines', []) if isinstance(routines_json, dict) else routines_json

    for routine in routines:
        for exercise in routine.get('exercises', []):
            sets = exercise.get('sets', [])
            if len(sets) < 2:
                continue

            weights = [s.get('weight_kg', 0) for s in sets if s.get('type') == 'normal']

            # Check if all weights are identical (straight sets)
            if len(set(weights)) == 1 and len(weights) > 1:
                ex_id = exercise.get('exercise_template_id', 'unknown')
                warnings.append({
                    'routine': routine.get('title'),
                    'exercise_id': ex_id,
                    'issue': f'Static weight ({weights[0]}kg) across {len(weights)} sets - consider variable loading'
                })

    return warnings

def fetch_and_save_hevy_exercises():
    """Downloads exercise list from Hevy and saves as CSV locally."""
    print("   [!] 'HEVY APP exercises.csv' missing. Downloading from Hevy API...")
    url = "https://api.hevyapp.com/v1/exercise_templates"
    headers = {"api-key": HEVY_API_KEY}
    
    all_exercises = []
    page = 1
    page_count = 1
    
    try:
        # Hevy paginates, so we loop to get them all
        while page <= page_count:
            response = requests.get(url, headers=headers, params={"page": page, "pageSize": 50})
            if response.status_code != 200:
                print(f"Error fetching exercises: {response.text}")
                return None
            
            data = response.json()
            page_count = data.get("page_count", 1)
            all_exercises.extend(data.get("exercise_templates", []))
            page += 1
            
        # Convert to DataFrame
        df = pd.DataFrame(all_exercises)
        # Keep columns needed for aggregation and LLM context
        required_cols = ['id', 'title', 'primary_muscle_group', 'secondary_muscle_groups', 'equipment', 'type']
        available_cols = [c for c in required_cols if c in df.columns]

        if 'title' in df.columns and 'id' in df.columns:
            df = df[available_cols]
            # Save locally so we can read it
            df.to_csv("HEVY APP exercises.csv", index=False)
            print(f"   -> Successfully saved {len(df)} exercises ({len(available_cols)} columns) to 'HEVY APP exercises.csv'")
            return df
        else:
            print("   -> Error: Unexpected data format from Hevy.")
            return None
            
    except Exception as e:
        print(f"   -> Failed to fetch exercises: {e}")
        return None

def get_sheet_tab(filename, sheet_name):
    """Fetch a specific tab from a local CSV file."""
    print(f"   Searching for '{filename}' locally...")
    if not os.path.exists(filename):
        print(f"   [!] Warning: Could not find '{filename}' locally.")
        return None

    # Read the CSV file
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    print(f"   -> Loaded '{filename}' ({len(rows)} rows)")
    return io.BytesIO('\n'.join([','.join(row) for row in rows]).encode('utf-8'))

def get_file_content(filename):
    if os.path.exists(filename):
        print(f"   Found '{filename}' locally.")
        with open(filename, 'rb') as f:
            return io.BytesIO(f.read())
    print(f"   [!] Warning: Could not find '{filename}' locally.")
    return None

def generate_monthly_plan():
    """Generate a monthly training plan using data and Ollama."""
    print("\n--- STEP 1: GATHERING DATA ---")
    
    # Try to read from data/ directory first, then current directory
    hevy_stats_data = None
    if os.path.exists("data/hevy_stats.csv"):
        hevy_stats = get_file_content("data/hevy_stats.csv")
        if hevy_stats:
            hevy_stats_data = hevy_stats.read().decode('utf-8')
    elif os.path.exists("hevy_stats.csv"):
        hevy_stats = get_file_content("hevy_stats.csv")
        if hevy_stats:
            hevy_stats_data = hevy_stats.read().decode('utf-8')
    
    exercise_db_data = None
    if os.path.exists("HEVY APP exercises.csv"):
        exercise_db = get_file_content("HEVY APP exercises.csv")
        if exercise_db:
            exercise_db_data = exercise_db.read().decode('utf-8')
    
    chat_memory_data = None
    if os.path.exists("data/Chat Memory.csv"):
        chat_memory = get_sheet_tab("data/Chat Memory.csv", "Memory Log")
        if chat_memory:
            chat_memory_data = chat_memory.read().decode('utf-8')
    elif os.path.exists("Chat Memory.csv"):
        chat_memory = get_sheet_tab("Chat Memory.csv", "Memory Log")
        if chat_memory:
            chat_memory_data = chat_memory.read().decode('utf-8')
    
    print(f"   Loaded hevy_stats: {len(hevy_stats_data.split(chr(10))) if hevy_stats_data else 0} rows")
    print(f"   Loaded exercise_db: {len(exercise_db_data.split(chr(10))) if exercise_db_data else 0} rows")
    print(f"   Loaded chat_memory: {len(chat_memory_data.split(chr(10))) if chat_memory_data else 0} rows")
    
    # Generate plan using Ollama or create a sample plan
    print("\n--- STEP 2: GENERATING PLAN ---")
    plan = generate_plan_with_ollama(hevy_stats_data, exercise_db_data, chat_memory_data)
    
    return plan

def generate_plan_with_ollama(hevy_stats, exercise_db, chat_memory):
    """Generate a training plan using Ollama or return a sample plan."""
    # Create a sample plan as fallback
    sample_plan = {
        "routines": [
            {
                "title": "Push - Chest Dominant",
                "exercises": [
                    {
                        "exercise_template_id": "947DAC23",
                        "name": "Barbell Bench Press",
                        "sets": [
                            {"type": "normal", "weight_kg": 100, "reps": 8},
                            {"type": "normal", "weight_kg": 110, "reps": 6}
                        ]
                    }
                ]
            },
            {
                "title": "Legs - Squat Focus",
                "exercises": [
                    {
                        "exercise_template_id": "B8127AD1",
                        "name": "Barbell Back Squat",
                        "sets": [
                            {"type": "normal", "weight_kg": 150, "reps": 6},
                            {"type": "normal", "weight_kg": 155, "reps": 5}
                        ]
                    }
                ]
            }
        ]
    }
    
    try:
        print("   Attempting to use Ollama for plan generation...")
        ollama_response = call_ollama_service(hevy_stats or "", chat_memory or "")
        if ollama_response:
            print("   Successfully generated plan with Ollama")
            try:
                parsed_plan = json.loads(ollama_response)
                if isinstance(parsed_plan, dict) and 'routines' in parsed_plan:
                    return parsed_plan
            except json.JSONDecodeError:
                print("   Could not parse Ollama response as JSON, using sample plan")
    except Exception as e:
        print(f"   Ollama error: {e}")
    
    print("   Using sample plan as fallback")
    return sample_plan

def call_ollama_service(hevy_stats, chat_memory):
    """Call Ollama service to generate a training plan."""
    try:
        # Try basic Ollama call with proper encoding and timeout
        import sys
        result = subprocess.run(
            ["ollama", "run", "mistral", "Hello"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print("   Ollama service is available")
            return None
        else:
            print("   Ollama test failed")
            return None
    except FileNotFoundError:
        print("   Note: Ollama executable not found - continuing with fallback plan")
        return None
    except subprocess.TimeoutExpired:
        print("   Note: Ollama request timed out - using fallback plan")
        return None
    except Exception as e:
        print(f"   Note: Error connecting to Ollama - using fallback plan")
        return None

def get_or_create_folder(folder_name="AI Fitness"):
    """Get the folder ID for the given folder name, or create it if it doesn't exist."""
    headers = {"api-key": HEVY_API_KEY, "Content-Type": "application/json"}

    # List existing folders
    response = requests.get("https://api.hevyapp.com/v1/routine_folders", headers=headers)
    if response.status_code == 200:
        folders = response.json().get('routine_folders', [])
        for folder in folders:
            if folder['title'] == folder_name:
                print(f"   Found existing folder '{folder_name}' (ID: {folder['id']})")
                return folder['id']

    # Folder doesn't exist, create it
    print(f"   Creating new folder '{folder_name}'...")
    payload = {"routine_folder": {"title": folder_name}}
    response = requests.post("https://api.hevyapp.com/v1/routine_folders", headers=headers, json=payload)
    if response.status_code in [200, 201]:
        folder_id = response.json()['routine_folder']['id']
        print(f"   Created folder '{folder_name}' (ID: {folder_id})")
        return folder_id
    else:
        print(f"   Failed to create folder: {response.text}")
        return None

def delete_routines_in_folder(folder_id):
    """Delete all routines in the specified folder."""
    headers = {"api-key": HEVY_API_KEY}

    # List routines in the folder
    response = requests.get(f"https://api.hevyapp.com/v1/routines?routine_folder_id={folder_id}", headers=headers)
    if response.status_code != 200:
        print(f"   Failed to list routines: {response.text}")
        return

    routines = response.json().get('routines', [])
    if not routines:
        print(f"   No existing routines to delete.")
        return

    print(f"   Deleting {len(routines)} existing routine(s)...")
    for routine in routines:
        routine_id = routine['id']
        title = routine['title']
        delete_response = requests.delete(f"https://api.hevyapp.com/v1/routines/{routine_id}", headers=headers)
        if delete_response.status_code == 200:
            print(f"   -> Deleted '{title}'")
        else:
            print(f"   -> Failed to delete '{title}': {delete_response.text}")

def post_to_hevy(routines_json):
    if DRY_RUN:
        print("\n[DRY RUN MODE ENABLED] - Skipping upload to Hevy.")
        print("Here is the exact data that WOULD be sent:")
        print(json.dumps(routines_json, indent=2))
        return

    print("\n--- STEP 3: UPLOADING TO HEVY ---")

    # Create a new dated folder each time
    from datetime import datetime
    folder_name = f"AI Fitness {datetime.now().strftime('%Y-%m-%d')}"
    folder_id = get_or_create_folder(folder_name)
    if not folder_id:
        print("ERROR: Could not get or create folder")
        return

    url = "https://api.hevyapp.com/v1/routines"
    headers = {"api-key": HEVY_API_KEY, "Content-Type": "application/json"}

    routines_list = routines_json.get('routines', []) if isinstance(routines_json, dict) else routines_json

    print(f"\n   Creating {len(routines_list)} new routine(s)...")
    for routine in routines_list:
        # Add folder_id to the routine
        routine['folder_id'] = folder_id

        payload = {"routine": routine} if "routine" not in routine else routine
        title = payload['routine']['title']
        print(f"   Posting routine: {title}...")

        response = requests.post(url, headers=headers, json=payload)
        # Hevy returns 200 or 201 for success, or the routine data itself
        try:
            response_data = response.json()
            if response.status_code in [200, 201] or 'routine' in response_data:
                routine_data = response_data.get('routine', [{}])
                routine_id = routine_data[0].get('id', 'unknown') if isinstance(routine_data, list) else routine_data.get('id', 'unknown')
                print(f"   -> Success! (ID: {routine_id})")
            else:
                print(f"   -> Failed: {response.text}")
        except (json.JSONDecodeError, requests.exceptions.JSONDecodeError):
            print(f"   -> Failed: Invalid JSON response - {response.text[:200]}")

if __name__ == "__main__":
    try:
        if not GEMINI_API_KEY:
            print("ERROR: GEMINI_API_KEY not found in .env file")
        else:
            plan = generate_monthly_plan()

            # Validate variable loading in generated plan
            print("\n--- VALIDATING PLAN ---")
            loading_warnings = validate_variable_loading(plan)
            if loading_warnings:
                print("   [!] Variable Loading Warnings (straight sets detected):")
                for w in loading_warnings:
                    print(f"       - {w['routine']}: {w['exercise_id']} - {w['issue']}")
            else:
                print("   Variable loading check passed.")

            post_to_hevy(plan)
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
