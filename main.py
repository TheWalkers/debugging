#!/usr/bin/python2.7
"""
Broken code for the debugging question.  This runs a server on port 8080 if
you run it at the command line.
"""

import BaseHTTPServer
import urlparse
from views import forms_html, breakdown_html

class BreakdownHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
    
    def do_GET(self):
        parsed = urlparse.urlparse(self.path)
        if parsed.path != '/':
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write('<h1>Not found</h1>')
            return
        self.do_HEAD()
        query = parsed.query
        args = urlparse.parse_qs(query)
        if args:
            resp = breakdown_html(args)
        else:
            resp = forms_html(args)
        self.wfile.write(resp)

def main():
    print "Serving on :8080"
    BaseHTTPServer.HTTPServer(('', 8080), BreakdownHandler).serve_forever()
    
if __name__ == '__main__':
    main()
