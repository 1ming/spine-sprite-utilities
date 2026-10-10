#!/usr/bin/env python3
from pathlib import Path

# Godot configuration
GODOT_EXECUTABLE = "/Applications/Godot.app/Contents/MacOS/Godot"
GODOT_PROJECT_DIR = Path("godot-project/")
SCENE_DIR = GODOT_PROJECT_DIR.joinpath("scenes")
FIXED_FPS = 24


OUTPUT_DIR = Path("output/")

COMMON_ARGS = [
    "--path",
    GODOT_PROJECT_DIR,
    "--fixed-fps",
    FIXED_FPS,
]


def main(scene_name: str):
    # create output dir for this scene
    Path.mkdir(OUTPUT_DIR.joinpath(scene_name), parents=True, exist_ok=True)

    # get bounding box
    # get sprites list

    # for each sprite
    # create directory for sprite
    # for each animation
    # create subdirectory for each animation
    # run godot to record animation frames
    # HACK delete last frame (MovieWriter always records an extra frame after requesting quit)
    # crop frames to bounding box size


# run scene without args to get bounding box data and list of sprites and
# animation names
def get_scene_data(scene_name: str) -> dict:
    pass


# run godot project with a specific sprite and animation to get animation
# frame recordings
def record_animation_frames(
    scene_name: str, sprite: str, animation: str, output_dir: str
):
    pass


if __name__ == "__main__":
    TEST_SCENE = "Scene1"
    main(TEST_SCENE)
