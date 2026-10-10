#!/usr/bin/env python3
from pathlib import Path
import subprocess
import argparse

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

    # run scene without args to get bounding box data and list of sprites and
    # animation names
    # Godot will output the data in a file in the default recording directory
    def get_scene_data(self) -> dict:
        print(f"Running Godot with args: {self.common_args}")
        subprocess.run(self.common_args, check=False)

    # run godot project with a specific sprite and animation to get animation
    # frame recordings
    def record_animation_frames(self, sprite: str, animation: str):
        pass

    def run(self):
        pass

        # get bounding box
        # get sprites list
        self.get_scene_data()

        # for each sprite
        # create directory for sprite
        # for each animation
        # create subdirectory for each animation
        # run godot to record animation frames
        # HACK delete last frame (MovieWriter always records an extra frame after requesting quit)
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
    args = parser.parse_args()

    spritesheet_generator = SpritesheetGenerator(args.scene, args.output_dir)
    spritesheet_generator.run()
