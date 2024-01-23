import subprocess
import platform
import sys
from utils.ffmpeg import install_ffmpeg_windows, install_ffmpeg_linux, install_ffmpeg_macos
import argparse

parser = argparse.ArgumentParser(description="Run the app.")
parser.add_argument("--suppress_output", action="store_true", help="Suppress output from the setup script.")

def install_ffmpeg():
    os_type = platform.system()
    print(f"Checking FFmpeg installation on {os_type}...")
    
    # Install FFmpeg
    if os_type == 'Windows':
        install_ffmpeg_windows(supress_output=False)
    elif os_type == 'Linux':
        install_ffmpeg_linux(supress_output=False)
    elif os_type == 'Darwin':  # macOS
        install_ffmpeg_macos(supress_output=True)
    else:
        print(f"Unsupported operating system: {os_type}")
        sys.exit(1)
        
def setup(supress_output=False):
    # Install FFmpeg
    install_ffmpeg()
    
    # Supress output?
    output = subprocess.DEVNULL if supress_output else None
    
    # Install dependencies
    print("Installing dependencies...")
    if platform.system() == "Windows":
        subprocess.run("pip install -r requirements.txt", shell=True, stdout=output)
    else:
        subprocess.run("sudo apt install python3-pip", shell=True, stdout=output)
        subprocess.run("pip3 install -r requirements.txt", shell=True, stdout=output)
        
if __name__ == '__main__':
    args = parser.parse_args()
    setup(supress_output=args.suppress_output)
