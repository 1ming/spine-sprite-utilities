#!/usr/bin/env python3
from pathlib import Path
import subprocess
import argparse
import json
import time

# Godot configuration
GODOT_EXECUTABLE = "/Applications/Godot.app/Contents/MacOS/Godot"
GODOT_PROJECT_DIR = Path("godot-project/")
GODOT_RECORDINGS_DIR = Path("godot-recordings/")
GODOT_DATA_FILE = GODOT_RECORDINGS_DIR.joinpath("data.json")
FIXED_FPS = 24


DEFAULT_OUTPUT_DIR = "output/"

COMMON_ARGS = [
    "--path",
    GODOT_PROJECT_DIR,
    "--fixed-fps",
    str(FIXED_FPS),
]


class SpritesheetGenerator:
    def __init__(self, scene_name: str, output_dir: str):
        self.scene_name = scene_name
        self.output_dir = Path(output_dir).joinpath(self.scene_name)
        self.common_args = [
            GODOT_EXECUTABLE,
            *COMMON_ARGS,
            "--scene",
            f"scenes/{scene_name}.tscn",
        ]

        # create output dir for this scene
        Path.mkdir(self.output_dir, parents=True, exist_ok=True)

        # create sub-directory for Godot's recording output
        self.recordings_dir = GODOT_RECORDINGS_DIR.joinpath(self.scene_name)
        try:
            Path.mkdir(self.recordings_dir, parents=True)
        except FileExistsError:
            # clear out contents if it already exists
            for file in self.recordings_dir.iterdir():
                if file.is_file():
                    file.unlink()

    # run scene without args to get bounding box data and list of sprites and
    # animation names
    # Godot will output the data in a file in the default recording directory
    def get_scene_data(self) -> dict:
        # run Godot with no args to generate data file
        print(f"Running Godot with args: {self.common_args}")
        subprocess.run(self.common_args, check=False)

        # extract data to dictionary
        data = {}
        with open(GODOT_DATA_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        # move data file to output dir
        GODOT_DATA_FILE.move_into(self.output_dir)
        return data

    # run godot project with a specific sprite and animation to get animation
    # frame recordings
    def record_animation_frames(self, sprite: str, animation: str) -> list[Path]:
        # run Godot with args for recording a specific animation
        args = [
            *self.common_args,
            "--write-movie",
            # using abs path to store outside Godot's project dir
            self.recordings_dir.joinpath("frame.png").absolute(),
            "--",
            sprite,
            animation,
        ]
        print(f"Running Godot with args: {args}")
        subprocess.run(args, check=False)

        # TODO add check to ensure files have been written. for now just use a sleep
        time.sleep(1)

        # HACK delete last animation frame image
        # Godot MovieWriter always records an extra frame after requesting quit
        # the sprite is also hidden in that frame to make it easy to identify
        frames = sorted(self.recordings_dir.glob("*.png"))
        extra_frame = frames.pop()
        print(f"Removing extra frame: {extra_frame}")
        extra_frame.unlink()

        # remove wav file(s)
        wav_files = self.recordings_dir.glob("*.wav")
        for file in wav_files:
            if file.is_file():
                print(f"Removing audio file: {file}")
                file.unlink()
        return frames

    def run(self):
        # get bounding box
        # get sprites list
        data = self.get_scene_data()

        # for each sprite
        # create directory for sprite
        # for each animation
        # create subdirectory for each animation
        # run godot to record animation frames
        # crop frames to bounding box size


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("scene", help="name of Godot scene containing SpineSprites")
    parser.add_argument(
        "-o",
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="output directory for results",
    )
    parser.add_argument(
        "-a",
        "--animation",
        nargs=2,
        help="only generate spritesheet for a specific sprite and animation. specify sprite name followed by animation name",
    )
    args = parser.parse_args()

    spritesheet_generator = SpritesheetGenerator(args.scene, args.output_dir)

    if args.animation is None:
        spritesheet_generator.run()
    else:
        # only generate spritesheet for a specific animation
        spritesheet_generator.record_animation_frames(*args.animation)
