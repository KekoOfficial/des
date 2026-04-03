import datetime
import json
import os

LOG_FILE = "logs.txt"

def log(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")

def clean_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
