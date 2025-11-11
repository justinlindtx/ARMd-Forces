import time
import http.server, cgi
#import RPi.GPIO as GPIO
from os import curdir, sep

HOST_NAME = ''
PORT_NUMBER = 8000

class MyHandler(http.server.BaseHTTPRequestHandler):
	# handler for GET requests
	def do_GET(self):
		if self.path in ("/", "/send?", "/send"):
			self.path = "/webpage.html"

		try:
			sendReply = False
			if self.path.endswith(".html"):
				mimetype = "text/html"
				sendReply = True
			elif self.path.endswith(".js"):
				mimetype = "application/javascript"
				sendReply = True
			elif self.path.endswith(".ico"):
				mimetype = "image/icon"
				sendReply = True
				
			#full_path = os.path.join(os.curdir, self.path.lstrip("/"))
			
			if sendReply:
				f = open(curdir + sep + self.path, 'rb')
				self.send_response(200)
				self.send_header("Content-type", mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				# This is where we need to create custom HTML and send it
				# note the use of single quotes so we can transmit double quotes
				f.close()
			return

		except IOError:
			self.send_error(404, "File not found: %s" % self.path)

	# handler for POST requests
	def do_POST(self):
		if self.path == "/send":
			self.path = "/"
			form = cgi.FieldStorage(
				fp = self.rfile,
				headers = self.headers,
				environ = {"REQUEST_METHOD":"POST",
					"CONTENT_TYPE":self.headers["Content-Type"],
			})
			if (form["sub"].value == "sub"):
				if ("x" in form):
					print(form["x"].value)
		self.do_GET()
		
def main():

	try:
		server = http.server.HTTPServer((HOST_NAME, PORT_NUMBER), MyHandler)
		print ("Started httpserver on port ", str(PORT_NUMBER))

		server.serve_forever()

	except KeyboardInterrupt:
		print("^C received, shutting down web server")
	finally:
		server.socket.close()
		GPIO.cleanup()

if __name__ == "__main__":
	main()
