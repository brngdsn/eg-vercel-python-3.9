from http.server import BaseHTTPRequestHandler
import json
import readmeai
import sys
import platform
import os
import inspect

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        response_content = {
            'readme': readme_content,
            'message': '(P)ython(API)',
            'readmeai_version': readmeai.__version__,
            'readmeai_path': list(readmeai.__path__),
            'readmeai_contents': dir(readmeai),  # Using dir() to list available items
            'version': sys.version,
            'version_info': {
                'major': sys.version_info.major,
                'minor': sys.version_info.minor,
                'micro': sys.version_info.micro,
                'releaselevel': sys.version_info.releaselevel,
                'serial': sys.version_info.serial
            },
            'platform': sys.platform,
            'executable': sys.executable,
            'prefix': sys.prefix,
            'base_prefix': sys.base_prefix,
            'byteorder': sys.byteorder,
            'maxsize': sys.maxsize,
            'maxunicode': sys.maxunicode,
            'path': sys.path,
            'modules': list(sys.modules.keys()),
            'builtin_module_names': sys.builtin_module_names,
            'argv': sys.argv,
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
            'recursion_limit': sys.getrecursionlimit(),
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

        self.wfile.write(json.dumps(response_content).encode())
