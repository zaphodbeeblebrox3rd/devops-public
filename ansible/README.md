# Ansible Development Environment

This repository contains scripts to help you set up both Ansible Community Edition (CE) and AWX Tower, providing you with flexible options for your automation needs.

## Ansible CE vs AWX Tower: Understanding the Differences

### Ansible Community Edition
- **Open-source** automation platform maintained by the community
- **Command-line based** workflow
- Perfect for **script-based** automation workflows
- No built-in UI for management
- Ideal for developers and small teams
- Free to use

### AWX Tower
- **Web-based UI** for Ansible automation
- The **upstream open-source project** that powers Red Hat Ansible Automation Platform
- Provides **role-based access control** (RBAC)
- Features **job scheduling and real-time job status updates**
- Offers **dashboard and reporting capabilities**
- Requires Kubernetes for deployment
- Ideal for teams that need centralized management and visibility

## Setup Instructions

### Prerequisites
- Python 3.11 or higher
- Internet connectivity for downloading packages
- For Windows users: Windows Subsystem for Linux (WSL) with Ubuntu

### Setting Up the Environment

#### 1. Install Miniconda

**For Windows (using WSL with Ubuntu):**
```bash
# First, ensure WSL is installed and Ubuntu is set up
# Open PowerShell as Administrator and run:
wsl --install -d Ubuntu

# After installation, open Ubuntu from the Start menu
# Then follow the Linux/Ubuntu instructions below
```

**For Linux and Windows (with WSL):**
```bash
# Download the Miniconda installer
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh

# Make the installer executable
chmod +x ~/miniconda.sh

# Run the installer (press Enter and type "yes" when prompted)
bash ~/miniconda.sh

# Restart your shell or run:
source ~/.bashrc
```

**For macOS:**
```bash
# Download the installer
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh

# Make the installer executable
chmod +x Miniconda3-latest-MacOSX-x86_64.sh

# Run the installer
./Miniconda3-latest-MacOSX-x86_64.sh
```

#### 2. Create and Activate Python 3.11 Environment

```bash
# Create a new environment with Python 3.11
conda create -n ansible_env python=3.11

# Activate the environment
conda activate ansible_env
```

#### 3. Install Requirements

```bash
# Navigate to the project directory
cd path/to/project

# Install requirements
pip install -r ansible/requirements.txt
```

### Running the Scripts

#### Install Ansible Community Edition

The `install_ansible_ce.py` script automates the installation of Ansible CE and allows you to select popular collections to install.

```bash
# Make sure your conda environment is activated
conda activate ansible_env

# Run the script
python ansible/install_ansible_ce.py
```

**What this script does:**
- Detects your operating system
- Ensures Python and pip are installed
- Installs Ansible via pip
- Presents a menu of popular Ansible collections for you to install
- Installs your selected collections

#### Set Up AWX Tower

The `setup_awx_tower.py` script automates the deployment of AWX Tower in a Kubernetes environment.

```bash
# Make sure your conda environment is activated
conda activate ansible_env

# Run the script
python ansible/setup_awx_tower.py
```

**What this script does:**
- Installs Kubernetes tools (kubectl, helm)
- Installs Kind (Kubernetes in Docker)
- Creates a Kind cluster if one doesn't exist
- Deploys AWX using Helm charts
- Configures a NodePort service for access

After running the script, AWX Tower will be available at `http://localhost:NodePort`, where NodePort is the port assigned by Kubernetes. You can find this port by running:

```bash
kubectl get service -n default awx-service -o jsonpath='{.spec.ports[0].nodePort}'
```

The default credentials for AWX are:
- Username: `admin`
- Password: Look up the password in the Kubernetes secret:
  ```bash
  kubectl get secret awx-admin-password -o jsonpath="{.data.password}" | base64 --decode
  ```

## Troubleshooting

### Common Issues with Ansible CE

- **Missing dependencies**: Make sure the Python packages in requirements.txt are installed correctly
- **Permission issues**: Some commands may require sudo privileges
- **Path issues**: Ensure the Ansible executables are in your PATH
- **Windows-specific issues**: If you encounter issues on Windows, ensure you're using WSL with Ubuntu and not running commands directly in Windows

### Common Issues with AWX Tower

- **Kubernetes cluster not starting**: Verify Docker is running and has sufficient resources
- **Helm installation fails**: Check internet connectivity and firewall settings
- **AWX pods not ready**: Check pod status with `kubectl get pods` and check logs with `kubectl logs <pod-name>`

## Additional Resources

- [Ansible Documentation](https://docs.ansible.com/)
- [AWX Documentation](https://github.com/ansible/awx/tree/devel/docs)
- [Kubernetes Documentation](https://kubernetes.io/docs/home/)
- [Helm Documentation](https://helm.sh/docs/)
- [WSL Documentation](https://docs.microsoft.com/en-us/windows/wsl/)

## Support

If you encounter issues, please open a GitHub issue in this repository, including:
- The command you ran
- The full error message
- Your operating system (and WSL version if applicable)
- Your Python version (run `python --version`)
