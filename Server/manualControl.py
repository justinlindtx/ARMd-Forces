# This file is a basic framework for how manual control mode can interface with direct control logic
# IMPORTANT: Web form buttons for manual control should be configured to send HTTP requests that toggle active_dir[] elements to True or False
# Movement is handled by the thread

import threading
import time
from controlLogic import servo_setup, move_to_coords, servo_cleanup

current_coords = [0.0, 0.0, 0.0]
active_dir = {"x+": False, "x-": False, "y+": False, "y-": False, "z+": False, "z-": False} # modified by webpage
speed = 0.5
time_interval = 0.05

def arm_motion_loop(servos):
	global current_coords
	while True:
		last_coords = current_coords
		dx = dy = dz = 0
		# The thread waits for these to be set to true (whenever buttons are being pressed on the webpage)
		if active_dir["x+"]: dx += speed * time_interval
		if active_dir["x-"]: dx -= speed * time_interval
		if active_dir["y+"]: dy += speed * time_interval
		if active_dir["y-"]: dy -= speed * time_interval
		if active_dir["z+"]: dz += speed * time_interval
		if active_dir["z-"]: dz -= speed * time_interval

		if dx or dy or dz:
			current_coords[0] += dx
			current_coords[1] += dy
			current_coords[2] += dz
			move_to_coords(servos, last_coords, current_coords, 1)

		time.sleep(time_interval)

def main():
	print("Starting manual control mode")
	arm_pins = [11, 13, 15] # shoulder, elbow, base (order is important)
	servos = servo_setup(arm_pins)

	t = threading.Thread(target=arm_motion_loop, daemon=True, args=(servos,))
	t.start()

	t.join()
	servo_cleanup(servos)

if __name__ == "__main__":
	main()