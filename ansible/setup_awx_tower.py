import subprocess
import os
import platform
import distro
import sys
import time
from typing import Tuple, Dict

# Global configuration
VERBOSE = True
REQUIRED_MEMORY_GB = 4
REQUIRED_CPU_CORES = 2
REQUIRED_DISK_SPACE_GB = 20

def print_verbose(message: str, level: int = 0):
    """Print verbose output with indentation based on level"""
    if VERBOSE:
        prefix = "  " * level
        print(f"{prefix}{message}")

def run_command(command: str, use_sudo: bool = False, check: bool = True) -> Tuple[int, str, str]:
    """Run a shell command with verbose output"""
    if use_sudo:
        command = f"echo 'your_password' | sudo -S {command}"
    print_verbose(f"Executing: {command}", 1)
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True, env=os.environ)
    
    if result.returncode != 0 and check:
        print_verbose(f"Error running command: {command}", 1)
        print_verbose(f"Error output: {result.stderr}", 2)
    else:
        print_verbose(f"Command output: {result.stdout}", 2)

    return result.returncode, result.stdout, result.stderr

def check_system_resources() -> Dict[str, bool]:
    """Check system resources and return status"""
    print_verbose("Checking system resources...")
    status = {
        "memory": False,
        "cpu": False,
        "disk": False
    }
    
    # Check memory
    if platform.system() == "Linux":
        with open("/proc/meminfo") as f:
            meminfo = f.read()
            total_memory_kb = int(meminfo.split("MemTotal:")[1].split()[0])
            total_memory_gb = total_memory_kb / (1024 * 1024)
            status["memory"] = total_memory_gb >= REQUIRED_MEMORY_GB
            print_verbose(f"Total memory: {total_memory_gb:.2f}GB (Required: {REQUIRED_MEMORY_GB}GB)", 1)
    
    # Check CPU cores
    cpu_count = os.cpu_count()
    status["cpu"] = cpu_count >= REQUIRED_CPU_CORES
    print_verbose(f"CPU cores: {cpu_count} (Required: {REQUIRED_CPU_CORES})", 1)
    
    # Check disk space
    if platform.system() == "Linux":
        stat = os.statvfs('/')
        free_space_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
        status["disk"] = free_space_gb >= REQUIRED_DISK_SPACE_GB
        print_verbose(f"Free disk space: {free_space_gb:.2f}GB (Required: {REQUIRED_DISK_SPACE_GB}GB)", 1)
    
    return status

def check_docker() -> bool:
    """Check Docker installation and status"""
    print_verbose("Checking Docker installation...")
    
    # Check Docker version
    returncode, stdout, stderr = run_command("docker --version", check=False)
    if returncode != 0:
        print_verbose("Docker is not installed", 1)
        return False
    
    print_verbose(f"Docker version: {stdout.strip()}", 1)
    
    # Check Docker daemon
    returncode, stdout, stderr = run_command("docker info", check=False)
    if returncode != 0:
        print_verbose("Docker daemon is not running", 1)
        return False
    
    print_verbose("Docker daemon is running", 1)
    return True

def check_kubernetes() -> bool:
    """Check Kubernetes installation and status"""
    print_verbose("Checking Kubernetes installation...")
    
    # Check kubectl version
    returncode, stdout, stderr = run_command("kubectl version --client", check=False)
    if returncode != 0:
        print_verbose("kubectl is not installed", 1)
        return False
    
    print_verbose(f"kubectl version: {stdout.strip()}", 1)
    
    # Check cluster connection
    returncode, stdout, stderr = run_command("kubectl cluster-info", check=False)
    if returncode != 0:
        print_verbose("Cannot connect to Kubernetes cluster", 1)
        return False
    
    print_verbose("Connected to Kubernetes cluster", 1)
    return True

def check_helm() -> bool:
    """Check Helm installation"""
    print_verbose("Checking Helm installation...")
    
    returncode, stdout, stderr = run_command("helm version", check=False)
    if returncode != 0:
        print_verbose("Helm is not installed", 1)
        return False
    
    print_verbose(f"Helm version: {stdout.strip()}", 1)
    return True

def check_kind() -> bool:
    """Check Kind installation"""
    print_verbose("Checking Kind installation...")
    
    returncode, stdout, stderr = run_command("kind version", check=False)
    if returncode != 0:
        print_verbose("Kind is not installed", 1)
        return False
    
    print_verbose(f"Kind version: {stdout.strip()}", 1)
    return True

