#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import threading
import cgi
import re
import json

class HTTPRequestHandler(BaseHTTPRequestHandler):
 
    def address_string(self): #Fix for the slow response
        host, _ = self.client_address[:2]
        return host
 
    def do_POST(self):
	if None != re.search('/user_locations.json', self.path):
		ctype, _ = cgi.parse_header(self.headers.getheader('content-type'))
		if "application/json" == ctype:
			length = int(self.headers.getheader('content-length'))
			data = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
			print data
			try:
				parsed_data = json.loads(data.keys()[0])
			except Exception as e:
				print e
				self.send_response(400, "Failed to parse json: " + str(e))
				return
			else:
				try:
					timestamp = parsed_data["user_location"]["timestamp"]
				except Exception as e:
					print e
					self.send_response(400, "Incorrect json: " + str(e))
					return
				else:
					self.send_response(200, "OK")
					print parsed_data
					return
	self.send_response(400, "Bad request")
        
    def do_GET(self):
	return
        print "Path:", self.path
        self.send_response(200, "OK")

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
 
    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)
 
class SimpleHttpServer():
    def __init__(self, ip, port):
        self.server = ThreadedHTTPServer((ip,port), HTTPRequestHandler)
 
    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = False
        self.server_thread.start()
 
    def waitForThread(self):
        self.server_thread.join()
 
    def stop(self):
        self.server.shutdown()
        self.waitForThread()


def main():
    http_server = SimpleHttpServer('', 31415)
    print 'HTTP Server Running...........'
    http_server.start()
    http_server.waitForThread()
    
if __name__ == "__main__":
    main()
