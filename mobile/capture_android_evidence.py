"""Capture evidence from an explicitly chosen Android device via adb.

Only run against a device/account you are authorized to test. Captured files stay
under ignored mobile/evidence and may contain personal data until reviewed.
"""

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def adb(serial: str, *arguments: str) -> bytes:
    return subprocess.run(
        ["adb", "-s", serial, *arguments],
        check=True, capture_output=True, timeout=30,
    ).stdout


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect Android QA evidence to a local ignored folder")
    parser.add_argument("--serial", required=True, help="Serial shown by adb devices -l")
    parser.add_argument("--case", required=True, help="Test case, e.g. MOB-03")
    parser.add_argument("--build", required=True, help="App build identifier recorded by tester")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,80}", args.serial):
        parser.error("invalid device serial")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,50}", args.case):
        parser.error("invalid case identifier")

    available = adb(args.serial, "get-state").decode().strip()
    if available != "device":
        parser.error("device is not ready")
    recorded = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = Path(__file__).with_name("evidence") / f"{args.case}-{recorded}"
    destination.mkdir(parents=True, exist_ok=False)
    try:
        (destination / "screen.png").write_bytes(adb(args.serial, "exec-out", "screencap", "-p"))
        (destination / "logcat.txt").write_bytes(adb(args.serial, "logcat", "-d", "-t", "200", "-v", "threadtime"))
        metadata = {
            "case": args.case,
            "captured_utc": recorded,
            "app_build": args.build,
            "device_serial": args.serial,
            "android_release": adb(args.serial, "shell", "getprop", "ro.build.version.release").decode().strip(),
            "device_model": adb(args.serial, "shell", "getprop", "ro.product.model").decode().strip(),
            "result": "NOT_RECORDED",
        }
        (destination / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
        parser.exit(1, f"Capture incomplete in {destination}: {exc}\n")
    print(f"Saved locally: {destination}. Review/redact before sharing; no test result assigned.")


if __name__ == "__main__":
    main()
