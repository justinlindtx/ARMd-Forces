# This file contains code for running routines

# Imports
import time
from controlLogic import servo_setup, set_position, move_to_coords, open_grip, close_grip, servo_cleanup, L1, L2, MAX_BASE_ANGLE

initial_coords = [L2, L1, MAX_BASE_ANGLE / 2]

# Executes the given routine
def execute_routine(routine, servos, gripper):
	print(f"Executing routine {routine['name']}")
	set_position(initial_coords, servos)
	current_coords = initial_coords
	
	for step in routine["steps"]:
		type = step["type"]
		if type == "move":
			next_coords = step["coords"]
			move_to_coords(servos, current_coords, next_coords, 50)
			current_coords = next_coords

		elif type == "pause":
			time.sleep(step["duration"])

		elif type == "grip":
			if step["state"] == "close":
				close_grip(gripper)
			elif step["state"] == "open":
				open_grip(gripper)
		
		else:
			print(f"Unknown step type {type}")
