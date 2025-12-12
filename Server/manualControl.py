# This file is a basic framework for how manual control mode can interface with direct control logic
# IMPORTANT: All web-based forms of manual control must be configured to send HTTP requests that toggle active_dir[] elements to True or False
# Movement is handled by the thread
# This file has funtions for maunually controlling the arm

# Imports
import threading
import time
from controlLogic import servo_setup, grip_setup, set_position, move_to_coords, close_grip, open_grip, servo_cleanup

# Control parameters
current_coords = [3, 3, 45] # initialized to default starting position
active_dir = {"x": False, "x-": False, "y": False, "y-": False, "z": False, "z-": False} # modified by webpage
last_grip_state = None
grip_closed = True
grip_lock = threading.Lock()

SPEED = 0.75
TIME_INTERVAL = 0.05

# Gets the current grip state
def get_grip_state():
	with grip_lock:
		return grip_closed

# Toggles grip state
def toggle_grip_state():
	global grip_closed
	with grip_lock:
		grip_closed = not grip_closed
		return grip_closed

# Adjusts arm position according to 'active_dir' inputs
def arm_motion_loop(servos, gripper):
	global current_coords, last_grip_state

	last_coords = current_coords
	dx = dy = dz = 0
	# The thread waits for these to be set to true (i.e. whenever buttons are being pressed on the webpage)
	if active_dir["x"]: dx += SPEED * TIME_INTERVAL
	if active_dir["x-"]: dx -= SPEED * TIME_INTERVAL
	if active_dir["y"]: dy += SPEED * TIME_INTERVAL
	if active_dir["y-"]: dy -= SPEED * TIME_INTERVAL
	if active_dir["z"]: dz += SPEED * 30 * TIME_INTERVAL
	if active_dir["z-"]: dz -= SPEED * 30 * TIME_INTERVAL
	
	print("dx: " + str(dx))

	if dx or dy or dz:
		current_coords[0] += dx
		current_coords[1] += dy
		current_coords[2] += dz
		move_to_coords(servos, last_coords, current_coords, 1)
	
	# Handle gripper
	is_closed = get_grip_state()
	if is_closed != last_grip_state:
		if is_closed:
			close_grip(gripper)
		else:
			open_grip(gripper)
		last_grip_state = is_closed

	time.sleep(TIME_INTERVAL)

