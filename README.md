# SSO-onlooker: Advanced SSO Security Testing Script

A comprehensive Python-based security testing tool designed to identify and exploit Single Sign-On (SSO) vulnerabilities. This script tests for subdomain takeovers, SAML vulnerabilities, OAuth token theft, and cookie hijacking attacks.

**⚠️ DISCLAIMER**: This tool is intended for authorized security testing and educational purposes only. Unauthorized access to computer systems is illegal. Always obtain proper authorization before testing any target domain.

## Features

### 1. **Subdomain Enumeration**
- **Certificate Transparency Logs**: Queries `crt.sh` to discover subdomains from SSL/TLS certificates
- **DNS Brute Force**: Tests common subdomain patterns (www, mail, ftp, admin, api, dev, staging, etc.)
- **External Tool Integration**: Supports `subfinder` and `amass` if available for passive reconnaissance

### 2. **Subdomain Takeover Detection**
- Identifies misconfigured CNAME records pointing to vulnerable third-party services
- Detects fingerprints from 20+ vulnerable providers (GitHub Pages, Heroku, Netlify, AWS S3, Azure, Shopify, etc.)
- Checks HTTP response codes and content for takeover signatures
- Returns detailed information about vulnerable subdomains

### 3. **Subdomain Takeover Exploitation**
- Attempts to claim vulnerable subdomains using Selenium WebDriver
- Creates proof-of-concept pages on claimed subdomains
- Supports GitHub Pages exploitation workflow
- Customizable proof-of-concept content

### 4. **SAML Vulnerability Detection**
- Identifies SAML implementations on target domains
- Analyzes SAML requests/responses for security flaws:
  - Missing or unsigned assertions
  - Weak signature algorithms (MD5, SHA1)
  - Unencrypted SAML messages
  - Username/email injection points
- Extracts and parses Base64-encoded SAML XML

### 5. **OAuth Vulnerability Testing**
- Detects OAuth implementations
- Tests for common OAuth vulnerabilities:
  - **Open Redirects**: Validates redirect_uri parameter manipulation
  - **Token Leakage**: Identifies exposed access tokens and authorization codes
  - **Weak Client Secrets**: Attempts to guess common client secret patterns
- Analyzes OAuth endpoints for security misconfigurations

### 6. **Cookie Theft via Subdomain Takeover**
- Tests for cookie vulnerabilities through domain takeovers
- Identifies cookies with wildcard domain attributes
- Demonstrates cookie theft potential via compromised subdomains
- Confirms vulnerability chain: takeover → cookie access → authentication bypass

### 7. **Comprehensive Reporting**
- JSON-formatted vulnerability reports
- Console and file-based logging with timestamps
- Detailed vulnerability categorization and summary statistics
- Actionable remediation information

## Installation

### Prerequisites

- **Python 3.7+**
- **Google Chrome** (for Selenium WebDriver)
- **ChromeDriver** (matching your Chrome version)

### Step 1: Clone the Repository

