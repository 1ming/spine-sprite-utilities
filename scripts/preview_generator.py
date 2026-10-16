#!/usr/bin/env python3
"""
Script to generate animated sprite overlaid onto static background as a gif.
"""

from pathlib import Path
import subprocess

# NOTE assume bg image chosen is already this size
WIDTH = 160
HEIGHT = 160

# determine the number of frames inside a .apng
# return as a string containing the number of frames
# NOTE just using str as return type since we'll be passing it in as an arg anyway
def _get_num_frames(filename: Path) -> str:
    args = [
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
    output = subprocess.check_output(args)
    print(f"Running command with args: {args}")
    print(f"output: {output}")
    return output.strip().decode("utf-8")


# overlay .apng with a static .png background
def generate_overlaid_animation(input_file: Path, bg_file: Path, output_file: Path):
    # get the number of frames in the input file
    num_frames_str = _get_num_frames(input_file)

    # intermediate apng file
    apng_file = output_file.with_suffix(".apng")

    filter_arg = f"[1:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease[fg];[0:v][fg]overlay=(W-w)/2:(H-h)/2:format=auto"

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


if __name__ == "__main__":
    pass