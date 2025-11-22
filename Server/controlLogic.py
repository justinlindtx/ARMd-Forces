# This file contains the logic for translating one coordinate position to another
# IMPORTANT: Z values are implemented using a polar coordinate system, measured in degrees
#
# x = horizontal distance from base
# y = height
# z = rotation about base

# import RPi.GPIO as GPIO
import time
import math
import threading

# Placeholders for arm segment lengths
L1 = 6
L2 = 5
# Servo limits (will need to test)
MAX_BASE_ANGLE = 270
# Duty cycle % parameters
MIN_DUTY = 5
MAX_DUTY = 10
GRIP_CLOSED = 3
GRIP_OPEN = 9

def servo_setup(arm_pins):
	GPIO.setmode(GPIO.BOARD)
	servos = []
	for pin in arm_pins:
		GPIO.setup(pin, GPIO.OUT)
		pwm = GPIO.PWM(pin, 50)
		pwm.start(0)
		servos.append(pwm)
	return servos

def grip_setup(pin):
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(pin, GPIO.OUT)
	pwm = GPIO.PWM(pin, 50)
	pwm.start(0)
	return pwm

def servo_cleanup(servos):
	for s in servos:
		s.stop()
	GPIO.cleanup()

def set_position(coords, servos):
	if not valid_coords(coords):
		print(f"Invalid coords: {coords}")
		return
	angles = find_angles(*coords)
	for i, servo in enumerate(servos):
		angle = angles[i]
		duty = dutycycle(angle)
		servo.ChangeDutyCycle(duty)

def move_servos(servos, start_angles, end_angles, steps, delay=0.02):
	for step in range(steps): # each servo reaches its end angle in the same # steps
		ratio = (step+1) / steps
		for i, servo in enumerate(servos): # move each servo
			angle = start_angles[i] + (end_angles[i] - start_angles[i]) * ratio
			print(f"Servo {i} angle: {angle}") # Debug print
			duty = dutycycle(angle)
			servo.ChangeDutyCycle(duty)
		time.sleep(delay)

def dutycycle(angle):
	return MIN_DUTY + (angle / math.pi) * (MAX_DUTY - MIN_DUTY)

# Calculates servo angles for desired x,y coordinates using the law of cosines
# Z coordinate is just converted to radians
# The function returns all values in radians
def find_angles(x,y,z):
	shoulder_angle = math.atan2(y,x) + math.acos(((x*x + y*y) + L1*L1 - L2*L2) / (2 * math.sqrt(x*x + y*y) * L1))
	elbow_angle = math.acos((L1*L1 + L2*L2 - (x*x + y*y)) / (2 * L1 * L2))
	base_angle = z * (math.pi/180)
	return shoulder_angle, elbow_angle, base_angle

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

def move_to_coords(servos, start, end, steps):
	if not valid_coords(*start) or not valid_coords(*end):
		print("Invalid move")
		return
	start_angles = find_angles(*start)
	end_angles = find_angles(*end)
	move_servos(servos, start_angles, end_angles, steps)

def open_grip(servo):
	servo.ChangeDutyCycle(GRIP_OPEN)

def close_grip(servo):
	servo.ChangeDutyCycle(GRIP_CLOSED)


def main():
	arm_pins = [11, 13, 15] # shoulder, elbow, base (order is important)
	servos = servo_setup(arm_pins)
	
	# Define start position
	x_start = float(input("Input starting x: "))
	y_start = float(input("Input starting y: "))
	z_start = float(input("Input starting z: "))

	# Define end position
	x_end = float(input("Input target x: "))
	y_end = float(input("Input target y: "))
	z_end = float(input("Input target z: "))

	move_to_coords(servos, (x_start, y_start, z_start), (x_end, y_end, z_end))

	servo_cleanup(servos)

if __name__ == "__main__":
	main()