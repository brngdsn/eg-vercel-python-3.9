from http.server import BaseHTTPRequestHandler
import json
import subprocess
import readmeai
import sys
import platform
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Generate README in offline mode using subprocess and full Python path
        python_executable = readmeai.__path__
        try:
            result = subprocess.run(
                [python_executable, '-m', '--offline', '--repo-path', './'],
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
            'version': sys.version,  # Full Python version string
            'version_info': {
                'major': sys.version_info.major,
                'minor': sys.version_info.minor,
                'micro': sys.version_info.micro,
                'releaselevel': sys.version_info.releaselevel,
                'serial': sys.version_info.serial
            },
            'platform': sys.platform,  # OS platform identifier
            'executable': sys.executable,  # Path to Python executable
            'prefix': sys.prefix,  # Installation prefix
            'base_prefix': sys.base_prefix,  # Base installation prefix (virtual envs)
            'byteorder': sys.byteorder,  # System byte order
            'maxsize': sys.maxsize,  # Largest supported integer
            'maxunicode': sys.maxunicode,  # Max Unicode code point
            'path': sys.path,  # Module search paths
            'modules': list(sys.modules.keys()),  # List of loaded module names
            'builtin_module_names': sys.builtin_module_names,  # Built-in modules
            'argv': sys.argv,  # Command-line arguments
            'flags': {
                'debug': sys.flags.debug,
                'inspect': sys.flags.inspect,
                'interactive': sys.flags.interactive,
                'optimize': sys.flags.optimize,
                'dont_write_bytecode': sys.flags.dont_write_bytecode,
                'no_user_site': sys.flags.no_user_site,
                'no_site': sys.flags.no_site,
                'ignore_environment': sys.flags.ignore_environment,
                'verbose': sys.flags.verbose,
                'quiet': sys.flags.quiet,
                'isolated': sys.flags.isolated
            },
            'recursion_limit': sys.getrecursionlimit(),  # Max recursion depth
            'readmeai_version': readmeai.__version__,
            'readmeai_path': list(readmeai.__path__),
            'readme': readme_content,
            'os': {
                'name': os.name,
                'cpu_count': os.cpu_count(),
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else 'N/A'
            },
            'platform_info': {
                'system': platform.system(),
                'node': platform.node(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor()
            }
        }

        # Send JSON response
        self.wfile.write(json.dumps(response_content).encode())
