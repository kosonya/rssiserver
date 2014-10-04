#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import threading
import cgi
import re
import json
import MySQLdb

def db_init():
	db = MySQLdb.connect(host = "localhost", user = "root",	passwd = "" , db = "rssi_mapper_user_locations")
	db.set_character_set('utf8')
	c = db.cursor()
	c.execute('SET NAMES utf8')
	c.execute('SET CHARACTER SET utf8')
	c.execute('SET character_set_connection=utf8')
	return db, c

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
					ipaddr = parsed_data["user_location"]["ipaddr"]
					macaddr = parsed_data["user_location"]["mac"]
					imei = parsed_data["user_location"]["imei"]
					lac = parsed_data["user_location"]["lac"]
					latitude = parsed_data["user_location"]["latitude"]
					longitude = parsed_data["user_location"]["longitude"]
					altitude = parsed_data["user_location"]["altitude"]
					RSSI = parsed_data["user_location"]["RSSI"]
				except Exception as e:
					print e
					self.send_response(400, "Incorrect json: " + str(e))
					return
				else:
					try:
						db, c = db_init()
						query_template = "INSERT INTO rssi_mapper_user_locations (timestamp, ipaddr, macaddr, imei, lac, latitude, longitude, altitude, RSSI) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
						c.execute(query_template, (timestamp, ipaddr, macaddr, imei, lac, latitude, longitude, altitude, RSSI))
						c.close()
						db.commit()
						db.close()
					except Exception as e:
						print e
						self.send_response(500, str(e))
						return
					else:
						self.send_response(200, "OK")
						print timestamp, ipaddr, macaddr, imei, lac, latitude, longitude, altitude, RSSI
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
