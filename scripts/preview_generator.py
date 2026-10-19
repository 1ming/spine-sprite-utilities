#!/usr/bin/env python3
"""
Script to generate animated sprite overlaid onto static background as a gif.
"""

from pathlib import Path
import subprocess
import argparse
from PIL import Image

DEFAULT_OUTPUT_DIR = "output_preview/"

# determine the number of frames inside a .apng
# return as a string containing the number of frames
# NOTE just using str as return type since we'll be passing it in as an arg anyway
def _get_num_frames(filename: Path) -> str:
    ffprobe_args = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-count_frames",
        "-show_entries",
        "stream=nb_read_frames",
        "-of",
        "csv=p=0",
        filename,
    ]
    output = subprocess.check_output(ffprobe_args)
    print(f"Running command with args: {ffprobe_args}")
    print(f"output: {output}")
    return output.strip().decode("utf-8")

# get image width and height
def _get_image_dimensions(filename: Path) -> tuple[int,int]:
    with Image.open(filename) as img:
        return img.size

# overlay .apng with a static .png background, convert and output as .gif
# scales to the background image size
def generate_overlaid_animation(input_file: Path, bg_file: Path, output_folder: Path):
    # get the number of frames in the input file
    num_frames_str = _get_num_frames(input_file)

    # get the dimensions of the background image
    width, height = _get_image_dimensions(bg_file)

    # final gif output path
    output_file = output_folder.joinpath(f"{input_file.stem}_{width}x{height}.gif")

    # intermediate apng path (will be converted to final gif)
    apng_file = output_file.with_suffix(".apng")

    # resize input .apng to match the background image
    # maintain aspect ratio and centering
    filter_arg = f"[1:v]scale={width}:{height}:force_original_aspect_ratio=decrease[fg];[0:v][fg]overlay=(W-w)/2:(H-h)/2:format=auto"
    ffmpeg_args = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        bg_file,
        "-ignore_loop",
        "1",
        "-i",
        input_file,
        "-filter_complex",
        filter_arg,
        "-frames:v",
        num_frames_str,
        "-plays",
        "0",
        apng_file,
    ]
    subprocess.run(ffmpeg_args, check=False)
    print(f"Running command with args: {ffmpeg_args}")

    _convert_to_gif(apng_file, output_file)
    print(f"Preview saved to: {output_file}")

# convert .apng to .gif
def _convert_to_gif(input_file: Path, output_file: Path):
    # convert apng to gif
    # filter with tailored palette for better colours
    # reference: https://www.michelleenos.com/notes/ffmpeg-gif-video/
    ffmpeg_args = [
        "ffmpeg",
        "-y",
        "-i",
        input_file,
        "-filter_complex",
        "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
        "-loop",
        "0",
        output_file,
    ]
    subprocess.run(ffmpeg_args, check=False)
    print(f"Running command with args: {ffmpeg_args}")
    print(f"Preview saved to: {output_file}")

def main(input_folder: Path, bg_file: Path, output_folder:Path):
    # create output dir
    output_folder.mkdir(parents=True, exist_ok=True)

    # for each .apng in the input folder, generate the resized version overlaid
    # onto bg
    for input_file in input_folder.iterdir():
        if input_file.is_file() and input_file.suffix == ".apng":
            generate_overlaid_animation(input_file, bg_file, output_folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="input directory containing original .apng files")
    parser.add_argument("bg_path", help="path to background .png file to use")
    parser.add_argument(
        "-o",
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="output directory for results",
    )
    args = parser.parse_args()

    main(Path(args.input_dir), Path(args.bg_path), Path(args.output_dir))