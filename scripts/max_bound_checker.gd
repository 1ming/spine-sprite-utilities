## Script to determine maximum bounding box of an entity by running through
## all animations for both directions
extends Node

# save into the same directory as movie writer recordings for now
@onready var SAVE_DIR = ProjectSettings.globalize_path(ProjectSettings.get_setting("editor/movie_writer/movie_file")).get_base_dir()

@onready var max_bounds: ReferenceRect = %ReferenceRect
@onready var label: Label = %Label

# SpineSprite nodes from the scene tree
var directions: Array[SpineSprite]

# keep track of which animation and direction we are on
var dir_index = 0
var animation_index = 0
var pose_bounds: ReferenceRect
var animation_list: Array[String]

# track max bounding box position and size
var top_left_corner: Vector2
var bottom_right_corner: Vector2

func _ready() -> void:
	var has_sprite_children = false
	
	# get sprites for each direction
	# treat any sibling that is a SpineSprite as a valid direction sprite
	# make sprites invisible and listen for animation completions to move on
	# to next animation and/or direction
	for node in get_parent().get_children():
		if node is SpineSprite:
			has_sprite_children = true
			directions.append(node)
			node.hide()
			node.animation_completed.connect(_on_animation_finished)

	if not has_sprite_children:
		print("No SpineSprite children found.")
		get_tree().paused = true
		get_tree().quit()
		return
	
	# set the initial position of the max bound rectangle to the first sprite's
	# position
	top_left_corner = directions[0].global_position
	bottom_right_corner = top_left_corner
	setup()

func setup():
	# create reference rect in current sprite
	var sprite: SpineSprite = directions[dir_index]
	pose_bounds = ReferenceRect.new()
	sprite.add_child(pose_bounds)
	sprite.show()
	
	# get animation list for this sprite
	animation_list.clear()
	for animation in sprite.skeleton_data_res.get_animations() as Array[SpineAnimation]:
		animation_list.append(animation.get_name())
	
	# set first animation
	sprite.get_animation_state().set_animation(animation_list[animation_index], false, 0)

func _process(_delta: float) -> void:
	var sprite: SpineSprite = directions[dir_index]
	var skeleton := sprite.get_skeleton()
	var bounds := skeleton.get_bounds()
	
	# update rect for pose bounds
	pose_bounds.position = bounds.position
	pose_bounds.custom_minimum_size = bounds.size
	
	# update rect for max bounds
	# use global rect for calculations to avoid negative values
	var pose_rect = pose_bounds.get_global_rect()
	
	# update bound values
	# position: top left corner
	# end: bottom right corner
	if pose_rect.position.x < top_left_corner.x:
		top_left_corner.x = pose_rect.position.x
	if pose_rect.position.y < top_left_corner.y:
		top_left_corner.y = pose_rect.position.y
	if pose_rect.end.x > bottom_right_corner.x:
		bottom_right_corner.x = pose_rect.end.x
	if pose_rect.end.y > bottom_right_corner.y:
		bottom_right_corner.y = pose_rect.end.y
	
	# update visuals
	max_bounds.global_position = top_left_corner
	max_bounds.size = Vector2(bottom_right_corner.x-top_left_corner.x, bottom_right_corner.y-top_left_corner.y)
	
	# for debugging
	label.text = "Max bounds: %s" % [max_bounds.size]

# go to the next animation and/or the next direction sprite
func _on_animation_finished(sprite, _b, _c):
	animation_index += 1
	if animation_index < animation_list.size():
		sprite.get_animation_state().set_animation(animation_list[animation_index], false, 0)
		return
	else:
		sprite.hide()
		animation_index = 0
		dir_index += 1
	
	if dir_index < directions.size():
		setup()
	else:
		print("max size: ", max_bounds.size)
		print("origin: ", max_bounds.global_position)
		
		# NOTE need to pause prior to quitting otherwise the next frame will
		# still be processed
		get_tree().paused = true
		_save_to_file(SAVE_DIR.path_join("data.json"))
		get_tree().quit()
		return

func _save_to_file(filename: String):
	# max bounding box data to be used for cropping in post-processing
	var data = {
		width = max_bounds.size.x,
		height = max_bounds.size.y,
		x = max_bounds.global_position.x,
		y = max_bounds.global_position.y,
	}
	
	var fh := FileAccess.open(filename, FileAccess.WRITE)
	var contents = JSON.stringify(data)
	fh.store_line(contents)
	print("Saved data to file: ", filename)
	
