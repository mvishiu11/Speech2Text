import subprocess
import sys
import platform

def install_ffmpeg_windows(supress_output=False):
    try:
        stdout = subprocess.DEVNULL if supress_output else None
        
        # Check if Chocolatey is installed
        if subprocess.run("choco -v", shell=True, stdout=stdout, check=False).returncode != 0:
            print("Installing Chocolatey...")
            subprocess.run('Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString(\'https://chocolatey.org/install.ps1\'))', check=True, shell=True)
        
        # Check if FFmpeg is installed
        if subprocess.run("ffmpeg -version", shell=True, stdout=stdout, check=False).returncode != 0:
            print("Installing FFmpeg...")
            subprocess.run(['choco', 'install', 'ffmpeg'], check=True, shell=True)
            
        else:
            print("FFmpeg is already installed.")
            
    except subprocess.CalledProcessError:
        print("Failed to install FFmpeg on Windows.")
        sys.exit(1)

def install_ffmpeg_linux(supress_output=False):
    try:
        stdout = subprocess.DEVNULL if supress_output else None
        
        # Check if FFmpeg is installed
        if subprocess.run(["ffmpeg", "-version"], stdout=stdout, check=False).returncode != 0:
            print("Installing FFmpeg...")
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            subprocess.run(['sudo', 'apt', 'install', '-y', 'ffmpeg'], check=True)
        else:
            print("FFmpeg is already installed.")
    except subprocess.CalledProcessError:
        print("Failed to install FFmpeg on Linux.")
        sys.exit(1)

def install_ffmpeg_macos(supress_output=False):
    try:
        stdout = subprocess.DEVNULL if supress_output else None
        
        # Check if Homebrew is installed
        if subprocess.run("brew -v", shell=True, stdout=stdout, check=False).returncode != 0:
            print("Installing Homebrew...")
            subprocess.run('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"', check=True, shell=True)
        
        # Check if FFmpeg is installed
        if subprocess.run("ffmpeg -version", shell=True, stdout=stdout, check=False).returncode != 0:
            print("Installing FFmpeg...")
            subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
        else:
            print("FFmpeg is already installed.")
    except subprocess.CalledProcessError:
        print("Failed to install FFmpeg on macOS.")
        sys.exit(1)

# if __name__ == '__main__':
#     os_type = platform.system()
#     print(f"Installing FFmpeg on {os_type}...")
#     if os_type == 'Windows':
#         install_ffmpeg_windows()
#     elif os_type == 'Linux':
#         # You can add more fine-grained detection to differentiate between Linux distributions
#         install_ffmpeg_linux()
#     elif os_type == 'Darwin':  # macOS
#         install_ffmpeg_macos()
#     else:
#         print(f"Unsupported operating system: {os_type}")
#         sys.exit(1)