def determine_os_family() -> str:
    """Determine OS family with verbose output"""
    print_verbose("Detecting operating system...")
    platform_type = platform.system().lower()
    
    if platform_type == 'linux':
        os_family = distro.id().lower()
        if 'redhat' in os_family or 'centos' in os_family or 'fedora' in os_family or 'rocky' in os_family:
            print_verbose("Detected RedHat-based Linux distribution", 1)
            return 'redhat'
        elif 'debian' in os_family or 'ubuntu' in os_family:
            print_verbose("Detected Debian-based Linux distribution", 1)
            return 'debian'
    elif platform_type == 'darwin':
        print_verbose("Detected macOS", 1)
        return 'macos'
    elif platform_type == 'windows':
        print_verbose("Detected Windows", 1)
        return 'windows'
    
    print_verbose("Unknown operating system", 1)
    return 'unknown'

def install_kubernetes_tools():
    """Install Kubernetes tools with verbose output"""
    os_family = determine_os_family()
    print_verbose(f"Installing Kubernetes tools for {os_family}...")
    
    if os_family == 'windows':
        print_verbose("Installing kubectl and helm on Windows...", 1)
        run_command("choco install kubernetes-cli -y")
        run_command("choco install kubernetes-helm -y")
    elif os_family == 'redhat':
        print_verbose("Installing kubectl and helm on RHEL...", 1)
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
        print_verbose("Installing kubectl and helm on Debian...", 1)
        run_command("sudo apt-get install -y apt-transport-https ca-certificates curl")
        run_command("sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg")
        run_command("echo 'deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main' | sudo tee /etc/apt/sources.list.d/kubernetes.list")
        run_command("sudo apt-get update")
        run_command("sudo apt-get install -y kubectl")
        run_command("curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash")

def install_kind():
    """Install Kind with verbose output"""
    os_family = determine_os_family()
    print_verbose(f"Installing Kind for {os_family}...")
    
    if os_family == 'windows':
        print_verbose("Installing Kind on Windows...", 1)
        run_command("choco install kind -y")
    elif os_family in ['redhat', 'debian']:
        print_verbose("Installing Kind on Linux...", 1)
        run_command("curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64")
        run_command("chmod +x ./kind")
        run_command("sudo mv ./kind /usr/local/bin/kind")
    elif os_family == 'macos':
        print_verbose("Installing Kind on macOS...", 1)
        run_command("brew install kind")

def create_kind_cluster():
    """Create and verify Kind cluster"""
    print_verbose("Creating Kind cluster...")
    
    # Check if cluster already exists
    returncode, stdout, stderr = run_command("kind get clusters", check=False)
    if returncode == 0 and "awx-cluster" in stdout:
        print_verbose("Kind cluster 'awx-cluster' already exists", 1)
    else:
        # Create new cluster with specific name
        print_verbose("Creating new Kind cluster 'awx-cluster'...", 1)
        kind_config = """
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 30080
    hostPort: 30080
    protocol: TCP
"""
        with open("kind-config.yaml", "w") as f:
            f.write(kind_config)
        
        run_command("kind create cluster --name awx-cluster --config kind-config.yaml")
    
    # Verify cluster is ready
    print_verbose("Verifying cluster status...", 1)
    run_command("kubectl cluster-info")
    run_command("kubectl get nodes")

def deploy_awx_kubernetes():
    """Deploy AWX on Kubernetes with verbose output"""
    print_verbose("Deploying AWX on Kubernetes...")
    
    # Ensure cluster exists and is ready
    create_kind_cluster()
    
    print_verbose("Adding AWX operator Helm repository...", 1)
    run_command("helm repo add awx-operator https://ansible-community.github.io/awx-operator-helm/")
    run_command("helm repo update")
    
    print_verbose("Installing AWX operator...", 1)
    run_command("helm install awx-operator awx-operator/awx-operator")

    print_verbose("Creating AWX instance manifest...", 1)
    awx_manifest = """
apiVersion: awx.ansible.com/v1beta1
kind: AWX
metadata:
  name: awx
spec:
  service_type: nodeport
  nodeport_port: 30080
"""
    with open("awx-instance.yaml", "w") as f:
        f.write(awx_manifest)

    print_verbose("Applying AWX instance manifest...", 1)
    run_command("kubectl apply -f awx-instance.yaml")

