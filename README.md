# Spine Sprite Utilities
Godot project and Python scripts to automate the generation of spritesheets from 2D assets with Spine data.

## Spritesheet generator
Script to generate spritesheets for a set of Spine sprites in a Godot scene.

Multiple Spine directional sprites can be included in the Godot scene. The base Godot scene contains a script to compute a maximum bounding box that fits all the animations for all directional sprites within the scene.

Usage:
```
usage: generate_spritesheet.py [-h] [-o OUTPUT_DIR] [-a SPRITE ANIMATION] scene

positional arguments:
  scene                 name of Godot scene containing SpineSprites

options:
  -h, --help            show this help message and exit
  -o, --output-dir OUTPUT_DIR
                        output directory for results
  -a, --animation SPRITE ANIMATION
                        only generate spritesheet for a specific sprite and animation. specify sprite name followed
                        by animation name
```
`scene` should match the name of a `.tscn` file (without the extension) in `godot-project/scenes/`.
For example, use `scene1` if your scene file is `godot-project/scenes/scene1.tscn`.

## Other scripts
Located in the `scripts/` folder, to be used to automate other relevant tasks.

### GIF preview generator
Script to generate animated sprites overlaid onto static background as a gif.

Usage:
```
usage: preview_generator.py [-h] [-o OUTPUT_DIR] input_dir bg_path

positional arguments:
  input_dir             input directory containing original .apng files
  bg_path               path to background .png file to use

options:
  -h, --help            show this help message and exit
  -o, --output-dir OUTPUT_DIR
                        output directory for results
```

### Spine export JSON converter
Script to convert Spine json data exports from an unknown version of Dragonbones
to be compatible for use with the Spine runtime. More of a one-off script but keeping it here for reference.
Usage:
```
usage: convert_spine.py [-h] [-o OUTPUT_DIR] input_file

positional arguments:
  input_file            Input Spine json export file

options:
  -h, --help            show this help message and exit
  -o, --output-dir OUTPUT_DIR
                        output directory for results
```
