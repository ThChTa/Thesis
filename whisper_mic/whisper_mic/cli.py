import json
import os
import re
from datetime import datetime
from typing import Optional

import click
import spacy
import speech_recognition as sr
import torch
from nlp_module import process_text
from spacy.matcher import Matcher

from whisper_mic import WhisperMic


@click.command()
@click.option(
    "--model",
    default="base",
    help="Model to use",
    type=click.Choice(
        ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3", "turbo"]
    ),
)
@click.option(
    "--device",
    default=("cuda" if torch.cuda.is_available() else "cpu"),
    help="Device to use",
    type=click.Choice(["cpu", "cuda", "mps"]),
)
@click.option(
    "--english",
    default=False,
    help="Whether to use English model",
    is_flag=True,
    type=bool,
)
@click.option(
    "--verbose",
    default=False,
    help="Whether to print verbose output",
    is_flag=True,
    type=bool,
)
@click.option("--energy", default=300, help="Energy level for mic to detect", type=int)
@click.option(
    "--dynamic_energy",
    default=False,
    is_flag=True,
    help="Flag to enable dynamic energy",
    type=bool,
)
@click.option("--pause", default=0.8, help="Pause time before entry ends", type=float)
@click.option(
    "--save_file", default=False, help="Flag to save file", is_flag=True, type=bool
)
@click.option("--loop", default=False, help="Flag to loop", is_flag=True, type=bool)
@click.option(
    "--dictate",
    default=False,
    help="Flag to dictate (implies loop)",
    is_flag=True,
    type=bool,
)
@click.option("--mic_index", default=None, help="Mic index to use", type=int)
@click.option(
    "--list_devices",
    default=False,
    help="Flag to list devices",
    is_flag=True,
    type=bool,
)
def main(
    model: str,
    english: bool,
    verbose: bool,
    energy: int,
    pause: float,
    dynamic_energy: bool,
    save_file: bool,
    device: str,
    loop: bool,
    dictate: bool,
    mic_index: Optional[int],
    list_devices: bool,
) -> None:
    if list_devices:
        print("Possible devices: ", sr.Microphone.list_microphone_names())
        return

    mic = WhisperMic(
        model=model,
        english=english,
        verbose=verbose,
        energy=energy,
        pause=pause,
        dynamic_energy=dynamic_energy,
        save_file=save_file,
        device=device,
        mic_index=mic_index,
    )

    ############### Check if file exists (Air condition) ###############

    file_check_air_condition = "./air_condition.json"

    if os.path.exists(file_check_air_condition):
        # file exists
        temp = 1

    else:
        # file do not exists
        dictionary = {"on_off": "off", "temperature": 23, "timer": 0, "mode": "auto"}

        with open(file_check_air_condition, "w") as outfile:
            json.dump(dictionary, outfile, indent=4)

    ############### Check if file exists (Alarm) ###############

    file_check_alarm = "./alarm.json"

    if os.path.exists(file_check_alarm):
        # file exists
        temp = 1

    else:
        # file do not exists
        dictionary = {
            "on_off": "off",
            "battery": 100,
            "timer": 0,
            "motion_detection": "deactivated",
        }

        with open(file_check_alarm, "w") as outfile:
            json.dump(dictionary, outfile, indent=4)

    if loop:

        try:
            while True:
                result = mic.listen()
                print("You said2: " + result)
                if save_file:

                    process_text(result)

        except KeyboardInterrupt:
            print("Operation interrupted successfully")
        finally:
            if save_file:
                mic.file.close()
    else:
        try:
            result = mic.listen()
            print("You said: " + result)
            if save_file:
                with open(data_file_path, "a") as json_file:
                    json.dump({"data": [result]}, json_file)
                    json_file.write(
                        "\n"
                    )  # Add a newline after each entry for readability
        except KeyboardInterrupt:
            print("Operation interrupted successfully")


if __name__ == "__main__":
    main()