def cleanup_awx():
    """Clean up AWX Tower deployment"""
    print_verbose("Cleaning up AWX Tower deployment...")
    
    # Delete AWX instance
    print_verbose("Deleting AWX instance...", 1)
    run_command("kubectl delete -f awx-instance.yaml")
    
    # Delete AWX operator
    print_verbose("Deleting AWX operator...", 1)
    run_command("helm uninstall awx-operator")
    
    # Delete Kind cluster
    print_verbose("Deleting Kind cluster...", 1)
    run_command("kind delete cluster --name awx-cluster")
    
    # Clean up local files
    print_verbose("Cleaning up local files...", 1)
    if os.path.exists("awx-instance.yaml"):
        os.remove("awx-instance.yaml")
    if os.path.exists("kind-config.yaml"):
        os.remove("kind-config.yaml")
    
    print("\n=== Cleanup Complete ===")
    print("AWX Tower deployment has been removed.")
    print("All associated resources have been cleaned up.")

def shutdown_awx():
    """Shutdown AWX Tower deployment while preserving configuration"""
    print_verbose("Shutting down AWX Tower deployment...")
    
    # Scale down AWX deployment
    print_verbose("Scaling down AWX deployment...", 1)
    run_command("kubectl scale deployment awx --replicas=0")
    
    # Scale down AWX operator
    print_verbose("Scaling down AWX operator...", 1)
    run_command("kubectl scale deployment awx-operator --replicas=0")
    
    print("\n=== Shutdown Complete ===")
    print("AWX Tower has been shut down.")
    print("Configuration is preserved for later use.")
    print("\nTo restart AWX, run:")
    print("python setup_awx_tower.py --start")

def start_awx():
    """Start AWX Tower deployment"""
    print_verbose("Starting AWX Tower deployment...")
    
    # Scale up AWX operator
    print_verbose("Starting AWX operator...", 1)
    run_command("kubectl scale deployment awx-operator --replicas=1")
    
    # Wait for operator to be ready
    print_verbose("Waiting for operator to be ready...", 1)
    time.sleep(10)
    
    # Scale up AWX deployment
    print_verbose("Starting AWX...", 1)
    run_command("kubectl scale deployment awx --replicas=1")
    
    # Wait for AWX to be ready and get the password
    print_verbose("Waiting for AWX to be ready...", 1)
    time.sleep(30)
    
    print_verbose("Retrieving admin password...", 1)
    returncode, stdout, stderr = run_command("kubectl get secret awx-admin-password -o jsonpath=\"{.data.password}\" | base64 --decode", check=False)
    
    print("\n=== Startup Complete ===")
    print("AWX Tower has been started. You should be able to access it at:")
    print("http://localhost:30080")
    print("\nDefault credentials:")
    print("Username: admin")
    print(f"Password: {stdout.strip()}")

def main():
    print("Starting AWX Tower setup with verbose output...")
    
    # Check system requirements
    print("\n=== Checking System Requirements ===")
    resource_status = check_system_resources()
    if not all(resource_status.values()):
        print("\nError: System does not meet minimum requirements:")
        for resource, status in resource_status.items():
            if not status:
                print(f"- {resource.capitalize()} requirements not met")
        sys.exit(1)
    
    # Check and install prerequisites
    print("\n=== Checking Prerequisites ===")
    if not check_docker():
        print("\nError: Docker is required but not installed or not running")
        sys.exit(1)
    
    if not check_kubernetes():
        print_verbose("Installing Kubernetes tools...")
        install_kubernetes_tools()
    
    if not check_helm():
        print("\nError: Helm is required but not installed")
        sys.exit(1)
    
    if not check_kind():
        print_verbose("Installing Kind...")
        install_kind()
    
    # Deploy AWX
    print("\n=== Deploying AWX ===")
    deploy_awx_kubernetes()
    
    # Wait for AWX to be ready and get the password
    print("\nWaiting for AWX to be ready...")
    time.sleep(30)  # Give some time for the secret to be created
    
    print_verbose("Retrieving admin password...", 1)
    returncode, stdout, stderr = run_command("kubectl get secret awx-admin-password -o jsonpath=\"{.data.password}\" | base64 --decode", check=False)
    
    print("\n=== Setup Complete ===")
    print("AWX Tower has been deployed. You should be able to access it at:")
    print("http://localhost:30080")
    print("\nDefault credentials:")
    print("Username: admin")
    print(f"Password: {stdout.strip()}")
    print("\nTo shut down AWX (preserving configuration), run:")
    print("python setup_awx_tower.py --shutdown")
    print("\nTo clean up the deployment completely, run:")
    print("python setup_awx_tower.py --cleanup")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--cleanup":
            cleanup_awx()
        elif sys.argv[1] == "--shutdown":
            shutdown_awx()
        elif sys.argv[1] == "--start":
            start_awx()
        else:
            print("Invalid option. Use --cleanup, --shutdown, or --start")
            sys.exit(1)
    else:
        main()


