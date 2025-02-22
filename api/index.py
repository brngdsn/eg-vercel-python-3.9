from http.server import BaseHTTPRequestHandler
import json
import subprocess
import readmeai
import sys

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Generate README in offline mode using subprocess and full Python path
        python_executable = readmeai.__path__
        try:
            result = subprocess.run(
                [python_executable, '-m', 'readmeai', '--offline', '--repo-path', './'],
                capture_output=True,
                text=True
            )
            readme_content = result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            readme_content = f"Failed to generate README: {str(e)}"

        # Prepare response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response_content = {
            'message': '(P)ython(API)',
            'version': sys.version,
            'info': readmeai.__version__,
            'readmeai.path': readmeai.__path__,
            'python_executable': python_executable,
            'readme': readme_content
        }

        # Send JSON response
        self.wfile.write(json.dumps(response_content).encode())
