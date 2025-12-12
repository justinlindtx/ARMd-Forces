# This file contains the logic for translating one coordinate position to another
# IMPORTANT: Z values are implemented using a polar coordinate system, measured in degrees
#
# x = horizontal distance from base
# y = height
# z = rotation about base

# Imports
from adafruit_servokit import ServoKit
import time
import math

# Arm segment lengths in 'units'
L1 = 7
L2 = 5

# Base servo limit
MAX_BASE_ANGLE = 170

# Grip angle parameters (in degrees)
GRIP_CLOSED = 25
GRIP_OPEN = 80

kit = ServoKit(channels=16)

# Call once to set up and return servos
def servo_setup(arm_channels):
	servos = []
	for ch in arm_channels:
		servos.append(kit.servo[ch])
	return servos

# Call once to set up and return grip servo
def grip_setup(channel):
	return kit.servo[channel]

# Call to clean up servos
def servo_cleanup(servos):
	for s in servos:
		s.angle = None

# Sets servo angles to coords [x, y, z]
def set_position(coords, servos):
	if not valid_coords(*coords):
		print(f"Invalid coords: {coords}")
		return
	angles = find_angles(*coords)
	for i, servo in enumerate(servos):
		servo.angle = angles[i]

# Interpolates servo angles from 'start_angles' to 'end_angles' over 'steps' steps
def move_servos(servos, start_angles, end_angles, steps, delay=0.02):
	for step in range(steps): # each servo reaches its end angle in the same # steps
		ratio = (step+1) / steps
		for i, servo in enumerate(servos): # move each servo
			angle = start_angles[i] + (end_angles[i] - start_angles[i]) * ratio
			print(f"Servo {i} angle: {angle:.2f}") # Debug print
			servo.angle = angle
		time.sleep(delay)

# Converts radians r to degrees
def rad_to_deg(r):
    return r * 180.0 / math.pi

# Calculates servo angles for desired x,y coordinates using the law of cosines
# Z coordinate is already an angle, so nothing is done to it
# The function returns all values in degrees
def find_angles(x,y,z):
	shoulder_angle = rad_to_deg(math.atan2(y,x) + math.acos(((x*x + y*y) + L1*L1 - L2*L2) / (2 * math.sqrt(x*x + y*y) * L1)))
	elbow_angle = rad_to_deg(math.acos((L1*L1 + L2*L2 - (x*x + y*y)) / (2 * L1 * L2)))
	base_angle = z
	return shoulder_angle, elbow_angle, base_angle

# Returns True if given coords are valid, False otherwise
def valid_coords(x,y,z):
	if x < 0 or y < 0 or z < 0: # out of range
		return False
	if z > MAX_BASE_ANGLE: # exceeds base rotation limit
		return False
	if math.sqrt(x*x + y*y) > (L1 + L2): # too far from origin
		return False
	if math.sqrt(x*x + y*y) < abs(L1 - L2): # too close to origin
		return False
	return True

# Interpolates position from coords 'start' to 'end' over 'steps' steps 
def move_to_coords(servos, start, end, steps):
	if not valid_coords(*start) or not valid_coords(*end):
		print("Invalid move")
		return
	start_angles = find_angles(*start)
	end_angles = find_angles(*end)
	move_servos(servos, start_angles, end_angles, steps)

# Opens the grip
def open_grip(servo):
	servo.angle = GRIP_OPEN

# Closes the grip
def close_grip(servo):
	servo.angle = GRIP_CLOSED
