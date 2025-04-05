import os
import subprocess
import platform
import distro

# Function to run a shell command
def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {command}\n{result.stderr}")
    else:
        print(result.stdout)
    return result

# Determine OS family
def determine_os_family():
    os_family = platform.system().lower()
    if os_family == 'linux':
        # Use the distro package to check for specific Linux distributions
        distro_name = distro.id().lower()
        if 'redhat' in distro_name or 'centos' in distro_name or 'fedora' in distro_name:
            return 'redhat'
        elif 'debian' in distro_name or 'ubuntu' in distro_name:
            return 'debian'
    elif os_family == 'darwin':
        return 'macos'
    elif os_family == 'windows':
        return 'windows'
    return 'unknown'

def install_python():
    os_family = determine_os_family()
    if os_family == 'redhat':
        print("Installing Python and pip...")
        run_command("yum install python3 python3-pip")
    elif os_family == 'debian':
        print("Installing Python and pip...")
        run_command("apt-get install python3 python3-pip")
    elif os_family == 'macos':
        print("Installing Python and pip...")
        run_command("brew install python3")
        run_command("python3 -m ensurepip")  # Ensure pip is installed
    elif os_family == 'windows':
        print("Installing Python and pip...")
        run_command("choco install python3")
        run_command("python -m ensurepip")  # Ensure pip is installed

        # If ensurepip doesn't work, use get-pip.py
        pip_check = run_command("pip --version")
        if pip_check.returncode != 0:
            print("Downloading get-pip.py to install pip...")
            run_command("curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py")
            run_command("python get-pip.py")

    # Upgrade pip to the latest version
    run_command("python -m pip install --upgrade pip")

# Ensure Python and pip are installed
def check_python():
    print("Checking Python and pip installation...")
    python_result = run_command("python --version")
    pip_result = run_command("pip --version")

    # if python and pip are not installed, install them
    if python_result.returncode != 0 or pip_result.returncode != 0:
        install_python()

        

def install_ansible():
    # Install Ansible using pip
    print("Installing Ansible...")
    run_command("python -m pip install ansible")
    # Verify Ansible installation
    print("Verifying Ansible installation...")
    run_command("ansible --version")

# Show a numbered menu of the top 20 most popular Ansible collections 
# allow the user to select any of them and return to the menu
def show_collections_menu():
    collections = []
    popular_collections = [
        "community.general",
        "ansible.posix",
        "community.network",
        "community.kubernetes",
        "community.aws",
        "community.docker",
        "community.crypto",
        "community.vmware",
        "community.windows"
    ]

    while True:
        print("Select a collection to install or press Enter to continue:")
        for i, collection in enumerate(popular_collections, start=1):
            print(f"{i}. {collection}")

        choice = input("Enter the number of the collection to install or press Enter to continue: ")

        if choice == "":
            break

        # clear the screen
        os.system('cls' if os.name == 'nt' else 'clear')

        try:
            index = int(choice) - 1
            if 0 <= index < len(popular_collections):
                selected_collection = popular_collections[index]
                if selected_collection not in collections:
                    collections.append(selected_collection)
                    print(f"Added {selected_collection} to the list.")
                    print(f"The list now contains the following collections:")
                    for collection in collections:
                        print(f"  {collection}")
                else:
                    print(f"{selected_collection} was already in the list.")
                    print(f"Removing {selected_collection} from the list.")
                    collections.remove(selected_collection)
                    print(f"The list now contains the following collections:")
                    for collection in collections:
                        print(f"  {collection}")
                    
            else:
                print("Invalid selection. Please choose a number from the list or press Enter to continue.")
        except ValueError:
            print("Invalid input. Please enter a number or press Enter to continue.")

    print("Selected collections:")
    for collection in collections:
        print(collection)

    return collections

# check if python and pip are installed
try:
    check_python()
except Exception as e:
    print(f"Error checking Python and pip installation: {e}")
    install_python()

# Install Ansible using pip
try:
    install_ansible()
except Exception as e:
    print(f"Error installing Ansible: {e}")

# Show collections menu and get selected collections
selected_collections = show_collections_menu()

# Install selected collections
if selected_collections:
    print("Installing selected collections...")
    for collection in selected_collections:
        print(f"Installing {collection}...")
        run_command(f"ansible-galaxy collection install {collection}")
else:
    print("No collections selected. Exiting.")
