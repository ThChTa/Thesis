import os
import requests
import time
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
BASE_PATH = os.path.normpath('C:/Users/Thomas/Desktop/whisper_mic/whisper_mic')
FILE_NAMES = ['alarm.json', 'data.json', 'air_condition.json']
RECEIVER_URL = 'http://192.168.32.181:9090/upload'
COOLDOWN_SECONDS = 2  # minimum seconds between sends per file

# Global tracker to avoid duplicate sends of data.json entries
last_sent_entry = None

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, file_paths):
        self.file_paths = set(file_paths)
        # Track last send time per file for cooldown
        self.last_sent_times = {file_path: 0 for file_path in file_paths}

    def on_modified(self, event):
        if event.src_path not in self.file_paths:
            return

        current_time = time.time()
        last_sent = self.last_sent_times.get(event.src_path, 0)
        if current_time - last_sent < COOLDOWN_SECONDS:
            # Skip rapid repeated events
            return

        print(f'Modification detected in: {event.src_path}')
        try:
            if os.path.basename(event.src_path) == 'data.json':
                send_last_data_entry(event.src_path, 'PC1')
            else:
                send_file(event.src_path, 'PC1')
            self.last_sent_times[event.src_path] = current_time
        except Exception as e:
            print(f'Error processing {event.src_path}: {e}')

def read_json_with_retry(file_path, retries=5, delay=0.2):
    for attempt in range(retries):
        try:
            if os.path.getsize(file_path) == 0:
                time.sleep(delay)
                continue

            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f'Attempt {attempt+1}: JSON not ready ({e}), retrying...')
            time.sleep(delay)
    raise ValueError('Failed to read valid JSON after retries')

def send_file(file_path, source):
    try:
        file_name = os.path.basename(file_path)
        headers = {'Source': source}
        with open(file_path, 'rb') as file:
            response = requests.post(RECEIVER_URL, files={file_name: file}, headers=headers, timeout=60)
        # print(f'Status: {response.status_code} - {response.text}')
    except Exception as e:
        print(f'File send failed: {e}')

def send_last_data_entry(file_path, source):
    global last_sent_entry
    try:
        data = read_json_with_retry(file_path)
        last_entry = data.get("data", [])[-1] if data.get("data") else None
        if not last_entry:
            print('No entry found in data.json.')
            return

        if last_sent_entry == last_entry:
            print('Same entry already sent. Skipping.')
            return

        headers = {'Source': source}
        response = requests.post(RECEIVER_URL, json=last_entry, headers=headers, timeout=10)

        if response.status_code == 200:
            # print(f'Successfully sent entry: {last_entry.get("nlp_text")}')
            last_sent_entry = last_entry
        else:
            print(f'Failed to send: {response.status_code} - {response.text}')
    except Exception as e:
        print(f'Error in send_last_data_entry: {e}')

def main():
    file_paths = [os.path.join(BASE_PATH, fname) for fname in FILE_NAMES]
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f'Missing file: {file_path}')
            return
    event_handler = FileChangeHandler(file_paths)
    observer = Observer()
    observer.schedule(event_handler, path=BASE_PATH, recursive=False)
    observer.start()
    print(f'Watching {BASE_PATH} for changes...')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
