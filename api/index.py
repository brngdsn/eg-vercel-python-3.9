from http.server import BaseHTTPRequestHandler
import json
import readmeai
from readmeai import ReadmeGenerator

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Generate README in offline mode from a local repository
        try:
            generator = ReadmeGenerator(offline=True)
            readme_content = generator.generate_readme(repo_path='./')  # Assuming current directory
        except Exception as e:
            readme_content = f"Failed to generate README: {str(e)}"

        # Prepare response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response_content = {
            'message': '(P)ython(API)#3.9',
            'info': readmeai.__version__,
            'readme': readme_content
        }

        # Send JSON response
        self.wfile.write(json.dumps(response_content).encode())
