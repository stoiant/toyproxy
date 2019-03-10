#!/usr/bin/env python3
import logging, cgi, ssl, re
from urllib.parse import urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import time, sys
from threading import Thread

#define port to be used for the server
HTTP_PORT = 8001
HTTPS_PORT = 8002
ENCODING = 'UTF-8'

logging.getLogger().setLevel(logging.INFO)

class GetPostServer(BaseHTTPRequestHandler):
    def do_GET(self):
        logging.info(self.headers)

        #ensure that only the verb proxy is processed
        target = self.parse_path_for_proxy_verb(self.path)
        if(target is None):
            self.send_response(400)
            self.end_headers()
            message = "Bad proxy URL for GET of  '{}' detected.".format(self.path)
            logging.error(message)
            self.wfile.write(bytes(message, ENCODING))
        else:
            self.send_response(200)
            self.end_headers()
            message = "Detected GET request for '{}'".format(target)
            logging.info(message)
            self.wfile.write(bytes(message, ENCODING))
            #SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
 
    def do_POST(self):
        logging.info(self.headers)

        #ensure that only the verb proxy is processed
        target = self.parse_path_for_proxy_verb(self.path)
        if(target is None):
            self.send_response(400)
            self.end_headers()
            message = "Bad proxy URL for POST of  '{}' detected.".format(self.path)
            logging.error(message)
            self.wfile.write(bytes(message, ENCODING))
        else:       
            message = "Detected POST request for '{}'".format(target)
            logging.info(message)

            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD':'POST',
                        'CONTENT_TYPE':self.headers['Content-Type'],
                        })
            self.send_response(200)
            self.end_headers()
            for item in form.list:
                logging.info(item)
                if(item is not None):
                    self.wfile.write(bytes("{}:{}\r\n".format(item.name, item.value), ENCODING))
                #BaseHTTPRequestHandler.do_GET(self)

    def parse_path_for_proxy_verb(self, path):
        match = re.search('^((?P<proxy>/proxy/)(?P<url>.*))$', path)
        if match is None:
            logging.error("Invalid URL passed.")
            return None
        else:
            return match.groups()[2]

    def is_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

VERBOSE = "True"
print("Serving HTTP at port: ", HTTP_PORT)
print("Serving HTTPS at port: ", HTTPS_PORT)

def init_server(host, port, isSsl):
    port = int(port)
    isSsl = bool(isSsl)
    server_address = ('', port)
    if (not isSsl):
        logging.info("Opening HTTP GET/POST server.")
        httpd = HTTPServer(server_address, GetPostServer)
    else: # https
        logging.info("Opening HTTPS GET/POST server.")
        httpd = HTTPServer(server_address, GetPostServer)
        httpd.socket = ssl.wrap_socket(httpd.socket,
                keyfile="credentials/key.pem",
                certfile='credentials/cert.pem', server_side=True)            

    httpdThr = Thread(target=httpd.serve_forever)
    httpdThr.daemon = True
    httpdThr.start()

if __name__ == '__main__':
    try:
        init_server("", HTTPS_PORT, True)
        init_server("", HTTP_PORT, False)
        input('Press enter to stop servers.')
    except KeyboardInterrupt:
        print("Ctrl C - Stopping server")
        sys.exit(1)
