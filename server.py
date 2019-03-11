#!/usr/bin/env python3
import logging, cgi, ssl, re
from urllib.parse import urlparse
import urllib
from http.server import HTTPServer, BaseHTTPRequestHandler, HTTPStatus
import time, sys
from threading import Thread
#requires pip install
import requests
from requests.exceptions import HTTPError
from requests.exceptions import Timeout
#requires pip install
import simplejson as json
import http.client
import io

#define port to be used for the server
HTTP_PORT = 8001
HTTPS_PORT = 8002
ENCODING = 'UTF-8'
REQUEST_TIMEOUT = 10

logging.getLogger().setLevel(logging.INFO)

class GetPostServer(BaseHTTPRequestHandler):
    def do_DELETE(self):
        logging.info(self.headers)
        self.send_response(HTTPStatus.NOT_IMPLEMENTED.value)
        self.end_headers()
        message = HTTPStatus.NOT_IMPLEMENTED.description
        logging.error(message)
        self.wfile.write(bytes(message, ENCODING))
    def do_GET(self):
        logging.info(self.headers)

        #delete does not seem to return not implemented so adding it to the proxy
        if(self.command == 'DELETE'):
            self.do_DELETE

        #ensure that only the verb proxy is processed
        target = self.parse_path_for_proxy_verb(self.path)
        if(target is None):
            self.send_response(HTTPStatus.BAD_REQUEST)
            BaseHTTPRequestHandler.end_headers(self)
            message = "Bad proxy URL for GET of '{}' detected.".format(self.path)
            logging.error(message)
            self.wfile.write(bytes(message, ENCODING))
        else:
            message = "Detected GET request for '{}'".format(target)
            logging.info(message)

            dHeaders = self.get_destination_headers()
            dParams = self.get_destination_params(target)

            response = None
            try:
                response = requests.get(target, headers=dHeaders, params=dParams, timeout=REQUEST_TIMEOUT)
                logging.info("Received response code of '{}' from '{}'".format(response.status_code, target))

                # If the response was successful, no Exception will be raised
                response.raise_for_status()

            except HTTPError as http_err:
                message = "HTTP error occurred: {}".format(http_err)
                logging.error(message)
                if(response != None and response.status_code != None):
                    self.send_response(response.status_code)
                else:
                    self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)

                self.end_headers()

                if(response != None and response.status_code != None):
                    self.wfile.write(response.content)
                else:
                    self.wfile.write(bytes(message, ENCODING))

            except Timeout:
                message = "The request timed out in {}s".format(REQUEST_TIMEOUT)
                logging.error(message)
                if(response != None and response.status_code != None):
                    self.send_response(response.status_code)
                else:
                    self.send_response(HTTPStatus.REQUEST_TIMEOUT)

                self.end_headers()

                if(response != None and response.status_code != None):
                    self.wfile.write(response.content)
                else:
                    self.wfile.write(bytes(message, ENCODING))
            except Exception as err:
                message = "Other error occurred: {}".format(err)
                logging.error(message)
                if(response != None and response.status_code != None):
                    self.send_response(response.status_code)
                else:
                    self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)

                self.end_headers()

                if(response != None and response.status_code != None):
                    self.wfile.write(response.content)
                else:
                    self.wfile.write(bytes(message, ENCODING))                
            else:
                logging.info("Call to target host successful.")
                self.send_response(response.status_code)
                self.write_headers(response.headers)
                self.wfile.write(response.content)
                self.close_connection = True

    def get_destination_params(self, target):
        params = {}
        if(self.is_url(target)):
            logging.info(urllib.parse.urlsplit(target))
            logging.info(urllib.parse.parse_qs(urllib.parse.urlsplit(target).query))
            params = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(target).query))

        return params

    def get_destination_headers(self):
        dHeaders = {}
        lines = io.StringIO(str(self.headers))
        line = lines.readline()
        while line:
            if line.strip() != '':
                print(line.strip())
                match = re.search('^((?P<key>\S+):\s*(?P<value>.*))$', line.strip())
                if match is None:
                    logging.error("Invalid header line format of '{}' detected. Ignoring header.".format(line.strip()))
                else:
                    key = match.groups()[1]
                    value = match.groups()[2]
                    if(key.lower() != 'Host'.lower()):
                        dHeaders[key] = value

            line = lines.readline()
        return dHeaders

    def write_headers(self, headers):
        for key, value in headers.items():
            logging.info("{}:{}".format(key,value))
            #serving the raw response with no support for chunking
            if(key.lower() == 'Transfer-Encoding'.lower()):
                logging.info("Skipping {} with value {}".format(key,value))
            else:
                self.send_header(key, value)
    
        self.end_headers()

    def do_POST(self):
        logging.info(self.headers)

        #ensure that only the verb proxy is processed
        target = self.parse_path_for_proxy_verb(self.path)
        if(target is None):
            self.send_response(HTTPStatus.BAD_REQUEST)
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
            self.send_response(HTTPStatus.OK)
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
        input('Press enter to stop toy proxy servers.')
    except KeyboardInterrupt:
        print("Ctrl C - Stopping toy proxy server")
        sys.exit(1)
