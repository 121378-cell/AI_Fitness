#!/usr/bin/env python3
"""AI Fitness Dashboard - Setup interactivo (solo Garmin)."""

import getpass
import os
import platform
import subprocess
import sys
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'


def info(msg):
    print(f"{Colors.BLUE}[i] {msg}{Colors.END}")


def ok(msg):
    print(f"{Colors.GREEN}[OK] {msg}{Colors.END}")


def warn(msg):
    print(f"{Colors.YELLOW}[!] {msg}{Colors.END}")


def err(msg):
    print(f"{Colors.RED}[ERROR] {msg}{Colors.END}")


def ask(prompt, default=None, password=False):
    suffix = f" [{default}]" if default else ""
    q = f"{prompt}{suffix}: "
    value = getpass.getpass(q) if password else input(q).strip()
    return value or default


def ask_yes_no(prompt, default=True):
    suffix = " [Y/n]: " if default else " [y/N]: "
    val = input(prompt + suffix).strip().lower()
    if not val:
        return default
    return val in {"y", "yes"}


def load_env(path: Path):
    data = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                data[k.strip()] = v.strip()
    return data


def save_env(path: Path, env):
    content = [
        "# AI Fitness Dashboard Configuration",
        "",
        "# File Paths",
        f"SAVE_PATH={env.get('SAVE_PATH', '')}",
        f"DRIVE_MOUNT_PATH={env.get('DRIVE_MOUNT_PATH', '')}",
        "",
        "# Garmin Connect",
        f"GARMIN_EMAIL={env.get('GARMIN_EMAIL', '')}",
        f"GARMIN_PASSWORD={env.get('GARMIN_PASSWORD', '')}",
        "",
        "# System Settings",
        f"CHECK_MOUNT_STATUS={env.get('CHECK_MOUNT_STATUS', 'False')}",
        f"DASHBOARD_PORT={env.get('DASHBOARD_PORT', '8501')}",
        f"AI_FITNESS_LOG_LEVEL={env.get('AI_FITNESS_LOG_LEVEL', 'INFO')}",
    ]
    path.write_text("\n".join(content) + "\n")
    ok(f"Configuración guardada en {path}")


def install_requirements(base: Path):
    req = base / "requirements.txt"
    if not req.exists():
        err("requirements.txt no encontrado")
        return False
    info("Instalando dependencias...")
    res = subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req)])
    return res.returncode == 0


def main():
    base = Path(__file__).parent
    env_path = base / ".env"
    env = load_env(env_path)

    info("Configuración inicial AI Fitness")

    is_pi = platform.machine().startswith("arm") or platform.machine() == "aarch64"
    default_save = env.get("SAVE_PATH", "/home/pi/GDrive/Gemini Gems/Personal trainer" if is_pi else str(Path.home() / "AI_Fitness_Data"))
    env["SAVE_PATH"] = ask("Ruta de guardado de datos", default_save)
    Path(env["SAVE_PATH"]).mkdir(parents=True, exist_ok=True)

    env["DRIVE_MOUNT_PATH"] = ask("Ruta de montaje GDrive (opcional)", env.get("DRIVE_MOUNT_PATH", ""))
    env["CHECK_MOUNT_STATUS"] = "True" if ask_yes_no("¿Comprobar estado de montaje en runtime?", default=False) else "False"

    if ask_yes_no("¿Configurar Garmin Connect ahora?", default=True):
        env["GARMIN_EMAIL"] = ask("Garmin email", env.get("GARMIN_EMAIL", ""))
        env["GARMIN_PASSWORD"] = ask("Garmin password", env.get("GARMIN_PASSWORD", ""), password=True)

    env["DASHBOARD_PORT"] = ask("Puerto dashboard", env.get("DASHBOARD_PORT", "8501"))
    env["AI_FITNESS_LOG_LEVEL"] = ask("Log level", env.get("AI_FITNESS_LOG_LEVEL", "INFO"))

    save_env(env_path, env)

    if ask_yes_no("¿Instalar dependencias ahora?", default=True):
        if install_requirements(base):
            ok("Dependencias instaladas")
        else:
            warn("La instalación devolvió error; revisa logs")

    ok("Setup completado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
