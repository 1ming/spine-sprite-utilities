#!/usr/bin/env python3
"""
Script to convert Spine json data exports from an unknown version of Dragonbones
to be compatible for use with the Spine runtime
"""

# NOTE this is a one-off script for a specific scenario and may not apply to other versions
# tested with Spine 4.3 runtime GDExtension for Godot 4.7: https://en.esotericsoftware.com/spine-godot

import json
import argparse
from pathlib import Path

# folder for the output files generated
DEFAULT_OUTPUT_DIR = "output_spine_export/"

# spine version to convert files to match
SPINE_VERSION = "4.3.26"


# convert old spine json export to current format
# reference: https://en.esotericsoftware.com/spine-json-format
def convert_json(input_file: Path, output_dir: Path):
    data = None
    with open(input_file, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    # TODO validate input file

    # add spine version
    data["skeleton"]["spine"] = SPINE_VERSION

    # change "angle" to "value" in animations
    # NOTE for now just replace the string
    animation_data = json.dumps(data["animations"])
    animation_data = animation_data.replace("angle", "value")
    data["animations"] = json.loads(animation_data)

    # match current skins schema
    # change "skins" to a list
    # set a name for the default skin
    # fix hierarchy
    default_skin_data = data["skins"]["default"]
    data["skins"] = [
        {
            "name": "default",
            "attachments": default_skin_data,
        }
    ]

    # match new schema for deforms that's not reflected in the official docs
    # yet: https://github.com/EsotericSoftware/spine-runtimes/blob/1ad4e94bc3f16f4908a87a97d31e0de657f1788a/spine-godot/example-v4-extension/assets/spineboy/spineboy-pro.spine-json#L3573
    # official docs: https://en.esotericsoftware.com/spine-json-format#Animations
    animations = data["animations"]
    for name, animation_data in animations.items():
        deform_data = animation_data.get("deform")
        if deform_data is None:
            continue

        for skin, slot_data in deform_data.items():
            for slot, attachment_data in slot_data.items():
                for attachment, timeline in attachment_data.items():
                    # insert "deform" field just before timeline
                    deform_data[skin][slot][attachment] = {"deform": timeline}

        # change outer "deform" field to "attachments"
        del animation_data["deform"]
        animation_data["attachments"] = deform_data
        animations[name] = animation_data

    # write converted data to file
    output_file = output_dir.joinpath(input_file.name)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=4)

    # make a copy with a different extension to allow import into Godot
    # for info, see: https://en.esotericsoftware.com/spine-godot#Exporting-for-Godot
    godot_output_file = output_file.with_suffix(".spine-json")
    output_file.copy(godot_output_file)


def main(input_file: Path, output_dir: Path):
    convert_json(input_file, output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Input Spine json export file")
    parser.add_argument(
        "-o",
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="output directory for results",
    )
    args = parser.parse_args()

    main(Path(args.input_file), Path(args.output_dir))
