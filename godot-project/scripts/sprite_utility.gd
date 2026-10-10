## Utility to aid processing SpineSprites into frames for spritesheets alongside
## an external python script to pass arguments to it
## To use, create a new inherited scene from this base scene and add a separate
## SpineSprite for each direction sprite as its children
## 
## Currently does the following:
## - Get the maximum bounding across all child SpineSprites (e.g. front, back)
## and their animations (used when no CLI args are supplied)
## - Play a specific animation for a specific sprite and exit (used to get all
## the frames for a specific animation)
## CLI args format: <sprite_name> <animation_name>
## where `sprite_name` is the name of a child node of the type SpineSprite
## and `animation_name` is a name of one of the animations for the sprite
extends Node2D

var sprite: SpineSprite
var frame_num: int = 0

@onready var max_bound_checker: Node = %MaxBoundChecker

func _ready() -> void:
	# NOTE currently just using args to determine which direction and animation
	# to use
	# if no args then get max bounds
	var args := OS.get_cmdline_user_args()
	if not args:
		print("no args specified: Do max bounds check")
	elif args.size() == 2:
		print("play animation: ", args)

		var sprite_name = args[0]
		var animation_name = args[1]
		
		# remove the max bound checker when we're only playing animations
		remove_child(max_bound_checker)
		max_bound_checker.queue_free()
		
		# hide all children
		for child in get_children():
			child.hide()

		sprite = find_child(sprite_name)
		if not sprite:
			print("Could not find sprite named: ", sprite_name)
			get_tree().paused = true
			get_tree().quit()
		
		# TODO add error handling
		
		sprite.show()
		sprite.animation_completed.connect(_on_animation_finished)
		sprite.get_animation_state().set_animation(animation_name, false, 0)

# for debugging
#func _process(delta: float) -> void:
	#print("frame: ", frame_num)
	#frame_num += 1

func _on_animation_finished(_sprite, _b, _c):
	# NOTE one extra frame will be recorded after requesting to quit
	# hiding the sprite to make it easy to tell that the last frame is the one
	# that should be removed externally
	get_tree().paused = true
	sprite.hide()
	get_tree().quit()
