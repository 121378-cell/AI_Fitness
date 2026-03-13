import os
from typing import Dict


def get_validation_tables(save_path: str) -> Dict[str, Dict[str, object]]:
    """Shared dataset configuration for validation/quality pipelines."""
    return {
        "garmin_stats": {
            "csv": os.path.join(save_path, "garmin_stats.csv"),
            "date_col": "Date",
            "check_cols": ["Weight (lbs)", "RHR", "Steps"],
        },
        "hevy_stats": {
            "csv": os.path.join(save_path, "hevy_stats.csv"),
            "date_col": "Date",
            "check_cols": ["Workout", "Exercise", "Weight (lbs)", "Reps"],
        },
        "garmin_activities": {
            "csv": os.path.join(save_path, "garmin_activities.csv"),
            "date_col": "Date",
            "check_cols": ["activityName", "sportType", "distance"],
        },
        "garmin_runs": {
            "csv": os.path.join(save_path, "garmin_runs.csv"),
            "date_col": "Date",
            "check_cols": ["activityName", "averageSpeed", "averageHR"],
        },
    }