```bash
git clone https://github.com/tkstanch/SSO-onlooker.git
cd SSO-onlooker
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or manually install required packages:

```bash
pip install requests dnspython beautifulsoup4 selenium
```

### Step 3: Install ChromeDriver

**macOS (Homebrew)**:
```bash
brew install chromedriver
```

**Ubuntu/Debian**:
```bash
sudo apt-get install chromium-chromedriver
# Or download from: https://chromedriver.chromium.org/
```

**Windows**:
- Download from: https://chromedriver.chromium.org/
- Add to PATH or place in the script directory

### Step 4: (Optional) Install External Reconnaissance Tools

For enhanced subdomain enumeration, install:

**subfinder**:
```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
```

**amass**:
```bash
brew install amass  # macOS
# or
sudo apt-get install amass  # Linux
```

## Usage

### Basic Syntax

```bash
python3 sso_scanner.py [target_domain] [options]
```

### Command-Line Arguments

| Argument | Short | Type | Default | Description |
|----------|-------|------|---------|-------------|
| `domain` | - | string | Required | Target domain to scan (e.g., `example.com`) |
| `--output` | `-o` | string | None | Output file for JSON report |
| `--custom-phrase` | `-c` | string | Default message | Custom text for takeover proof-of-concept pages |
| `--threads` | `-t` | integer | 10 | Number of concurrent threads for subdomain scanning |
| `--delay` | `-d` | float | 1.0 | Delay between requests in seconds (in-between random delays) |
| `--no-stealth` | - | flag | False | Disable stealth mode (headless browser, user-agent rotation) |

### Usage Examples

#### 1. Basic Scan
```bash
python3 sso_scanner.py example.com
```

#### 2. Scan with Report Output
```bash
python3 sso_scanner.py example.com -o report.json
```

#### 3. Custom Takeover Message
```bash
python3 sso_scanner.py example.com -c "Security research by [Your Name]" -o report.json
```

#### 4. Faster Scanning (More Threads, Less Delay)
```bash
python3 sso_scanner.py example.com -t 20 -d 0.5 -o report.json
```

#### 5. Slower Stealth Scanning (Less Detection)
```bash
python3 sso_scanner.py example.com -t 5 -d 2.0 --no-stealth -o report.json
```

#### 6. Complete Example
```bash
python3 sso_scanner.py example.com \
  --output results/example_com_report.json \
  --custom-phrase "Authorized security testing by ACME Security" \
  --threads 15 \
  --delay 1.5
```

## How the Script Works

### Execution Flow

```
┌─────────────────────────────────────────┐
│   1. Subdomain Enumeration              │
│   - CT Logs, DNS brute force, tools    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   2. Subdomain Takeover Detection       │
│   - Check CNAME records, signatures     │
│   - Parallel testing with ThreadPool    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   3. Exploitation Attempts              │
│   - Try to claim vulnerable subdomains  │
│   - Create proof-of-concept pages       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   4. SAML Vulnerability Check           │
│   - Identify SAML implementations       │
│   - Analyze for weak signatures, etc.   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   5. OAuth Vulnerability Check          │
│   - Detect OAuth endpoints              │
│   - Test redirects, token leakage, etc. │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   6. Cookie Theft Testing               │
│   - Test via claimed subdomains         │
│   - Identify cross-domain cookies       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   7. Report Generation & Logging        │
│   - JSON report + console output        │
└─────────────────────────────────────────┘
```

### Detailed Step Descriptions

#### Step 1: Subdomain Enumeration
- **Certificate Transparency**: Queries `https://crt.sh/?q=%.example.com&output=json` to find all subdomains from SSL certificates
- **DNS Brute Force**: Attempts to resolve 50+ common subdomain patterns
- **External Tools**: If `subfinder` or `amass` are installed, uses them for passive enumeration
- **Result**: List of discovered subdomains

#### Step 2: Subdomain Takeover Detection
- **DNS Lookup**: Checks each subdomain for CNAME records
- **Provider Matching**: Identifies if CNAME points to vulnerable services
- **HTTP Inspection**: Makes HTTP request and checks response for takeover signatures
- **Vulnerability Confirmation**: If signatures match (e.g., "No such app" for Heroku), marks as vulnerable
- **Parallel Processing**: Uses ThreadPoolExecutor to check multiple subdomains concurrently

#### Step 3: Subdomain Takeover Exploitation
- **Selenium Automation**: Uses Chrome WebDriver to automate registration process
- **GitHub Pages Workflow** (example):
  1. Navigate to GitHub repository creation page
  2. Create repository with the vulnerable subdomain name
  3. Enable GitHub Pages in repository settings
  4. Create `index.html` with proof-of-concept content
  5. Verify takeover by accessing the subdomain
- **Custom Content**: Includes timestamp and custom phrase in PoC page

#### Step 4: SAML Vulnerability Analysis
- **Implementation Detection**: Looks for SAML indicators in page source (SAMLRequest, SAMLResponse, etc.)
- **Flow Triggering**: Attempts to trigger SAML authentication flow
- **Message Extraction**: Extracts Base64-encoded SAML requests/responses from URLs or page source
- **XML Parsing**: Decodes and parses SAML XML for vulnerabilities:
  - **NO_SIGNATURE**: Unsigned SAML assertions (allows impersonation)
  - **WEAK_SIGNATURE**: MD5/SHA1 algorithms (vulnerable to collision attacks)
  - **NO_ENCRYPTION**: Unencrypted SAML messages (information disclosure)
  - **INJECTION_POINTS**: Username/email attributes vulnerable to injection

