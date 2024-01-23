import subprocess
import sys
import platform
import os

def is_admin():
    try:
        return subprocess.check_call(['net', 'session'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    except:
        return False

def run_as_admin():
    print("Requesting administrator privileges...")
    subprocess.call(['powershell', 'Start-Process', 'python', f"'{sys.argv[0]}'", '-Verb', 'RunAs'])
    sys.exit()

def is_choco_installed():
    return subprocess.run("choco -v", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

def is_ffmpeg_installed():
    return subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, check=False).returncode == 0

def install_ffmpeg_windows(supress_output=False):
    stdout = subprocess.DEVNULL if supress_output else None
    
    if not is_choco_installed() or not is_ffmpeg_installed():
        if not is_admin():
            run_as_admin()

        if not is_choco_installed():
            print("Installing Chocolatey...")
            ps_command = 'Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString(\'https://chocolatey.org/install.ps1\'))'
            subprocess.run(["powershell", "-Command", ps_command], check=True)

        if not is_ffmpeg_installed():
            print("Installing FFmpeg...")
            subprocess.run(['choco', 'install', 'ffmpeg'], check=True)
            
    else:
        print("Chocolatey and FFmpeg are already installed.")

def install_ffmpeg_linux(supress_output=False):
    try:
        stdout = subprocess.DEVNULL if supress_output else None

        # Check if FFmpeg is installed
        try:
            ffmpeg_check = subprocess.run(["ffmpeg", "-version"], stdout=stdout, stderr=stdout, check=False)
            if ffmpeg_check.returncode != 0:
                raise FileNotFoundError("FFmpeg not found")
        except FileNotFoundError:
            print("FFmpeg is not installed, installing now...")
            subprocess.run(['sudo', 'apt', 'update'], check=True, stdout=stdout, stderr=stdout)
            subprocess.run(['sudo', 'apt', 'install', '-y', 'ffmpeg'], check=True, stdout=stdout, stderr=stdout)
        else:
            print("FFmpeg is already installed.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install FFmpeg on Linux. Error: {str(e)}")
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
