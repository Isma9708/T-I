"""
Simple Flask-like web server using standard library
"""
import http.server
import socketserver
import json
from urllib.parse import parse_qs, urlparse
import os

PORT = 8080

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            try:
                with open('templates/index.html', 'rb') as file:
                    self.wfile.write(file.read())
            except Exception as e:
                self.wfile.write(f"Error reading file: {str(e)}".encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Page not found')

    def log_message(self, format, *args):
        print(format % args)

print(f"Server starting at http://localhost:{PORT}")
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print("Server started")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped by user")
