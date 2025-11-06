import json
import time
import math
from controlLogic import servo_setup, find_angles, move_servos, servo_cleanup, MAX_BASE_ANGLE

initial_angles = [math.pi/4, math.pi/2, (MAX_BASE_ANGLE * math.pi/180) / 2] # 45 (shoulder), 90 (elbow), centered (base)

def execute_routine(routine, servos):
	print(f"Executing routine {routine["name"]}")
	current_angles = initial_angles

	for step in routine["steps"]:
		type = step["type"]
		if type == "move":
			next_angles = find_angles(step["coords"])
			move_servos(servos, current_angles, next_angles)
			current_angles = next_angles

		elif type == "pause":
			time.sleep(step["duration"])

		elif type == "grip":
			if step["state"] == "close":
				close_gripper() # function not written yet
			elif step["state"] == "open":
				open_gripper() # function not written yet
		
		else:
			print(f"Unknown step type {type}")

def main():
	with open("routines/routine_1.json", "r") as file:
		routine = json.load(file)
	
	arm_pins = [11, 13, 15] # shoulder, elbow, base (order is important)
	servos = servo_setup(arm_pins)

	execute_routine(routine, servos)
	servo_cleanup(servos)

if __name__ == "__main__":
	main()