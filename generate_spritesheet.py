#!/usr/bin/env python3
from pathlib import Path

# Godot configuration
GODOT_EXECUTABLE = "/Applications/Godot.app/Contents/MacOS/Godot"
GODOT_PROJECT_DIR = Path("godot-project/")
GODOT_RECORDINGS_DIR = Path("godot-recordings/")
GODOT_DATA_FILE = GODOT_RECORDINGS_DIR.joinpath("data.json")
SCENE_DIR = GODOT_PROJECT_DIR.joinpath("scenes")
FIXED_FPS = 24


DEFAULT_OUTPUT_DIR = "output/"

COMMON_ARGS = [
    "--path",
    GODOT_PROJECT_DIR,
    "--fixed-fps",
    FIXED_FPS,
]


class SpritesheetGenerator:
    def __init__(self, scene_name: str, output_dir: str):
        self.scene_name = scene_name
        self.output_dir = Path(output_dir).joinpath(self.scene_name)
        self.common_args = [
            GODOT_EXECUTABLE,
            *COMMON_ARGS,
            "--scene",
            GODOT_PROJECT_DIR.joinpath(f"{scene_name}.tscn"),
        ]

        # create output dir for this scene
        Path.mkdir(self.output_dir, parents=True, exist_ok=True)

    # run scene without args to get bounding box data and list of sprites and
    # animation names
    # Godot will output the data in a file in the default recording directory
    def get_scene_data(self) -> dict:
        pass

    # run godot project with a specific sprite and animation to get animation
    # frame recordings
    def record_animation_frames(self, sprite: str, animation: str):
        pass

    def run(self):
        pass

        # get bounding box
        # get sprites list

        # for each sprite
        # create directory for sprite
        # for each animation
        # create subdirectory for each animation
        # run godot to record animation frames
        # HACK delete last frame (MovieWriter always records an extra frame after requesting quit)
        # crop frames to bounding box size


if __name__ == "__main__":
    TEST_SCENE = "Scene1"
    spritesheet_generator = SpritesheetGenerator(TEST_SCENE, DEFAULT_OUTPUT_DIR)
    spritesheet_generator.run()
