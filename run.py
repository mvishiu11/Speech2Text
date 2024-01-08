import subprocess
import platform
import argparse
import os

parser = argparse.ArgumentParser(description="Run the app.")
parser.add_argument("--port", type=int, default=8000, help="Port to run the app on.")
parser.add_argument("--debug", action="store_true", help="Run the app in debug mode.")
parser.add_argument("--noreload", action="store_false", help="Reload the app when the code changes.")
parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to run the app on. If you do not know what to put here, do not include this option.")

# Command to be executed
command = "uvicorn app:app"

# Default port
os.environ["PORT"] = "8000"
os.environ["HOST"] = "127.0.0.1"

if __name__ == "__main__":
    print(f"Starting the app on {platform.system()}...")
    
    # Parse the arguments
    args = parser.parse_args()
    if args.port:
        if args.port < 1024 or args.port > 65535:
            print("Port number must be between 1024 and 65535.")
        else:
            command += f" --port {args.port}"
            os.environ["PORT"] = str(args.port)
    if args.host:
        if args.host == "127.0.0.1":                # localhost
            command += f" --host {args.host}"
        elif args.host == "0.0.0.0":                # any interface
            command += f" --host {args.host}"
        else:                                       # custom host                  
            print("Custom host set, hope you know what you are doing.")
            command += f" --host {args.host}"
        os.environ["HOST"] = args.host
    if args.noreload:
        command += " --reload"
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