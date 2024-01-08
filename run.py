import subprocess
import platform

# Command to be executed
command = "uvicorn app:app --reload"

if __name__ == "__main__":
    print(f"Starting the app on {platform.system()}...")
    
    # Execute the command
    try:
        subprocess.run(command, shell=True)
    except KeyboardInterrupt:
        print("Stopping the app by user request...")
        exit()