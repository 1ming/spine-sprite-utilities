#!/usr/bin/env python3
from pathlib import Path
from dataclasses import dataclass
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


@dataclass
class SheetConfig:
    padding: int = 10
    columns: int = 5


@dataclass
class CropConfig:
    # size
    width: int
    height: int

    # origin
    x: int
    y: int


class SpritesheetGenerator:
    def __init__(
        self,
        scene_name: str,
        output_dir: str,
        sheet_config: SheetConfig = SheetConfig(),
    ):
        self.scene_name = scene_name
        self.output_dir = Path(output_dir).joinpath(self.scene_name)
        self.sheet_config = sheet_config
        self.common_args = [
            GODOT_EXECUTABLE,
            *COMMON_ARGS,
            "--scene",
            f"scenes/{scene_name}.tscn",
        ]

        # store data about max bounding box and list of animations form scene
        self.raw_data = {}
        self.crop_config: CropConfig

        # create output dir for this scene
        Path.mkdir(self.output_dir, parents=True, exist_ok=True)

    # run scene without args to get bounding box data and list of sprites and
    # animation names
    # Godot will output the data in a file in the default recording directory
    def get_scene_data(self) -> dict:
        # check if data file already exists
        data_file = self.output_dir.joinpath("data.json")
        if data_file.exists():
            print(f"Using existing data file: {data_file}")
        else:
            # run Godot with no args to generate data file
            print(f"Running Godot with args: {self.common_args}")
            subprocess.run(self.common_args, check=False)

            # move data file to output dir
            GODOT_DATA_FILE.move(data_file)

        # extract data to dictionary
        with open(data_file, "r", encoding="utf-8") as fh:
            self.raw_data = json.load(fh)

        # populate crop config from data
        bounds_data = self.raw_data["bounds"]
        self.crop_config = CropConfig(
            # round width and height to nearest 10
            # NOTE due to rounding padding is only used as a rough guide
            width=round(
                int(
                    bounds_data["width"] + self.sheet_config.padding,
                ),
                -1,
            ),
            height=round(int(bounds_data["height"] + self.sheet_config.padding), -1),
            x=round(bounds_data["x"]),
            y=round(bounds_data["y"]),
        )

        return self.raw_data

    # run godot project with a specific sprite and animation to get animation
    # frame recordings
    def record_animation_frames(self, sprite: str, animation: str) -> Path:
        # set up output dir
        images_dir = self.output_dir.joinpath(sprite, animation, "images")
        try:
            images_dir.mkdir(parents=True)
        except FileExistsError:
            # clear out contents if it already exists
            for file in images_dir.iterdir():
                if file.is_file():
                    file.unlink()

        # run Godot with args for recording a specific animation
        recording_args = [
            *self.common_args,
            "--write-movie",
            # using abs path to store outside Godot's project dir
            images_dir.joinpath("raw_frame.png").absolute(),
            "--",
            sprite,
            animation,
        ]
        print(f"Running Godot with args: {recording_args}")
        subprocess.run(recording_args, check=False)

        # TODO add check to ensure files have been written. for now just use a sleep
        time.sleep(1)

        # HACK delete last animation frame image
        # Godot MovieWriter always records an extra frame after requesting quit
        # the sprite is also hidden in that frame to make it easy to identify
        frames = sorted(images_dir.glob("*.png"))
        extra_frame = frames.pop()
        print(f"Removing extra frame: {extra_frame}")
        extra_frame.unlink()

        # remove wav file(s)
        wav_files = images_dir.glob("*.wav")
        for file in wav_files:
            if file.is_file():
                print(f"Removing audio file: {file}")
                file.unlink()

        # crop frames to bounding box size
        self.crop_frames(images_dir)

        return images_dir

    # crop all images within a directory using ffmpeg
    # expects naming scheme to be raw_frame%8d.png (following godot's output convention for PNG recordings)
    # outputs cropped files as: frame%8d.png
    # raw images are deleted after cropping
    def crop_frames(self, images_dir: Path):
        ffmpeg_args = [
            "ffmpeg",
            "-i",
            f"{images_dir.joinpath("raw_frame%08d.png")}",
            "-vf",
            f"crop={self.crop_config.width}:{self.crop_config.height}:{self.crop_config.x}:{self.crop_config.y}",
            "-start_number",
            "0",
            f"{images_dir.joinpath("frame%08d.png")}",
        ]
        print(f"Running command with args: {ffmpeg_args}")

        # crop images
        subprocess.run(ffmpeg_args, check=False)

        # delete raw files
        for file in images_dir.glob("raw_frame*.png"):
            if file.is_file():
                file.unlink()

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

    spritesheet_generator.run()

    if args.animation is not None:
        # only generate spritesheet for a specific animation
        spritesheet_generator.record_animation_frames(*args.animation)
