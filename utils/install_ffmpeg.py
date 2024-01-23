import subprocess
import sys
import platform

def install_ffmpeg_windows():
    try:
        # Install Chocolatey if not already installed
        subprocess.run('Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString(\'https://chocolatey.org/install.ps1\'))', check=True, shell=True)
        
        # Install FFmpeg using Chocolatey
        subprocess.run(['choco', 'install', 'ffmpeg'], check=True, shell=True)
    except subprocess.CalledProcessError:
        print("Failed to install FFmpeg on Windows.")
        sys.exit(1)

def install_ffmpeg_linux():
    try:
        # Detect the Linux distribution (Ubuntu in this case) and install FFmpeg
        subprocess.run(['sudo', 'apt', 'update'], check=True)
        subprocess.run(['sudo', 'apt', 'install', '-y', 'ffmpeg'], check=True)
    except subprocess.CalledProcessError:
        print("Failed to install FFmpeg on Linux.")
        sys.exit(1)

def install_ffmpeg_macos():
    try:
        # Install Homebrew if not already installed (you can add the full Homebrew installation script here)
        subprocess.run('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"', check=True, shell=True)
        
        # Install FFmpeg using Homebrew
        subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
    except subprocess.CalledProcessError:
        print("Failed to install FFmpeg on macOS.")
        sys.exit(1)

if __name__ == '__main__':
    os_type = platform.system()
    if os_type == 'Windows':
        install_ffmpeg_windows()
    elif os_type == 'Linux':
        # You can add more fine-grained detection to differentiate between Linux distributions
        install_ffmpeg_linux()
    elif os_type == 'Darwin':  # macOS
        install_ffmpeg_macos()
    else:
        print(f"Unsupported operating system: {os_type}")
        sys.exit(1)
