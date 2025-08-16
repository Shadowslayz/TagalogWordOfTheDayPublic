import webbrowser
import time
from datetime import datetime

# === CONFIGURATION ===
target_time_str = "2025-05-24 08:10:00"  # Format: YYYY-MM-DD HH:MM:SS
url = "https://www.twitch.tv/playsoulframe"

# Convert string to datetime object
target_time = datetime.strptime(target_time_str, "%Y-%m-%d %H:%M:%S")

print(f"Waiting until {target_time} to open {url}...")

# Wait loop
while datetime.now() < target_time:
    time.sleep(1)

# Open the URL
webbrowser.open(url)
print(f"Opened {url} at {datetime.now()}")
