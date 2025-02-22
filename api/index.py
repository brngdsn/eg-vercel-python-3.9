from http.server import BaseHTTPRequestHandler
import json
import readmeai
from readmeai import ReadmeGenerator

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response_content = {
            'message': '(P)ython(API)#3.9',
            'info': readmeai.__version__
        }
        self.wfile.write(json.dumps(response_content).encode())
