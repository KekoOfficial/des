import datetime
import json

QUEUE_FILE = "queue.json"
LOG_FILE = "logs.txt"

def log(text):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.datetime.now()}] {text}\n")


def add_to_queue(url):
    try:
        with open(QUEUE_FILE, "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append(url)

    with open(QUEUE_FILE, "w") as f:
        json.dump(data, f)


def remove_from_queue(url):
    try:
        with open(QUEUE_FILE, "r") as f:
            data = json.load(f)
    except:
        return

    if url in data:
        data.remove(url)

    with open(QUEUE_FILE, "w") as f:
        json.dump(data, f)