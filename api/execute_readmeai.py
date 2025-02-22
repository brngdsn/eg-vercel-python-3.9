import subprocess
import json

def handler(request):
    try:
        # Execute the CLI tool (adjust the command arguments as needed)
        result = subprocess.run(
            ["readmeai", "--version"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": result.stderr})
            }

        return {
            "statusCode": 200,
            "body": json.dumps({"output": result.stdout})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