#### Step 5: OAuth Vulnerability Testing
- **Endpoint Discovery**: Scans page for OAuth indicators and endpoints
- **Open Redirect Testing**: Attempts to modify `redirect_uri` parameter with malicious values
  - Tests: `https://evil.com`, `//evil.com`, data URIs, javascript URIs
  - Checks HTTP redirects for successful exploitation
- **Token Leakage**: Checks responses for exposed access tokens or authorization codes
- **Client Secret Guessing**: Attempts common patterns: `{client_id}`, `{client_id}_secret`, `secret`, `admin`, etc.

#### Step 6: Cookie Theft Testing
- **Cookie Extraction**: Retrieves all cookies set on the main domain
- **Wildcard Detection**: Identifies cookies with domain set to `.example.com` (accessible to subdomains)
- **Takeover Chain**: Uses claimed subdomains to demonstrate cookie access
- **Vulnerability**: Proves authentication bypass through cookie theft

#### Step 7: Report Generation
- **JSON Output**: Structured report with findings, timestamps, and metadata
- **Console Logging**: Real-time output with severity levels (INFO, ERROR, WARNING)
- **Summary Statistics**: Counts of vulnerabilities by type
- **Detailed Findings**: Full information for each discovered vulnerability

### Code Structure

#### Main Classes

**`SSOVulnerabilityScanner`**: Core scanner class

Key methods:
- `enumerate_subdomains()`: Discovers subdomains
- `check_subdomain_takeover()`: Tests for takeover vulnerabilities
- `take_over_subdomain()`: Attempts exploitation
- `check_saml_vulnerabilities()`: Analyzes SAML implementations
- `check_oauth_vulnerabilities()`: Tests OAuth endpoints
- `test_cookie_theft_via_subdomain_takeover()`: Demonstrates cookie theft
- `generate_report()`: Creates and outputs report
- `run_scan()`: Orchestrates entire workflow

#### Key Features

- **User-Agent Rotation**: Randomizes browser identifiers to avoid detection
- **Random Delays**: Introduces delays between requests (configurable)
- **Stealth Mode**: Headless Chrome with automation detection disabled
- **Concurrent Processing**: ThreadPoolExecutor for parallel subdomain testing
- **Comprehensive Logging**: Timestamp and severity level on all messages
- **Error Handling**: Graceful exception handling with detailed error messages

## Output and Reports

### Console Output Example
```
[2026-06-08 10:15:30] [INFO] Starting SSO vulnerability scan for example.com
[2026-06-08 10:15:30] [INFO] Enumerating subdomains for example.com
[2026-06-08 10:15:45] [INFO] Found 12 subdomains
[2026-06-08 10:15:45] [INFO] Checking for subdomain takeovers
[2026-06-08 10:16:15] [INFO] Potential subdomain takeover found: old-api.example.com -> old-api.github.io
[2026-06-08 10:16:20] [INFO] Attempting to take over vulnerable subdomains
[2026-06-08 10:16:30] [INFO] Successfully claimed old-api.example.com

=== SCAN SUMMARY ===
Target: example.com
Subdomains scanned: 12
Subdomain takeovers found: 1
SAML vulnerabilities found: 0
OAuth vulnerabilities found: 2
Cookie theft vulnerabilities found: 1
```

### JSON Report Example
```json
{
  "scan_date": "2026-06-08 10:17:00",
  "target_domain": "example.com",
  "summary": {
    "subdomains_scanned": 12,
    "subdomain_takeovers": 1,
    "saml_vulnerabilities": 0,
    "oauth_vulnerabilities": 2,
    "cookie_theft_vulnerabilities": 1
  },
  "findings": {
    "subdomain_takeovers": [
      {
        "subdomain": "old-api.example.com",
        "cname": "old-api.github.io",
        "provider": "github.io",
        "signature": "There isn't a GitHub Pages site here",
        "status": "CLAIMED",
        "proof_url": "https://old-api.example.com"
      }
    ],
    "oauth_vulnerabilities": [
      {
        "endpoint": "https://example.com/oauth/authorize?client_id=123&redirect_uri=...",
        "vulnerability": "OPEN_REDIRECT",
        "malicious_uri": "https://evil.com",
        "status": "VULNERABLE"
      }
    ]
  }
}
```

