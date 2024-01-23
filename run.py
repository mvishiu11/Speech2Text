import subprocess
import platform
import argparse
import os
import sys
from utils.ffmpeg import install_ffmpeg_windows, install_ffmpeg_linux, install_ffmpeg_macos
import asyncio

parser = argparse.ArgumentParser(description="Run the app.")
parser.add_argument("--port", type=int, default=8000, help="Port to run the app on.")
parser.add_argument("--debug", action="store_true", help="Run the app in debug mode.")
parser.add_argument("--noreload", action="store_false", help="Reload the app when the code changes.")
parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to run the app on. If you do not know what to put here, do not include this option.")

# List of environment variables used
env_vars = []

# Command to be executed
command = "uvicorn app:app"

# Default port
os.environ["PORT"] = "8000"
env_vars.append("PORT")
os.environ["HOST"] = "127.0.0.1"
env_vars.append("HOST")
os.environ["SAMPLE_RATE"] = "16000"
env_vars.append("SAMPLE_RATE")
os.environ["BIT_DEPTH"] = "16"
env_vars.append("BIT_DEPTH")
os.environ["CHANNELS"] = "1"
env_vars.append("CHANNELS")


def main():
    os_type = platform.system()
    print(f"Running the app on {os_type}...")
    if platform.system() == "Windows":
        subprocess.run(["python", "setup.py", "--suppress_output"], shell=True)
    else:
        subprocess.run("python3 setup.py", shell=True)
    print(f"Setup completed successfully.")
    # Parse the arguments
    
    # Create necessary folders
    if not os.path.exists("runs"):
        os.makedirs("runs")
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    
    # Execute the command
    try:
        subprocess.run(command, shell=True)
    except KeyboardInterrupt:
        print("Stopping the app by user request...")
        exit(0)
    finally:
        # Remove the environment variables
        for env_var in env_vars:
            del os.environ[env_var]
            assert os.environ.get(env_var) is None, f"Failed to remove the environment variable {env_var}"
        
        print("Done and cleaned up!")

if __name__ == '__main__':
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
        env_vars.append("LOG_LEVEL")
    if not args.debug:
        os.environ["LOG_LEVEL"] = "INFO"
        env_vars.append("LOG_LEVEL")
        
    main()