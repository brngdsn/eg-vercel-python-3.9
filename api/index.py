from http.server import BaseHTTPRequestHandler
import json
import readmeai

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response_content = {'message': '(P)ython(API)'}
        self.wfile.write(json.dumps(response_content).encode())
