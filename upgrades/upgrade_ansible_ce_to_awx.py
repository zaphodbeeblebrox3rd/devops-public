import subprocess
import os
import platform
import distro

# Function to run a shell command
def run_command(command, use_sudo=False):
    if use_sudo:
        command = f"echo 'your_password' | sudo -S {command}"
    print(f"Running command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True, env=os.environ)
    if result.returncode != 0:
        print(f"Error running command: {command}\n{result.stderr}")
    else:
        print(f"Command output:\n{result.stdout}")
    return result

# Determine OS family
def determine_os_family():
    platform_type = platform.system().lower()
    if platform_type == 'linux':
        os_family = distro.id().lower()
        if 'redhat' in os_family or 'centos' in os_family or 'fedora' in os_family or 'rocky' in os_family:
            return 'redhat'
        elif 'debian' in os_family or 'ubuntu' in os_family:
            return 'debian'
    elif platform_type == 'darwin':
        return 'macos'
    elif platform_type == 'windows':
        return 'windows'
    return 'unknown'

# Check if Kubernetes cluster is running
def check_kubernetes_cluster():
    print("Checking if Kubernetes cluster is running...")
    result = run_command("kubectl cluster-info")
    if result.returncode != 0:
        print("Kubernetes cluster is not accessible. Please ensure it is running and accessible.")
        return False
    return True

# Install Kubernetes tools
def install_kubernetes_tools():
    os_family = determine_os_family()
    if os_family == 'windows':
        print("Installing kubectl and helm on Windows...")
        run_command("choco install kubernetes-cli")
        run_command("choco install kubernetes-helm")
    elif os_family == 'redhat':
        print("Installing kubectl and helm on RHEL...")
        # Create the Kubernetes repo file using sudo tee
        # The open function does not have sudo support
        kubernetes_repo = """
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v1.32/rpm/
enabled=1
gpgcheck=1
gpgkey=https://pkgs.k8s.io/core:/stable:/v1.32/rpm/repodata/repomd.xml.key
"""
        run_command(f"echo '{kubernetes_repo}' | sudo tee /etc/yum.repos.d/kubernetes.repo")
        run_command("sudo yum install -y kubectl")
        run_command("curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash")
    elif os_family == 'debian':
        print("Installing kubectl and helm on Debian...")
        run_command("sudo apt-get install -y apt-transport-https ca-certificates curl")
        run_command("sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg")
        run_command("echo 'deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main' | sudo tee /etc/apt/sources.list.d/kubernetes.list")
        run_command("sudo apt-get update")
        run_command("sudo apt-get install -y kubectl")
        run_command("curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash")
    elif os_family == 'macos':
        print("Installing kubectl and helm on macnstalling Kind on Windows...")
        run_command("choco install kind")
    elif os_family == 'redhat' or os_family == 'debian':
        print("Installing Kind on Linux...")
        run_command("curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64")
        run_command("chmod +x ./kind")
        run_command("sudo mv ./kind /usr/local/bin/kind")
    elif os_family == 'macos':
        print("Installing Kind on macOS...")
        run_command("brew install kind")
    else:
        print("Unsupported OS. Please install Kind manually.")

# Deploy AWX on Kubernetes
def deploy_awx_kubernetes():
    print("Deploying AWX on Kubernetes...")
    run_command("helm repo add awx-operator https://ansible-community.github.io/awx-operator-helm/")
    run_command("helm repo update")
    run_command("helm install awx-operator awx-operator/awx-operator")

    # Create AWX instance manifest
    awx_manifest = """
apiVersion: awx.ansible.com/v1beta1
kind: AWX
metadata:
  name: awx
spec:
  service_type: nodeport
"""
    with open("awx-instance.yaml", "w") as f:
        f.write(awx_manifest)

    # Apply the AWX instance manifest
    run_command("kubectl apply -f awx-instance.yaml")

# Check if Kind is installed and create a cluster if necessary
def start_kind_cluster():
    print("Checking Kind status...")
    result = run_command("/usr/local/bin/kind get clusters", use_sudo=True)
    
    # Print the output for debugging
    print("Output from 'kind get clusters':")
    print(result.stdout)
    
    # Check if "No kind clusters found" is in any line of the output
    if any("No kind clusters found" in line for line in result.stdout.splitlines()):
        print("No Kind cluster found. Creating a new Kind cluster...")
        run_command("/usr/local/bin/kind create cluster", use_sudo=True)
    else:
        print("Kind cluster is already running.")

def install_kind():
    os_family = determine_os_family()
    if os_family == 'windows':
        print("Installing Kind on Windows...")
        run_command("choco install kind")
    elif os_family == 'redhat' or os_family == 'debian':
        print("Installing Kind on Linux...")
        run_command("curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64")
        run_command("chmod +x ./kind")
        run_command("sudo mv ./kind /usr/local/bin/kind")
    elif os_family == 'macos':
        print("Installing Kind on macOS...")
        run_command("brew install kind")
    else:
        print("Unsupported OS. Please install Kind manually.")

# Main logic
print("Proceeding with AWX installation on Kubernetes...")

install_kubernetes_tools()
install_kind()

# Start Kind cluster if necessary
start_kind_cluster()

if check_kubernetes_cluster():
    deploy_awx_kubernetes()
else:
    print("Please start your Kubernetes cluster and try again.")


