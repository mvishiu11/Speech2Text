import subprocess

# Command to be executed
command = "uvicorn app:app --reload"

# Running the command
subprocess.run(command, shell=True)