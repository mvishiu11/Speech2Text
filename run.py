import subprocess
import platform
import argparse
import os

parser = argparse.ArgumentParser(description="Run the app.")
parser.add_argument("--port", type=int, default=8000, help="Port to run the app on.")
parser.add_argument("--debug", action="store_true", help="Run the app in debug mode.")

# Command to be executed
command = "uvicorn app:app --reload"

if __name__ == "__main__":
    print(f"Starting the app on {platform.system()}...")
    
    # Parse the arguments
    args = parser.parse_args()
    if args.port:
        command += f" --port {args.port}"
    if args.debug:
        os.environ["LOG_LEVEL"] = "DEBUG"
    if not args.debug:
        os.environ["LOG_LEVEL"] = "INFO"
    
    # Execute the command
    try:
        subprocess.run(command, shell=True)
    except KeyboardInterrupt:
        print("Stopping the app by user request...")
        exit()