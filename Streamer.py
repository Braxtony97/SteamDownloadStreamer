import time
import re
import winreg
from pathlib import Path
from collections import deque

CHECK_INTERVAL = 60  # 1 minute
TOTAL_CHECKS = 5     # 5 minute

def main():
    steam_path = get_steam_path()
    log_path = steam_path / "logs" / "content_log.txt"

    print("Steam found:", steam_path)
    print("Streaming start...\n")

    for i in range(TOTAL_CHECKS):
        game, speed, status = parse_content_log(log_path)

        print(f"[{i + 1}/5]")
        print(f"Game: {game}")
        print(f"Status: {status}")
        print(f"Speed: {speed:.2f} MB/s")
        print("-" * 40)

        time.sleep(CHECK_INTERVAL)


def get_steam_path():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
            steam_path, _ = winreg.QueryValueEx(key, "SteamPath")
            return Path(steam_path)
    except FileNotFoundError:
        raise RuntimeError("Steam not found in registry")


def parse_content_log(log_path):
    if not log_path.exists():
        return None, 0.0, "log not found"

    lines = deque(log_path.open(encoding="utf-8", errors="ignore"), maxlen=300)

    game_name = "Unknown"
    speed = 0.0
    status = "idle"

    for line in reversed(lines):
        if "AppID" in line and "Downloading" in line:
            status = "downloading"

        if "Paused" in line:
            status = "paused"

        if "name" in line.lower():
            match = re.search(r'"name"\s+"(.+?)"', line)
            if match:
                game_name = match.group(1)

        if "rate" in line.lower():
            match = re.search(r'([\d.]+)\s*MB/s', line)
            if match:
                speed = float(match.group(1))
                break

    return game_name, speed, status

if __name__ == "__main__":
    main()