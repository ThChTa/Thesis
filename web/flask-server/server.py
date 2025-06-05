import json
import os
import threading
import time

from flask import Flask, Response, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow all origins

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
alarm_path = os.path.join(BASE_DIR, "alarm.json")
#alarm_path = r"C:\Users\Thomas\Desktop\whisper_mic\whisper_mic\alarm.json"
air_condition_path = os.path.join(BASE_DIR, "air_condition.json")
data_path = os.path.join(BASE_DIR, "data.json")  # Assuming this file exists


def update_timers():
    last_update = time.time()

    while True:
        current_time = time.time()
        elapsed_time = current_time - last_update

        # Check if a full minute has passed
        if elapsed_time >= 60:
            last_update += 60  # Keep fixed interval to prevent drift

            try:
                # Update alarm timer if it's on and timer > 0
                if os.path.exists(alarm_path):
                    with open(alarm_path, "r+", encoding="utf-8-sig") as alarm_file:
                        alarm_data = json.load(alarm_file)
                        if (
                            alarm_data.get("on_off") == "off"
                            and alarm_data.get("timer", 0) > 0
                        ):
                            alarm_data["timer"] -= 1
                            if alarm_data["timer"] <= 0:
                                alarm_data["timer"] = 0
                                alarm_data["on_off"] = "on"  # Turn on the alarm
                            alarm_file.seek(0)
                            json.dump(alarm_data, alarm_file, indent=4)
                            alarm_file.truncate()

                # Update air_condition timer if it's on and timer > 0
                if os.path.exists(air_condition_path):
                    with open(
                        air_condition_path, "r+", encoding="utf-8-sig"
                    ) as air_file:
                        air_data = json.load(air_file)
                        if (
                            air_data.get("on_off") == "on"
                            and air_data.get("timer", 0) > 0
                        ):
                            air_data["timer"] -= 1
                            if air_data["timer"] <= 0:
                                air_data["timer"] = 0
                                air_data["on_off"] = (
                                    "off"  # Turn off the air conditioner
                                )
                            air_file.seek(0)
                            json.dump(air_data, air_file, indent=4)
                            air_file.truncate()

            except Exception as e:
                print(f"Error updating timers: {str(e)}")

        # Sleep for a short period to avoid high CPU usage
        time.sleep(1)

# loadS the initial state when the component first mounts 
@app.route("/text")
def text():
    try:
        with open(data_path, "r", encoding="utf-8-sig") as file:
            data = json.load(file)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/alarm")
def alarm():
    try:
        with open(alarm_path, "r", encoding="utf-8-sig") as alarm_file:
            alarm_data = json.load(alarm_file)
        return jsonify(alarm_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/air_condition")
def air_condition():
    try:
        with open(air_condition_path, "r", encoding="utf-8-sig") as air_file:
            air_data = json.load(air_file)
        return jsonify(air_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/stream")
def stream():
    def generate():
        while True:
            try:
                with open(data_path, "r", encoding="utf-8-sig") as file:
                    data = json.load(file)
                yield f"data: {json.dumps(data)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
            time.sleep(1)  # Adjust the interval as needed

    return Response(generate(), mimetype="text/event-stream")


if __name__ == "__main__":
    # Start the timer update thread
    timer_thread = threading.Thread(target=update_timers, daemon=True)
    timer_thread.start()

    # Start the Flask application
    app.run(host="0.0.0.0", port=5000, debug=True)
