#!/usr/bin/env python3
# encoding: utf-8

# serve.py

"""
Use instead of `python3 -m http.server` when you need CORS.
Derived from gist @ https://gist.github.com/acdha/925e9ffc3d74ad59c3ea
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super(CORSRequestHandler, self).end_headers()

def serve(directory: str = './', port: int = 8000) -> None:
    os.chdir(directory)

    httpd = HTTPServer(('localhost', port), CORSRequestHandler)
    print(f'Serving to http://localhost:{port}')
    print('Press CTRL+C to quit.')
    httpd.serve_forever()
    
if __name__ == '__main__':
    import sys
    serve_dir = sys.argv[1] if len(sys.argv) > 1 else './'
    serve_port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    serve(serve_dir, serve_port)
