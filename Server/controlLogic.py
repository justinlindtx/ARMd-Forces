# This file contains the logic for translating one coordinate position to another
# IMPORTANT: Z VALUES ARE NOT CHANGED YET. They are using a polar coordinate system, so this will have to be accounted for
#
# x = horizontal distance from base
# y = height
# z = rotation about base

import RPi.GPIO as GPIO
import time
import math

# GPIO setup
arm_pins = [11, 13] # shoulder, elbow (order is important)
base_pin = 15
GPIO.setmode(GPIO.BOARD)

# Placeholders for arm segment lengths
L1 = 6
L2 = 5
# Servo limits (will need to test)
MAX_BASE_ANGLE = 270
MIN_DUTY = 5 		# %
MAX_DUTY = 10

def move_servos(servos, start_angles, end_angles, steps=50, delay=0.02):
	for step in range(steps + 1): # each servo reaches its end angle in the same # steps
		ratio = step / steps
		for i, servo in enumerate(servos): # move each servo
			angle = start_angles[i] + (end_angles[i] - start_angles[i]) * ratio
			duty = dutycycle(angle)
			servo.ChangeDutyCycle(duty)
		time.sleep(delay)
	# Hold briefly at final positions
	time.sleep(0.2)

def dutycycle(angle):
	return MIN_DUTY + (angle / math.pi) * (MAX_DUTY - MIN_DUTY)

# Calculates servo angles for desired x,y coordinates using the law of cosines
# Returns values in radians
def find_angles(x,y):
	shoulder_angle = math.atan2(y,x) + math.acos(((x*x + y*y) + L1*L1 - L2*L2) / (2 * math.sqrt(x*x + y*y) * L1))
	elbow_angle = math.acos((L1*L1 + L2*L2 - (x*x + y*y)) / (2 * L1 * L2))
	return shoulder_angle, elbow_angle

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

def main():
	# Setup servos
	servos = []
	for pin in arm_pins:
		GPIO.setup(pin, GPIO.OUT)
		pwm = GPIO.PWM(pin, 50)
		pwm.start(0)
		servos.append(pwm)

	# Define start position
	x_start = float(input("Input starting x: "))
	y_start = float(input("Input starting y: "))
	z_start = float(input("Input starting z: "))
	if not valid_coords(x_start, y_start, z_start):
		print("INVALID INPUT")
		return
	start_angles = find_angles(x_start, y_start)

	# Define end position
	x_end = float(input("Input target x: "))
	y_end = float(input("Input target y: "))
	z_end = float(input("Input target z: "))
	if not valid_coords(x_end, y_end, z_end):
		print("INVALID INPUT")
		return
	end_angles = find_angles(x_end, y_end)

	move_servos(servos, start_angles, end_angles)

	for s in servos:
		s.stop()
	GPIO.cleanup()

if __name__ == "__main__":
	main()