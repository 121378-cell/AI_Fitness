import os
import platform
import sys
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class RuntimeConfig:
    save_path: str
    check_mount: bool
    drive_path: str
    is_windows: bool


def load_runtime_config(default_save: Optional[str] = None) -> RuntimeConfig:
    """Load environment/runtime settings once with safe defaults."""
    load_dotenv()
    save_path = os.getenv("SAVE_PATH", default_save or os.getcwd())
    check_mount = os.getenv("CHECK_MOUNT_STATUS", "False").lower() == "true"
    drive_path = os.getenv("DRIVE_MOUNT_PATH", "/home/pi/google_drive")
    is_windows = platform.system() == "Windows"
    return RuntimeConfig(
        save_path=save_path,
        check_mount=check_mount,
        drive_path=drive_path,
        is_windows=is_windows,
    )


def enforce_mount_safety(config: RuntimeConfig) -> None:
    """Stop process when mount safety is enabled but the mount is missing."""
    if config.check_mount and not config.is_windows:
        print(f"Safety Check: Verifying mount at {config.drive_path}...")
        if not os.path.ismount(config.drive_path):
            print(f"CRITICAL ERROR: Drive is not mounted at {config.drive_path}.")
            print("Stopping script to prevent writing to local storage.")
            sys.exit(1)
        print("Safety Check: PASSED. Drive is mounted.")
    elif config.check_mount and config.is_windows:
        print("Note: Mount check skipped on Windows (not applicable).")
