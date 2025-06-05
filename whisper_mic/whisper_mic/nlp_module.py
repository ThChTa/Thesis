import json
import re
from datetime import datetime

import spacy
from spacy.matcher import Matcher


# Function to process the text with the matchers
def process_text(result):

    data_file_path = "C:\\Users\\Thomas\\Desktop\\whisper_mic\\whisper_mic\\data.json"
    alarm_file_path = "C:\\Users\\Thomas\\Desktop\\whisper_mic\\whisper_mic\\alarm.json"
    air_condition_file_path = (
        "C:\\Users\\Thomas\\Desktop\\whisper_mic\\whisper_mic\\air_condition.json"
    )

    nlp = spacy.load("en_core_web_sm")

    # air condition patterns

    pattern_10 = [{"LOWER": "air"}, {"LOWER": "condition"}]

    pattern_1a = [
        {"LOWER": "air"},
        {"LOWER": "condition"},
        {"IS_PUNCT": True, "OP": "*"},  # Optional punctuation
        {"LOWER": "on"},
    ]

    pattern_1b = [
        {"LOWER": "air"},
        {"LOWER": "condition"},
        {"IS_PUNCT": True, "OP": "*"},  # Optional punctuation
        {"LOWER": "off"},
        {"IS_PUNCT": True, "OP": "*"},  # Optional punctuation
        {"LOWER": "now"},
    ]

    pattern_1c = [
        {"LOWER": "air"},
        {"LOWER": "condition"},
        {"IS_PUNCT": True, "OP": "*"},  # Optional punctuation
        {"TEXT": {"REGEX": "(1[6-9]|2[0-9]|30)"}},  # Match numbers from 16 to 30
        {"LOWER": "degrees"},
    ]

    pattern_1d = [
        {"LOWER": "air"},
        {"LOWER": "condition"},
        {"IS_PUNCT": True, "OP": "*"},  # Optional punctuation
        {"LOWER": "off"},
        {"LOWER": "in"},
        {"TEXT": {"REGEX": "\\d+"}},  # Match any digit
        {"LOWER": "minutes"},
    ]

    mode = ["Cool", "cool", "Heat", "heat", "Auto", "auto"]

    pattern_1e = [
        {"LOWER": "air"},
        {"LOWER": "condition"},
        {"IS_PUNCT": True, "OP": "*"},  # Optional punctuation
        {"LEMMA": {"IN": mode}},  # Use LEMMA for base form matching
    ]

    ####################################################################################################

    # home alarm patterns
    pattern_20 = [{"LOWER": "alarm"}]

    pattern_2a = [
        {"LOWER": "alarm"},
        {"IS_PUNCT": True, "OP": "*"},  # Optional punctuation
        {"LOWER": "on"},  
    ]

    pattern_2b = [
        {"LOWER": "alarm"},
        {"IS_PUNCT": True, "OP": "*"},  # Optional punctuation
        {"LOWER": "off"},  
    ]

    pattern_2c = [
        {"LOWER": "alarm"},
        {"IS_PUNCT": True, "OP": "*"},  # Optional punctuation
        {"LOWER": "in"},
        {"TEXT": {"REGEX": "\\d+"}},  # Match any digit
        {"LOWER": "minutes"},
    ]

    pattern_2d = [
        {"LOWER": "alarm"},
        {"IS_PUNCT": True, "OP": "*"},  # Optional punctuation
        {"LOWER": "status"},
    ]

    pattern_2e = [
        {"LOWER": "alarm"},
        {"IS_PUNCT": True, "OP": "*"},  # Optional punctuation
        {"LOWER": "battery"},
    ]

    pattern_2f = [
        {"LOWER": "alarm"},
        {"IS_PUNCT": True, "OP": "*"},  # Optional punctuation
        {"LOWER": "activate"},
        {"LOWER": "motion"},
        {"LOWER": "detection"},
    ]

    pattern_2g = [
        {"LOWER": "alarm"},
        {"IS_PUNCT": True, "OP": "*"},  # Optional punctuation
        {"LOWER": "deactivate"},
        {"LOWER": "motion"},
        {"LOWER": "detection"},
    ]

    ###################### Define actions for air condition ######################

    def on_match_pattern_10(
        matcher_for_air_condition, doc, i, non_matches_for_air_condition
    ):  # pattern which do not match the commands
        # Load existing data from the JSON file
        with open(data_file_path, "r") as json_file:
            data = json.load(json_file)

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        for match in matches_for_air_condition[:10]:
            t = doc[match[1] : match[2]].text
            print(t)
            # Append each match to the data structure
            data["data"].append(
                {
                    "original_text": result,
                    "nlp_text": t,
                    "device": "air condition",
                    "flag": "correct",
                    "time": current_time,
                }
            )

        if not matches_for_air_condition:  # If there are no matches
            for non_match in non_matches_for_air_condition:
                non_t = doc[non_match[1] : non_match[2]].text
                # Append each non-match to the data structure
                data["data"].append(
                    {
                        "original_text": result,
                        "nlp_text": non_t,
                        "device": "air condition",
                        "flag": "incorrect",
                        "time": current_time,
                    }
                )

        # Write the updated data back to the JSON file
        with open(data_file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

    def on_match_pattern_1a(
        matcher_for_air_condition, doc, i, matches_for_air_condition
    ):  # pattern_1a
        # Load existing data from the JSON file
        print("Pattern 1a triggered")  # Add this print statement
        with open(
            air_condition_file_path,
            "r",
        ) as file:
            data = json.load(file)

        for match in matches_for_air_condition[:10]:
            t = doc[match[1] : match[2]].text
            var = t.split(" ")[2]
            data["on_off"] = "on"  # Change this to the desired value

        with open(
            air_condition_file_path,
            "w",
        ) as file:
            json.dump(data, file, indent=4)
            # Write the updated data back to the JSON file

    def on_match_pattern_1b(
        matcher_for_air_condition, doc, i, matches_for_air_condition
    ):  # pattern_1b
        # Load existing data from the JSON file
        print("Pattern 1b triggered")  # Add this print statement
        with open(
            air_condition_file_path,
            "r",
        ) as file:
            data = json.load(file)

        for match in matches_for_air_condition[:10]:
            t = doc[match[1] : match[2]].text
            var = t.split(" ")[2]
            data["on_off"] = "off"  # Change this to the desired value
            data["timer"] = 0

        with open(
            air_condition_file_path,
            "w",
        ) as file:
            json.dump(data, file, indent=4)
            # Write the updated data back to the JSON file

    def on_match_pattern_1c(
        matcher_for_air_condition, doc, i, matches_for_air_condition
    ):
        print("Pattern 1c triggered")  # Add this print statement
        # Load existing data from the JSON file
        with open(air_condition_file_path, "r") as file:
            data = json.load(file)

        if data.get("on_off", "").lower() == "on":  # Check if the air condition is ON
            for match in matches_for_air_condition[:10]:
                t = doc[match[1] : match[2]].text
                temperature_match = re.search(r"\d+", t)  # Extract digits from the matched text
                if temperature_match:
                    temperature = int(temperature_match.group())  # Convert the matched digits to integer
                    data["temperature"] = temperature  # Update the temperature value in the JSON

            # Save changes only if temperature was updated
            with open(air_condition_file_path, "w") as file:
                json.dump(data, file, indent=4)
        else:
            print("Air condition is OFF. Temperature not updated.")


    def on_match_pattern_1d(
        matcher_for_air_condition, doc, i, matches_for_air_condition
    ):
        print("Pattern 1d triggered")  # Debug print

        # Load existing data from the JSON file
        with open(air_condition_file_path, "r") as file:
            data = json.load(file)

        # Check if air condition is ON (case-insensitive)
        if data.get("on_off", "").lower() == "on":
            for match in matches_for_air_condition[:10]:
                t = doc[match[1] : match[2]].text
                split_t = t.split(" ")
                if len(split_t) >= 5:
                    try:
                        var = int(split_t[4])
                        data["timer"] = var  # Update the timer
                    except ValueError:
                        print(f"Could not convert '{split_t[4]}' to int.")
            
            # Save changes only if ON
            with open(air_condition_file_path, "w") as file:
                json.dump(data, file, indent=4)
        else:
            print("Air condition is OFF. Timer not updated.")


    def on_match_pattern_1e(
        matcher_for_air_condition, doc, i, matches_for_air_condition
    ):  # pattern_1e
        print("Pattern 1e triggered")  # Debug print

        # Load existing data from the JSON file
        with open(air_condition_file_path, "r") as file:
            data = json.load(file)

        # Check if air condition is ON
        if data.get("on_off", "").lower() == "on":
            for match in matches_for_air_condition[:10]:
                t = doc[match[1] : match[2]].text
                split_t = t.split(" ")
                if len(split_t) >= 3:
                    var = split_t[2]
                    data["mode"] = var  # Update mode
            # Save only if ON
            with open(air_condition_file_path, "w") as file:
                json.dump(data, file, indent=4)
        else:
            print("Air condition is OFF. Mode not updated.")


    ###################### Define actions for alarm ######################

    def on_match_pattern_20(matcher_for_alarm, doc, i, non_matches_for_alarm):
        # Load existing data from the JSON file
        with open(data_file_path, "r") as json_file:
            data = json.load(json_file)

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        for match in matches_for_alarm[:10]:
            t = doc[match[1] : match[2]].text
            print(t)
            # Append each match to the data structure
            data["data"].append(
                {
                    "original_text": result,
                    "nlp_text": t,
                    "device": "alarm",
                    "flag": "correct",
                    "time": current_time,
                }
            )

        if not matches_for_alarm:  # If there are no matches
            for non_match in non_matches_for_alarm:
                non_t = doc[non_match[1] : non_match[2]].text
                # Append each non-match to the data structure
                data["data"].append(
                    {
                        "original_text": result,
                        "nlp_text": non_t,
                        "device": "alarm",
                        "flag": "incorrect",
                        "time": current_time,
                    }
                )

        # Write the updated data back to the JSON file
        with open(data_file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

    def on_match_pattern_2a(matcher_for_alarm, doc, i, matches_for_alarm):  # pattern_2a
        # Load existing data from the JSON file
        print("Pattern 2a triggered")  # Add this print statement
        with open(
            alarm_file_path,
            "r",
        ) as file:
            data = json.load(file)

        for match in matches_for_alarm[:10]:
            t = doc[match[1] : match[2]].text
            var = t.split(" ")[1]
            data["on_off"] = var  # Change this to the desired value
            data["timer"] = 0

        with open(
            alarm_file_path,
            "w",
        ) as file:
            json.dump(data, file, indent=4)
            # Write the updated data back to the JSON file

    def on_match_pattern_2b(matcher_for_alarm, doc, i, matches_for_alarm):  # pattern_2b
        # Load existing data from the JSON file
        print("Pattern 2b triggered")  # Add this print statement
        with open(
            alarm_file_path,
            "r",
        ) as file:
            data = json.load(file)

        for match in matches_for_alarm[:10]:
            t = doc[match[1] : match[2]].text
            var = t.split(" ")[1]
            data["on_off"] = var  # Change this to the desired value

        with open(
            alarm_file_path,
            "w",
        ) as file:
            json.dump(data, file, indent=4)
            # Write the updated data back to the JSON file

    def on_match_pattern_2c(matcher_for_alarm, doc, i, matches_for_alarm):  # pattern_2c
        print("Pattern 2c triggered")  # Add this print statement

        # Load existing data from the JSON file
        with open(alarm_file_path, "r") as file:
            data = json.load(file)

        # Check if alarm is OFF (case-insensitive)
        if data.get("on_off", "").lower() == "off":
            for match in matches_for_alarm[:10]:
                t = doc[match[1] : match[2]].text
                split_t = t.split(" ")
                if len(split_t) >= 3:
                    try:
                        var = int(split_t[2])
                        data["timer"] = var  # Update timer only if alarm is off
                    except ValueError:
                        print(f"Could not convert '{split_t[2]}' to int.")

            with open(alarm_file_path, "w") as file:
                json.dump(data, file, indent=4)
        else:
            print("Alarm is ON. Timer not updated.")


    def on_match_pattern_2f(matcher_for_alarm, doc, i, matches_for_alarm):  # pattern_2f
        # Load existing data from the JSON file
        print("Pattern 2f triggered")  # Add this print statement
        with open(
            alarm_file_path,
            "r",
        ) as file:
            data = json.load(file)

            data["motion_detection"] = "activated"  # Change this to the desired value

        with open(
            alarm_file_path,
            "w",
        ) as file:
            json.dump(data, file, indent=4)
            # Write the updated data back to the JSON file

    def on_match_pattern_2g(matcher_for_alarm, doc, i, matches_for_alarm):  # pattern_2g
        # Load existing data from the JSON file
        print("Pattern 2g triggered")  # Add this print statement
        with open(
            alarm_file_path,
            "r",
        ) as file:
            data = json.load(file)

            data["motion_detection"] = "deactivated"  # Change this to the desired value

        with open(
            alarm_file_path,
            "w",
        ) as file:
            json.dump(data, file, indent=4)
            # Write the updated data back to the JSON file

    matcher_for_air_condition = Matcher(nlp.vocab)
    matcher_for_alarm = Matcher(nlp.vocab)

    non_matcher_for_air_condition = Matcher(nlp.vocab)
    non_matcher_for_alarm = Matcher(nlp.vocab)

    matcher_for_air_condition.add(
        "Pattern_1a",
        [pattern_1a],
        greedy="LONGEST",
        on_match=on_match_pattern_1a,
    )
    matcher_for_air_condition.add(
        "Pattern_1b",
        [pattern_1b],
        greedy="LONGEST",
        on_match=on_match_pattern_1b,
    )
    matcher_for_air_condition.add(
        "Pattern_1c",
        [pattern_1c],
        greedy="LONGEST",
        on_match=on_match_pattern_1c,
    )
    matcher_for_air_condition.add(
        "Pattern_1d",
        [pattern_1d],
        greedy="LONGEST",
        on_match=on_match_pattern_1d,
    )
    matcher_for_air_condition.add(
        "Pattern_1e",
        [pattern_1e],
        greedy="LONGEST",
        on_match=on_match_pattern_1e,
    )

    matcher_for_alarm.add(
        "Pattern_2a",
        [pattern_2a],
        greedy="LONGEST",
        on_match=on_match_pattern_2a,
    )
    matcher_for_alarm.add(
        "Pattern_2b",
        [pattern_2b],
        greedy="LONGEST",
        on_match=on_match_pattern_2b,
    )
    matcher_for_alarm.add(
        "Pattern_2c",
        [pattern_2c],
        greedy="LONGEST",
        on_match=on_match_pattern_2c,
    )
    # matcher_for_alarm.add("Pattern_2d", [pattern_2d], greedy="LONGEST",on_match=on_match_pattern_1d)
    # matcher_for_alarm.add("Pattern_2e", [pattern_2e], greedy="LONGEST",on_match=on_match_pattern_1e)
    matcher_for_alarm.add(
        "Pattern_2f",
        [pattern_2f],
        greedy="LONGEST",
        on_match=on_match_pattern_2f,
    )
    matcher_for_alarm.add(
        "Pattern_2g",
        [pattern_2g],
        greedy="LONGEST",
        on_match=on_match_pattern_2g,
    )

    non_matcher_for_air_condition.add(
        "NON_PROPER_NOUNS_FOR_AIR_CONDITION",
        [pattern_10],
        greedy="LONGEST",
        on_match=on_match_pattern_10,
    )
    non_matcher_for_alarm.add(
        "NON_PROPER_NOUNS_FOR_ALARM",
        [pattern_20],
        greedy="LONGEST",
        on_match=on_match_pattern_20,
    )

    doc = nlp(result)

    matches_for_air_condition = matcher_for_air_condition(doc)
    matches_for_alarm = matcher_for_alarm(doc)

    non_matches_for_air_condition = non_matcher_for_air_condition(doc)
    non_matches_for_alarm = non_matcher_for_alarm(doc)
