#!/usr/bin/env python3
from pathlib import Path
from dataclasses import dataclass
import subprocess
import argparse
import json
import time

from PIL import Image

# Godot configuration
FIXED_FPS = 24
GODOT_EXECUTABLE = "/Applications/Godot.app/Contents/MacOS/Godot"
GODOT_PROJECT_DIR = Path("godot-project/")
GODOT_RECORDINGS_DIR = Path("godot-recordings/")

DEFAULT_OUTPUT_DIR = "output/"

COMMON_GODOT_ARGS = [
    "--path",
    GODOT_PROJECT_DIR,
    "--fixed-fps",
    str(FIXED_FPS),
]


@dataclass
class SheetConfig:
    padding: int = 10
    max_columns: int = 8


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
            *COMMON_GODOT_ARGS,
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
        # ensure Godot recordings directory for movie-writer exists
        # as we don't currently pass it any directory when we aren't recording
        # NOTE could add this as a CLI option later on the godot project
        GODOT_RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
        godot_data_file = GODOT_RECORDINGS_DIR.joinpath("data.json")

        # check if data file already exists
        data_file = self.output_dir.joinpath("data.json")
        if data_file.exists():
            print(f"Using existing data file: {data_file}")
        else:
            # run Godot with no args to generate data file
            print(f"Running Godot with args: {self.common_args}")
            subprocess.run(self.common_args, check=False)

            # move data file to output dir
            godot_data_file.move(data_file)

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
    def _record_animation_frames(self, sprite: str, animation: str) -> Path:
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
        self._crop_frames(images_dir)

        return images_dir

    # crop all images within a directory using ffmpeg
    # expects naming scheme to be raw_frame%8d.png (following godot's output convention for PNG recordings)
    # outputs cropped files as: frame%8d.png
    # raw images are deleted after cropping
    def _crop_frames(self, images_dir: Path):
        input_file = f"{images_dir.joinpath("raw_frame%08d.png")}"
        output_file = f"{images_dir.joinpath("frame%08d.png")}"
        crop_options = f"crop={self.crop_config.width}:{self.crop_config.height}:{self.crop_config.x}:{self.crop_config.y}"
        ffmpeg_args = [
            "ffmpeg",
            "-y",
            "-i",
            input_file,
            "-vf",
            crop_options,
            "-start_number",
            "0",
            output_file,
        ]
        print(f"Running command with args: {ffmpeg_args}")

        # crop images
        subprocess.run(ffmpeg_args, check=False)

        # delete raw files
        for file in images_dir.glob("raw_frame*.png"):
            if file.is_file():
                file.unlink()

    # create animated png
    def _create_previews(self, images_dir: Path) -> list[Path]:
        output_files = []
        # generated animated png from frames
        output_dir = images_dir.parent
        input_file = f"{images_dir.joinpath("frame%08d.png")}"
        output_file = f"{output_dir.joinpath("preview.apng")}"
        ffmpeg_args = [
            "ffmpeg",
            "-y",
            "-framerate",
            str(FIXED_FPS),
            "-i",
            input_file,
            "-plays",
            "0",
            output_file,
        ]
        subprocess.run(ffmpeg_args, check=False)
        print(f"Running command with args: {ffmpeg_args}")
        print(f"Preview saved to: {output_file}")
        output_files.append(output_file)

        # convert apng to gif
        # filter with tailored palette for better colours
        # reference: https://www.michelleenos.com/notes/ffmpeg-gif-video/
        input_file = output_file
        output_file = f"{output_dir.joinpath("preview.gif")}"
        ffmpeg_args = [
            "ffmpeg",
            "-y",
            "-i",
            input_file,
            "-filter_complex",
            "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
            output_file,
        ]
        subprocess.run(ffmpeg_args, check=False)
        print(f"Running command with args: {ffmpeg_args}")
        print(f"Preview saved to: {output_file}")
        output_files.append(output_file)

        return output_files

    # combine individual frames together to construct spritesheet
    def _construct_spritesheet(self, images_dir: Path, filename: str = None) -> Path:
        if filename is None:
            filename = "sheet.png"
        output_file = images_dir.parent.joinpath(filename)

        # calculate size for sheet based on cropped image config and number of frames
        frames = sorted(images_dir.iterdir())
        num_images = len(frames)

        # calculate of rows and columns
        columns = min(self.sheet_config.max_columns, num_images)
        rows = num_images // columns
        if num_images % columns != 0:
            rows += 1

        # sheet size
        width = self.crop_config.width * columns
        height = self.crop_config.height * rows

        # create new image for sheet that fits all images
        sheet = Image.new("RGBA", (width, height))

        # paste individual frames onto sheet
        for i, frame in enumerate(frames):
            # compute target position for pasting (top left corner)
            row = i // columns
            col = i % columns
            pos = (col * self.crop_config.width, row * self.crop_config.height)

            with Image.open(frame, "r") as frame_img:
                sheet.paste(frame_img, pos)

        # save sheet to file
        sheet.save(output_file)
        print(f"Spritesheet saved to: {output_file}")

    # record and create spritesheet for a specific animation
    def generate_spritesheet(self, sprite: str, animation: str):
        image_dir = self._record_animation_frames(sprite, animation)
        self._create_previews(image_dir)
        self._construct_spritesheet(
            image_dir, f"{sprite.lower()}-{animation.lower()}_sheet.png"
        )

    # generate spritesheets for all sprites and their animations
    # within the specified Godot scene
    # if data file containing bounding box and animations list doesn't exist, it will be generated by running through them in Godot
    # if a specific animation is specified, will only record and
    # generate sheet for that animation
    def run(self, animation_args: tuple[str, str] = None):
        # get bounding box and animations list
        data = self.get_scene_data()

        if animation_args is None:
            # generate sheets for all directions and animations
            direction_sprites = data["sprites"]
            for sprite in direction_sprites:
                for animation in direction_sprites[sprite]:
                    self.generate_spritesheet(sprite, animation)

        else:
            # only generate sheet for a specific animation
            self.generate_spritesheet(*animation_args)


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
        help="only generate spritesheet for a specific sprite and animation. \
            specify sprite name followed by animation name",
    )
    args = parser.parse_args()

    spritesheet_generator = SpritesheetGenerator(args.scene, args.output_dir)
    spritesheet_generator.run(args.animation)
