#!/usr/bin/env python3
"""AI Fitness Dashboard - Interactive Setup Script (Garmin-only edition)."""

import os
import platform
import subprocess
import sys
from pathlib import Path


def ask(prompt: str, default: str = "") -> str:
    value = input(f"{prompt} [{default}]: ").strip()
    return value or default


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    value = input(f"{prompt} {suffix}: ").strip().lower()
    if not value:
        return default
    return value in {"y", "yes"}


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def load_env() -> dict:
    env_path = script_dir() / ".env"
    values = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.strip().startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                values[k.strip()] = v.strip()
    return values


def save_env(values: dict) -> None:
    lines = [
        "# AI Fitness Dashboard Configuration",
        "",
        "# File Paths",
        f"SAVE_PATH={values.get('SAVE_PATH', '')}",
        f"DRIVE_MOUNT_PATH={values.get('DRIVE_MOUNT_PATH', '')}",
        "",
        "# Garmin Connect",
        f"GARMIN_EMAIL={values.get('GARMIN_EMAIL', '')}",
        f"GARMIN_PASSWORD={values.get('GARMIN_PASSWORD', '')}",
        "",
        "# AI Providers",
        f"AI_PROVIDER_ORDER={values.get('AI_PROVIDER_ORDER', 'ollama,groq,gemini')}",
        f"OLLAMA_BASE_URL={values.get('OLLAMA_BASE_URL', 'http://localhost:11434')}",
        f"OLLAMA_MODEL={values.get('OLLAMA_MODEL', 'llama3.1:8b-instruct')}",
        f"GROQ_API_KEY={values.get('GROQ_API_KEY', '')}",
        f"GROQ_MODEL={values.get('GROQ_MODEL', 'llama-3.1-70b-versatile')}",
        f"GEMINI_API_KEY={values.get('GEMINI_API_KEY', '')}",
        f"GEMINI_MODEL={values.get('GEMINI_MODEL', 'gemini-flash-latest')}",
        f"GOOGLE_DRIVE_FOLDER_ID={values.get('GOOGLE_DRIVE_FOLDER_ID', '')}",
        "",
        "# System Settings",
        f"CHECK_MOUNT_STATUS={values.get('CHECK_MOUNT_STATUS', 'False')}",
        f"PROJECT_DIR={values.get('PROJECT_DIR', str(script_dir()))}",
        f"LOG_FILE={values.get('LOG_FILE', '/home/pi/cron_log.txt')}",
        f"DASHBOARD_PORT={values.get('DASHBOARD_PORT', '8501')}",
        f"AI_FITNESS_LOG_LEVEL={values.get('AI_FITNESS_LOG_LEVEL', 'INFO')}",
        "",
    ]
    (script_dir() / ".env").write_text("\n".join(lines), encoding="utf-8")


def install_requirements() -> None:
    req = script_dir() / "requirements.txt"
    if req.exists() and ask_yes_no("Install dependencies now?", default=True):
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req)], check=False)


def configure(values: dict) -> dict:
    is_pi = platform.machine().startswith("arm") or platform.machine() == "aarch64"
    default_save = values.get("SAVE_PATH", "/home/pi/GDrive/Gemini Gems/Personal trainer" if is_pi else str(Path.home() / "AI_Fitness_Data"))
    values["SAVE_PATH"] = ask("Data save path", default_save)
    values["DRIVE_MOUNT_PATH"] = ask("Drive mount path", values.get("DRIVE_MOUNT_PATH", "/home/pi/GDrive" if is_pi else ""))
    values["GARMIN_EMAIL"] = ask("Garmin email", values.get("GARMIN_EMAIL", ""))
    values["GARMIN_PASSWORD"] = ask("Garmin password", values.get("GARMIN_PASSWORD", ""))

    values["AI_PROVIDER_ORDER"] = ask("AI provider order", values.get("AI_PROVIDER_ORDER", "ollama,groq,gemini"))
    values["OLLAMA_BASE_URL"] = ask("OLLAMA_BASE_URL", values.get("OLLAMA_BASE_URL", "http://localhost:11434"))
    values["OLLAMA_MODEL"] = ask("OLLAMA_MODEL", values.get("OLLAMA_MODEL", "llama3.1:8b-instruct"))
    values["GROQ_API_KEY"] = ask("GROQ_API_KEY", values.get("GROQ_API_KEY", ""))
    values["GROQ_MODEL"] = ask("GROQ_MODEL", values.get("GROQ_MODEL", "llama-3.1-70b-versatile"))
    values["GEMINI_API_KEY"] = ask("GEMINI_API_KEY", values.get("GEMINI_API_KEY", ""))
    values["GEMINI_MODEL"] = ask("GEMINI_MODEL", values.get("GEMINI_MODEL", "gemini-flash-latest"))
    values["GOOGLE_DRIVE_FOLDER_ID"] = ask("GOOGLE_DRIVE_FOLDER_ID", values.get("GOOGLE_DRIVE_FOLDER_ID", ""))

    values["CHECK_MOUNT_STATUS"] = "True" if ask_yes_no("Enable mount checks?", default=False) else "False"
    values["PROJECT_DIR"] = str(script_dir())
    values["LOG_FILE"] = ask("Log file", values.get("LOG_FILE", "/home/pi/cron_log.txt"))
    values["DASHBOARD_PORT"] = ask("Dashboard port", values.get("DASHBOARD_PORT", "8501"))
    values["AI_FITNESS_LOG_LEVEL"] = ask("Log level", values.get("AI_FITNESS_LOG_LEVEL", "INFO"))

    Path(values["SAVE_PATH"]).mkdir(parents=True, exist_ok=True)
    return values


def print_cron_examples() -> None:
    proj = script_dir()
    print("\nSuggested cron jobs (Garmin-only):")
    print(f"30 * * * * cd {proj} && /usr/bin/python3 daily_garmin_health.py >> /home/pi/cron_log.txt 2>&1")
    print(f"40 * * * * cd {proj} && /usr/bin/python3 daily_garmin_activities.py >> /home/pi/cron_log.txt 2>&1")
    print(f"0 6 * * * cd {proj} && /usr/bin/python3 update_yesterday_garmin.py >> /home/pi/cron_log.txt 2>&1")


def main() -> int:
    print("AI Fitness setup (Garmin-only)\n")
    env_values = configure(load_env())
    save_env(env_values)
    install_requirements()
    print_cron_examples()
    print("\nSetup complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
