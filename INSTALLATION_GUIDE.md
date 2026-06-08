# INSTALLATION_GUIDE.md - Detailed Setup Instructions

## System Requirements

- **Python**: 3.7 or higher
- **OS**: Linux, macOS, or Windows
- **RAM**: Minimum 2GB (4GB recommended)
- **Disk Space**: 500MB for dependencies and reports
- **Internet**: Required for API calls and reconnaissance

## Installation Steps

### 1. Install Python 3.7+

#### macOS
```bash
# Using Homebrew
brew install python@3.11

# Verify installation
python3 --version
```

#### Ubuntu/Debian
```bash
# Update package manager
sudo apt-get update

# Install Python
sudo apt-get install python3 python3-pip

# Verify installation
python3 --version
pip3 --version
```

#### Windows
1. Download Python from https://www.python.org/downloads/
2. Run installer and **check "Add Python to PATH"**
3. Open Command Prompt and verify:
```cmd
python --version
pip --version
```

### 2. Clone the Repository

```bash
# Using git
git clone https://github.com/tkstanch/SSO-onlooker.git
cd SSO-onlooker

# Or download as ZIP from GitHub and extract
```

### 3. Create Virtual Environment (Recommended)

Virtual environments isolate project dependencies from system Python.

#### macOS/Linux
```bash
# Create virtual environment
python3 -m venv sso_env

# Activate virtual environment
source sso_env/bin/activate

# Verify activation (you should see "(sso_env)" in terminal)
which python
```

#### Windows
```cmd
# Create virtual environment
python -m venv sso_env

# Activate virtual environment
sso_env\Scripts\activate

# Verify activation (you should see "(sso_env)" in terminal)
where python
```

### 4. Install Python Dependencies

```bash
# Ensure virtual environment is activated
pip install -r requirements.txt

# Verify installation
pip list
```

**Package Details:**
- `requests`: HTTP library for API calls
- `dnspython`: DNS resolution and queries
- `beautifulsoup4`: HTML/XML parsing
- `selenium`: Web browser automation

### 5. Install ChromeDriver

ChromeDriver is required for Selenium WebDriver automation.

#### macOS (Homebrew - Easiest)
```bash
brew install chromedriver

# Verify installation
chromedriver --version
```

#### macOS (Manual Download)
```bash
# 1. Check Chrome version: Go to Chrome menu > About Google Chrome
# 2. Download matching ChromeDriver from https://chromedriver.chromium.org/
# 3. Extract and move to system PATH
sudo mv ~/Downloads/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
chromedriver --version
```

#### Ubuntu/Debian
```bash
# Method 1: Using APT
sudo apt-get install chromium-chromedriver

# Or Method 2: Manual download
# 1. Check Chrome version: google-chrome --version
# 2. Download from https://chromedriver.chromium.org/
# 3. Extract to /usr/local/bin/
sudo mv ~/Downloads/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
chromedriver --version
```

#### Windows
```cmd
# 1. Check Chrome version: Settings > About Chrome
# 2. Download matching version from https://chromedriver.chromium.org/
# 3. Extract chromedriver.exe to project directory or add to PATH

# Add to PATH environment variable:
# Right-click "This PC" > Properties > Advanced system settings > 
# Environment Variables > Edit PATH > Add C:\path\to\chromedriver

# Verify installation
chromedriver --version
```

### 6. Verify Installation

```bash
# Test Python and dependencies
python3 -c "import requests, dns.resolver, bs4, selenium; print('All dependencies installed!')"

# Test ChromeDriver
chromedriver --version

# Test script import
python3 -c "from sso_scanner import SSOVulnerabilityScanner; print('Script loads successfully!')"
```

## Optional: Install Reconnaissance Tools

These tools enhance subdomain enumeration but are not required.

### Install subfinder

**macOS:**
```bash
brew install subfinder
```

**Ubuntu/Debian:**
```bash
wget https://github.com/projectdiscovery/subfinder/releases/download/v2.6.5/subfinder_2.6.5_linux_amd64.tar.gz
tar -xvf subfinder_2.6.5_linux_amd64.tar.gz
sudo mv subfinder /usr/local/bin/
chmod +x /usr/local/bin/subfinder
```

**Windows:**
```cmd
# Download from: https://github.com/projectdiscovery/subfinder/releases
# Extract and add to PATH
```

### Install amass

**macOS:**
```bash
brew install amass
```

**Ubuntu/Debian:**
```bash
sudo snap install amass
# Or download binary from: https://github.com/OWASP/Amass/releases
```

**Windows:**
```cmd
# Download from: https://github.com/OWASP/Amass/releases
# Extract and add to PATH
```

Verify installation:
```bash
subfinder --version
amass --help
```

## Troubleshooting Installation

### Issue: ChromeDriver Not Found
```bash
# Solution: Ensure ChromeDriver is in PATH
which chromedriver  # macOS/Linux
where chromedriver  # Windows

# Or specify full path in script
export PATH=$PATH:/usr/local/bin
```

### Issue: Python Dependencies Won't Install
```bash
# Update pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel

# Try installing again
pip install -r requirements.txt

# Or install packages individually
pip install requests==2.28.0
pip install dnspython==2.3.0
pip install beautifulsoup4==4.11.0
pip install selenium==4.10.0
```

### Issue: Permission Denied on ChromeDriver
```bash
# Fix permissions
chmod +x /usr/local/bin/chromedriver

# Or move to writeable location
mv /usr/local/bin/chromedriver ~/chromedriver
export PATH="$HOME:$PATH"
```

### Issue: Chrome/Chromium Not Found
```bash
# macOS: Install Chrome
brew install google-chrome

# Ubuntu: Install Chromium
sudo apt-get install chromium-browser

# Verify
google-chrome --version
chromium-browser --version
```

### Issue: DNS Resolution Fails
```bash
# Test DNS
nslookup example.com
dig example.com

# Check system DNS
cat /etc/resolv.conf  # Linux/macOS
ipconfig /all         # Windows

# Configure different DNS
# Edit /etc/resolv.conf to use 8.8.8.8 (Google DNS)
```

## Deactivating Virtual Environment

When finished, deactivate the virtual environment:

```bash
# macOS/Linux
deactivate

# Or just close the terminal
```

## Uninstallation

To remove SSO-onlooker:

```bash
# Remove virtual environment
rm -rf sso_env

# Remove repository
rm -rf SSO-onlooker

# Uninstall ChromeDriver (optional)
rm /usr/local/bin/chromedriver
```

## Quick Start After Installation

```bash
# Activate virtual environment
source sso_env/bin/activate  # macOS/Linux
sso_env\Scripts\activate     # Windows

# Run basic scan
python3 sso_scanner.py example.com

# Run with output file
python3 sso_scanner.py example.com -o report.json

# Deactivate when done
deactivate
```

## Platform-Specific Notes

### macOS M1/M2 (Apple Silicon)
```bash
# Install Python for ARM64
brew install python@3.11

# Most packages support Apple Silicon
# If you get "no suitable image" error:
arch -x86_64 python3 -m pip install -r requirements.txt
```

### Windows Subsystem for Linux (WSL)
```bash
# WSL2 with Ubuntu
wsl --install

# Inside WSL, follow Ubuntu/Debian instructions
sudo apt-get update
sudo apt-get install python3 python3-pip chromium-chromedriver
```

### Docker (Alternative)
Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y chromium chromium-driver

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY sso_scanner.py .

ENTRYPOINT ["python3", "sso_scanner.py"]
```

Build and run:
```bash
docker build -t sso-onlooker .
docker run sso-onlooker example.com -o report.json
```
