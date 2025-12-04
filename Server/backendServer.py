import datetime
import time
import http.server #, cgi

#from unittest.mock import patch, MagicMock


import os
#import sys
import json
from urllib.parse import urlparse, parse_qs
from manualControl import active_dir, current_coords, get_grip_state, toggle_grip_state, close_grip, arm_motion_loop
from runRoutine import execute_routine
from controlLogic import *
from threading import *

HOST_NAME = ''
PORT_NUMBER = 8000

mode = ""
mode_lock = Lock()

cur_routine = None
routine_lock = Lock()

ARM_CHANNELS = [0, 1, 2]
servos = servo_setup(ARM_CHANNELS) # shoulder, elbow, base (order is important)
grip = grip_setup(3)

class MyHandler(http.server.BaseHTTPRequestHandler):
	# handler for GET requests
	def do_GET(self):
		if self.path in ("/", "/send?", "/send"):
			self.path = "Server/Webpage/webpage.html"
		
		# Handle movement controls
		if self.path.startswith("/move"):
			parsed = urlparse(self.path)
			params = parse_qs(parsed.query)
			dir = params.get("dir", [""])[0]
			state = params.get("state", [""])[0]
			active_dir[dir] = (state == "on") # This will cause the servos to move
			print("dir:" + dir)
			print("state: " + state)
			
			self.send_response(200)
			self.send_header("Content-type", "text/plain")
			self.end_headers()
			self.wfile.write(b"OK")
			return
		
		# Find grip state (only called at startup)
		if self.path == "/grip-state":
			self.send_response(200)
			self.send_header("Content-type", "text/plain")
			self.end_headers()
			self.wfile.write(("close" if get_grip_state() else "open").encode())
			return
		
		# Toggle grip state
		if self.path == "/grip":
			new_state = toggle_grip_state()
			self.send_response(200)
			self.send_header("Content-type", "text/plain")
			self.end_headers()
			self.wfile.write(("close" if new_state else "open").encode())
			return
		
		# Handle snapshot requests
		if self.path == "/get-coords":
			response = json.dumps(current_coords).encode()

			self.send_response(200)
			self.send_header("Content-type", "application/json")
			self.send_header("Content-Length", len(response))
			self.end_headers()
			self.wfile.write(response) # send json to client
			return
		
		# List previously saved routines
		if self.path == "/list-files":
			files = os.listdir("Server/routines")
			response = json.dumps(files).encode()

			self.send_response(200)
			self.send_header("Content-type", "application/json")
			self.send_header("Content-Length", len(response))
			self.end_headers()
			self.wfile.write(response)
			return

		try:
			sendReply = False
			if self.path.endswith(".html"):
				mimetype = "text/html"
				sendReply = True
			elif self.path.endswith(".js"):
				mimetype = "application/javascript"
				sendReply = True
			elif self.path.endswith(".ico"):
				mimetype = "image/x-icon"
				sendReply = True
			elif self.path.endswith(".css"):
				mimetype = "text/css"
				sendReply = True
			else:
				self.send_error(404, "Unknown file type")
				return
			
			if sendReply:
				full_path = os.path.join(os.curdir, self.path.lstrip("/"))
				with open(full_path, 'rb') as f:
					self.send_response(200)
					self.send_header("Content-type", mimetype)
					self.end_headers()
					try:
						self.wfile.write(f.read())
					except ConnectionAbortedError:
						pass
				return

		except IOError:
			self.send_error(404, "File not found: %s" % self.path)

	# handler for POST requests
	def do_POST(self):
		global cur_routine
		content_length = int(self.headers["Content-Length"])
		body = self.rfile.read(content_length)
		
		if self.path == "/send":
			form = parse_qs(body.decode())
			sub = form.get("sub", [""])[0]
			if (sub == "sub"):
				if ("x" in form):
					print(form["x"][0])
			self.send_response(303) # redirect
			self.send_header("Location", "/")
			self.end_headers()
			return

		if self.path == "/run-routine":
			filename = json.loads(body)
			path = os.path.join("Server/routines", filename)
			with open(path, "r") as file:
				routine = json.load(file)
				with routine_lock:
					cur_routine = routine
			#execute_routine(routine, servos)
			
			self.send_response(303) # redirect
			self.send_header("Location", "/")
			self.end_headers()
			return
		
		if self.path == "/change-mode":
			data = json.loads(body)
			m = data.get("mode")
			change_mode(m)
			self.send_response(200)
			self.send_header("Content-Type", "application/json")
			self.end_headers()
			self.wfile.write(json.dumps({"status":"running"}).encode())
			return
		# Save a routine
		if self.path == "/submit-routine":
			data = json.loads(body)
			routine = {
				"name": data[0]["name"],
				"date": datetime.date.today().isoformat(),
				"steps": data[1:]
			}

			filename = f"{data[0]['name']}.json"
			base_directory = os.path.dirname(os.path.abspath(__file__))
			directory = os.path.join(base_directory, "routines")
			filepath = os.path.join(directory, filename)

			with open(filepath, 'w') as f:
				json.dump(routine, f, indent=2)
			
			self.send_response(303) # redirect
			self.send_header("Location", "/")
			self.end_headers()
			return

def change_mode(m):
	global mode
	with mode_lock:
		mode = m
		print(mode)

def serve_manual():
	global servos
	set_position(current_coords, servos)
	close_grip(grip)

	while(1):
		arm_motion_loop(servos, grip)
		with mode_lock:
			if mode != "manual":
				break
	
def serve_routine():
	global servos, cur_routine
	while (1):
		with routine_lock:
			if (cur_routine):
				break
		time.sleep(0.1)
	execute_routine(cur_routine, servos)
	with routine_lock:
		cur_routine = None

def serve_coords():
	global servos
	while (1):
		move_to_coords(servos, )

def main():
	global servos
	try:
		server = http.server.HTTPServer((HOST_NAME, PORT_NUMBER), MyHandler)
		print ("Started httpserver on port ", str(PORT_NUMBER))

		server_thread = Thread(target = server.serve_forever)
		control_thread = None	
		server_thread.start()
		while(1):
			with mode_lock:
				m = mode
			print(m)
			match m:
				case "manual":
					serve_manual()
				case "create":
					serve_manual()
				case "run-routine":
					serve_routine()
				case "coords":
					serve_coords()
				case _:
					pass
			time.sleep(0.1)

	except KeyboardInterrupt:
		print("^C received, shutting down web server")
		server.shutdown()
	finally:
		if server:
			server.server_close()
		servo_cleanup(servos)
	
	
	
	

if __name__ == "__main__":
	main()
