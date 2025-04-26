import subprocess
import shutil

# Function to run a shell command
def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

# Check and update apt
if shutil.which("apt"):
    print("Updating and upgrading packages using apt...")
    run_command("sudo apt update && sudo apt upgrade -y")

# Check and update dnf
if shutil.which("dnf"):
    print("Updating and upgrading packages using dnf...")
    run_command("sudo dnf check-update && sudo dnf upgrade -y")

# Check and update conda
if shutil.which("conda"):
    print("Updating and upgrading packages using conda...")
    run_command("conda update --all -y")

# Add more package managers as needed
# Example for pip
if shutil.which("pip"):
    print("Updating packages using pip...")
    run_command("pip install --upgrade pip")
    run_command("pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U")

print("Upgrade process completed.") 