## Vulnerable Providers Checked

The script tests for takeovers of these services:

| Provider | Common Signature | Registration |
|----------|------------------|--------------|
| GitHub Pages | "There isn't a GitHub Pages site here" | github.com/new |
| Heroku | "No such app" | dashboard.heroku.com |
| Netlify | "Not found" | app.netlify.com |
| AWS S3 | "NoSuchBucket" | aws.amazon.com/s3 |
| Azure | "The resource... has been removed" | portal.azure.com |
| Shopify | "Sorry, this shop is unavailable" | shopify.com |
| WordPress.com | "This site is not available" | wordpress.com |
| And 12+ others | Various | Various |

## Security Considerations

### Stealth and Detection Avoidance
- **Headless Mode**: Browser runs without GUI
- **User-Agent Rotation**: Changes browser identifier per request
- **Automation Detection Disabled**: Hides Selenium fingerprints
- **Request Delays**: Randomized delays between requests to appear human
- **Concurrent Limits**: Configurable thread pool to avoid rate-limit triggers

### Responsible Use
1. **Authorization**: Only test domains you own or have explicit written permission to test
2. **Scope**: Stick to vulnerability identification, avoid destructive actions
3. **Data**: Do not access or exfiltrate sensitive information
4. **Reporting**: Report findings responsibly to the domain owner
5. **Cleanup**: Remove all proof-of-concept pages after testing

## Troubleshooting

### ChromeDriver Issues
```bash
# Update ChromeDriver to match your Chrome version
# Check Chrome version: chrome://version/
# Download matching ChromeDriver: https://chromedriver.chromium.org/
```

### DNS Resolution Errors
```bash
# Check internet connectivity
ping 8.8.8.8

# Verify DNS configuration
nslookup example.com
```

### SSL Certificate Errors
```bash
# Disable SSL verification (not recommended)
# Modify requests.session() calls to use verify=False
```

### Timeout Errors
- Increase `--delay` parameter
- Decrease `--threads` parameter
- Check target domain availability

### No Subdomains Found
- Verify domain is valid
- Check for DNS issues
- Install `subfinder` or `amass` for better enumeration
- Query `https://crt.sh/?q=example.com` directly

## Performance Tips

| Goal | Settings |
|------|----------|
| **Fast Scanning** | `-t 20 -d 0.5` |
| **Stealth** | `-t 5 -d 2.0` |
| **Balanced** | `-t 10 -d 1.0` (default) |
| **Limited Bandwidth** | `-t 3 -d 3.0` |

## Legal and Ethical Notes

**This tool is for authorized security testing only.**

- Unauthorized access to computer systems is **illegal**
- Always obtain written permission before testing
- Responsible disclosure of findings is required
- Comply with local laws and regulations
- Use for educational purposes only on systems you control

## Contributing

Contributions are welcome! Areas for improvement:

- Additional vulnerable provider signatures
- More OAuth vulnerability tests
- Enhanced SAML analysis
- Additional authentication protocols (OpenID Connect, etc.)
- Better reporting formats

## License

[Add your license here - MIT recommended]

## Author

**tkstanch** - Security Researcher

## References

- [OWASP Subdomain Takeover](https://owasp.org/www-community/Subdomain_Takeover)
- [CVE-2023-XXXXX](https://cve.mitre.org) - SAML/OAuth vulnerabilities
- [CWE-601: URL Redirection to Untrusted Site](https://cwe.mitre.org/data/definitions/601.html)
- [RFC 6749 - OAuth 2.0 Authorization Framework](https://tools.ietf.org/html/rfc6749)
- [SAML 2.0 Security Considerations](https://docs.oasis-open.org/security/saml/v2.0/saml-security-2.0-os.pdf)

---

⚠️ **Use responsibly and legally.**
