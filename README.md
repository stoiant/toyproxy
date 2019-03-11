# Web Service acting as HTTP(S) Proxy for GET/POST

## Goal

The goal is to write a web service that acts as an `HTTP(S)` proxy in python. 

If you know what you are doing it will take about 42 minutes.

## Requirements

The only method that needs to be implemented is `/proxy/<url>`

It should listen for both `GET` and `POST`

* On a `GET` request, it should make a get request to `<url>` 
* On a `POST` request, it should make a post request to `<url>`, passing through any form data
It should set the user-agent header to the same user-agent that it is being called by (note `curl/7.35.0` in the examples)

## Installation

### Requirements

* python3
* pip3
* external libraries(packages)
 * simplejson
 * requests

### Steps to setup environment

* clone repository
* ensure python3 and pip3 is installed
* setup virtaul environment to download packages

```
virtualenv venvdev
virtualenv -p /usr/local/bin/python3 venvdev
source venv/bin/activate
source venvdev/bin/activate
pip3 install requests
pip3 install simplejson
```

### Run the server

Ports are defined as 8001 for `HTTP` and 8002 for `HTTPS` if ports are busy on the system running the proxy server then code will have to be modified accordingly.

For simplicity ports are not taken as input paramters.

```
python3 server.py
```

## Limitations

* single user
* performance is not relevant
* no support for Websockets
* no support for chunking
* limited response as it is written at once
* running on port 8001(HTTP) and 8002(HTTPS)
* relative url requests will fail due to /proxy/ not being used (e.g. viewing a website)
* logging is for debug prupposes
* no TLS
* response encoding set to `UTF-8` for custom messages
* REQUEST_TIMEOUT set to 10 seconds
* authentication is not supported
* file transfer and limits in post not tested
* timeboxed fun to toy with :)

## SSL Self Signed Certificate

### Generate a certificate
```
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365
```

### Remove passphrase to avoid manual entry
```
openssl rsa -in [key.pem] -out [key_no_pass.pem]
```

Note: To properly server SSL requests the certificate will have to be trusted by the local server.

## Testing

### Dev Environment

MacOS

IDE (VisualStudio)

### Display basic web-pages

Verify sites such as http://google.ca https://google.ca render with the provided limitations.

<https://127.0.0.1:8002/proxy/https://gotrain.app>
<http://127.0.0.1:8001/proxy/https://google.ca>

### Use Postman

-  test to ensure handling of `HTTP` requests and proper message is 	displayed if request is not supported
- `RFC 7231`, section 4: Request methods	Hypertext Transfer Protocol (HTTP/1.1): Semantics and Content	Specifies GET, HEAD, POST, PUT, DELETE, CONNECT, OPTIONS, TRACE.

### REST Calls

The following site was utilized for `GET` `POST` API calls:

<https://reqres.in/>

<http://127.0.0.1:8001/proxy/https://reqres.in/api/users?page=2>


## Provided Examples 
Assuming the web service is running on localhost:8000, here are some examples of how it can be used:

* `GET`

```   
$ curl  http://localhost:8000/proxy/http://httpbin.org/get
    
{
   "args": {}, 
   "headers": {
   "Accept": "*/*", 
   "Accept-Encoding": "gzip, deflate", 
   "Host": "httpbin.org", 
   "User-Agent": "curl/7.35.0"
 }, 
   "origin": "99.250.201.200", 
   "url": "http://httpbin.org/get"
 }
```

* `POST`

```
$ curl -X POST -d asdf=blah  http://localhost:8000/proxy/http://httpbin.org/post
    
{
  "args": {}, 
  "data": "", 
  "files": {}, 
  "form": {
  "asdf": "blah"
}, 
  "headers": {
  "Accept": "*/*", 
  "Accept-Encoding": "gzip, deflate", 
  "Content-Length": "9", 
  "Content-Type": "application/x-www-form-urlencoded", 
  "Host": "httpbin.org", 
  "User-Agent": "curl/7.35.0"
}, 
  "json": null, 
  "origin": "99.250.201.200", 
  "url": "http://httpbin.org/post"
}
```

## References

<https://docs.python.org/3/library/urllib.parse.html>
<https://docs.python.org/3/library/http.server.html>
<https://docs.python.org/3/library/http.html>
<https://realpython.com/python-requests/#the-get-request>
<https://docs.python.org/3.3/library/http.client.html>
<https://docs.python.org/3/library/io.html>
<https://realpython.com>