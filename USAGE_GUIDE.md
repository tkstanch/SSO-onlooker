# USAGE_GUIDE.md - Complete Usage Examples and Tutorials

## Quick Start

### 1. Basic Scan (Simplest)
```bash
python3 sso_scanner.py example.com
```

### 2. Scan with Report Output
```bash
python3 sso_scanner.py example.com -o report.json
```

### 3. View the Report
```bash
# macOS/Linux
cat report.json | python3 -m json.tool

# Or use any JSON viewer
```

## Command Reference

### Full Syntax
```bash
python3 sso_scanner.py DOMAIN [OPTIONS]
```

### Options

| Option | Short | Type | Default | Purpose |
|--------|-------|------|---------|---------|
| `domain` | - | string | Required | Target domain (e.g., acme.com) |
| `--output` | `-o` | string | None | Save JSON report to file |
| `--custom-phrase` | `-c` | string | Default | Custom text for PoC pages |
| `--threads` | `-t` | int | 10 | Concurrent subdomain checks |
| `--delay` | `-d` | float | 1.0 | Delay between requests (seconds) |
| `--no-stealth` | - | flag | - | Disable headless mode & user-agent rotation |

## Usage Scenarios

### Scenario 1: Quick Assessment

**Goal**: Fast initial scan to identify major vulnerabilities

```bash
python3 sso_scanner.py startup.io -t 20 -d 0.5 -o quick_scan.json
```

**Explanation:**
- `-t 20`: Use 20 threads for parallel scanning (faster)
- `-d 0.5`: Minimal delay between requests
- `-o quick_scan.json`: Save results for later analysis

**When to use:** Initial reconnaissance, non-sensitive targets

---

### Scenario 2: Careful/Stealthy Scan

**Goal**: Avoid rate-limiting and IDS detection

```bash
python3 sso_scanner.py enterprise.com -t 5 -d 2.0 -o stealth_scan.json
```

**Explanation:**
- `-t 5`: Fewer concurrent threads
- `-d 2.0`: 2 second delays between requests
- Script uses headless browser by default (stealth mode)
- User-agent rotation enabled

**When to use:** Sensitive targets, protected systems, high security environments

---

### Scenario 3: Comprehensive Deep Scan

**Goal**: Thorough vulnerability assessment

```bash
python3 sso_scanner.py company.com \
  --output results/company_scan_$(date +%Y%m%d_%H%M%S).json \
  --custom-phrase "Authorized security assessment by ACME Corp" \
  --threads 15 \
  --delay 1.5
```

**Explanation:**
- Dynamic filename with timestamp
- Custom message for PoC pages
- Balanced settings (15 threads, 1.5s delay)

**When to use:** Full security audits with authorization

---

### Scenario 4: Multiple Domain Scanning

**Goal**: Scan several domains in batch

```bash
#!/bin/bash
# scan_multiple.sh

DOMAINS=("company1.com" "company2.io" "startup.net")
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

for domain in "${DOMAINS[@]}"; do
  echo "Scanning $domain..."
  python3 sso_scanner.py "$domain" \
    -o "results/${domain}_${TIMESTAMP}.json" \
    -t 10 \
    -d 1.0
  echo "Completed $domain scan"
  sleep 60  # Wait between domain scans
done

echo "All scans completed!"
```

**Usage:**
```bash
chmod +x scan_multiple.sh
./scan_multiple.sh
```

---

### Scenario 5: Minimal Output (Verbose Logging)

**Goal**: See detailed progress without file output

```bash
python3 sso_scanner.py example.com --no-stealth
```

**Explanation:**
- `--no-stealth`: Shows visible browser window and detailed output
- Good for debugging and monitoring progress
- Console logging shows real-time findings

**When to use:** Development, debugging, understanding script behavior

---

## Report Analysis

### Understanding JSON Output

```json
{
  "scan_date": "2026-06-08 14:30:00",
  "target_domain": "example.com",
  "summary": {
    "subdomains_scanned": 25,
    "subdomain_takeovers": 2,
    "saml_vulnerabilities": 1,
    "oauth_vulnerabilities": 3,
    "cookie_theft_vulnerabilities": 1
  },
  "findings": {
    "subdomain_takeovers": [
      {
        "subdomain": "old-api.example.com",
        "cname": "old-api.github.io",
        "provider": "github.io",
        "signature": "There isn't a GitHub Pages site here",
        "status": "VULNERABLE",
        "proof_url": "https://old-api.example.com"
      }
    ],
    "saml_vulnerabilities": [
      {
        "url": "https://example.com/sso/saml",
        "vulnerabilities": [
          "WEAK_SIGNATURE",
          "NO_ENCRYPTION"
        ],
        "status": "VULNERABLE"
      }
    ],
    "oauth_vulnerabilities": [
      {
        "endpoint": "https://example.com/oauth/authorize",
        "vulnerability": "OPEN_REDIRECT",
        "malicious_uri": "https://evil.com",
        "status": "VULNERABLE"
      }
    ]
  }
}
```

### Key Findings to Prioritize

1. **CRITICAL**: Subdomain takeovers (complete account compromise)
2. **HIGH**: Open redirects in OAuth (phishing attacks)
3. **HIGH**: Token leakage (session hijacking)
4. **MEDIUM**: Weak SAML signatures (impersonation)
5. **MEDIUM**: Missing encryption (information disclosure)
6. **LOW**: Cookie theft (requires other vulnerabilities)

---

## Advanced Techniques

### Technique 1: API Integration

Process results programmatically:

```python
import json
import subprocess

def scan_and_analyze(domain, output_file):
    """Scan domain and analyze results"""
    
    # Run scan
    cmd = [
        "python3", "sso_scanner.py", domain,
        "-o", output_file,
        "-t", "15"
    ]
    subprocess.run(cmd)
    
    # Analyze results
    with open(output_file) as f:
        report = json.load(f)
    
    # Extract critical findings
    critical = []
    if report["findings"]["subdomain_takeovers"]:
        critical.extend(report["findings"]["subdomain_takeovers"])
    
    if report["findings"]["oauth_vulnerabilities"]:
        critical.extend([
            v for v in report["findings"]["oauth_vulnerabilities"]
            if v["vulnerability"] == "OPEN_REDIRECT"
        ])
    
    # Send alerts
    for finding in critical:
        print(f"CRITICAL: {finding}")
        # Send to security monitoring system
    
    return report

# Usage
report = scan_and_analyze("example.com", "report.json")
```

---

### Technique 2: Scheduled Scanning

Run scans automatically on a schedule:

```bash
#!/bin/bash
# scheduled_scan.sh - Daily security scanning

DOMAIN="company.com"
RESULTS_DIR="/var/log/sso_scans"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $RESULTS_DIR

# Run scan
python3 /opt/sso_scanner/sso_scanner.py $DOMAIN \
  -o "$RESULTS_DIR/${DOMAIN}_${TIMESTAMP}.json" \
  -t 15 \
  -d 1.5

# Alert on critical findings
python3 << 'EOF'
import json
import subprocess
import sys

with open("$RESULTS_DIR/${DOMAIN}_${TIMESTAMP}.json") as f:
    report = json.load(f)

critical_count = (
    len(report["findings"]["subdomain_takeovers"]) +
    len(report["findings"]["saml_vulnerabilities"]) +
    len(report["findings"]["oauth_vulnerabilities"])
)

if critical_count > 0:
    # Send email alert
    subprocess.run([
        "mail", "-s", f"SSO Vulnerabilities Found: {critical_count}",
        "security@company.com"
    ])
EOF
```

Add to crontab:
```bash
# Daily scan at 2 AM
0 2 * * * /path/to/scheduled_scan.sh
```

---

### Technique 3: Continuous Monitoring

Monitor specific subdomains over time:

```python
#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime
import time

def monitor_domain(domain, interval_hours=24):
    """Continuously monitor domain for new vulnerabilities"""
    
    history = []
    
    while True:
        print(f"[{datetime.now()}] Scanning {domain}...")
        
        # Run scan
        output_file = f"monitor_{domain}_{int(time.time())}.json"
        subprocess.run([
            "python3", "sso_scanner.py", domain,
            "-o", output_file,
            "-t", "10"
        ])
        
        # Load results
        with open(output_file) as f:
            report = json.load(f)
        
        # Check for new vulnerabilities
        findings = report["findings"]
        total = (
            len(findings["subdomain_takeovers"]) +
            len(findings["saml_vulnerabilities"]) +
            len(findings["oauth_vulnerabilities"])
        )
        
        history.append({
            "timestamp": datetime.now().isoformat(),
            "total_vulnerabilities": total,
            "findings": findings
        })
        
        # Alert on increase
        if len(history) > 1:
            prev_total = history[-2]["total_vulnerabilities"]
            if total > prev_total:
                print(f"⚠️  NEW VULNERABILITIES DETECTED: {total - prev_total} new issues")
        
        print(f"Total vulnerabilities: {total}")
        print(f"Next scan in {interval_hours} hours...")
        
        time.sleep(interval_hours * 3600)

if __name__ == "__main__":
    monitor_domain("example.com", interval_hours=24)
```

---

## Troubleshooting Scans

### Issue: Scan Hangs/Times Out

**Solution:**
```bash
# Reduce concurrency and increase delays
python3 sso_scanner.py example.com -t 3 -d 3.0

# Or set a timeout manually
timeout 300 python3 sso_scanner.py example.com
```

---

### Issue: Rate Limiting (429 Errors)

**Solution:**
```bash
# Increase delays significantly
python3 sso_scanner.py example.com -t 2 -d 5.0

# Or use with proxy (manual modification needed)
```

---

### Issue: No Subdomains Found

**Solution:**
```bash
# Install and use external tools
brew install subfinder amass

# Verify subdomain enumeration
python3 sso_scanner.py example.com --no-stealth

# Check manually
curl https://crt.sh/?q=example.com
```

---

### Issue: Chrome/Selenium Errors

**Solution:**
```bash
# Verify ChromeDriver matches Chrome version
google-chrome --version
chromedriver --version

# Update ChromeDriver
brew upgrade chromedriver

# Or run without stealth mode
python3 sso_scanner.py example.com --no-stealth
```

---

## Performance Optimization

### Settings by Target Type

| Target Type | Threads | Delay | Speed | Stealth |
|------------|---------|-------|-------|---------|
| Large enterprise | 5 | 2.0s | Slow | High |
| Medium company | 10 | 1.0s | Medium | Medium |
| Startup/small | 15 | 0.5s | Fast | Low |
| Development/test | 20 | 0.2s | Very fast | N/A |

### Memory Usage
- Default: ~200MB
- High threads (20): ~500MB
- Low threads (3): ~100MB

---

## Output Examples

### Success Output
```
[2026-06-08 14:30:15] [INFO] Starting SSO vulnerability scan for example.com
[2026-06-08 14:30:15] [INFO] Enumerating subdomains for example.com
[2026-06-08 14:30:45] [INFO] Found 18 subdomains
[2026-06-08 14:30:46] [INFO] Checking for subdomain takeovers
[2026-06-08 14:31:22] [INFO] Potential subdomain takeover found: old-api.example.com -> old-api.github.io
[2026-06-08 14:31:25] [INFO] Attempting to take over vulnerable subdomains
[2026-06-08 14:31:45] [INFO] Successfully claimed old-api.example.com
[2026-06-08 14:31:46] [INFO] Checking for SAML vulnerabilities
[2026-06-08 14:31:50] [INFO] SAML implementation detected
[2026-06-08 14:32:15] [INFO] SAML vulnerabilities found: NO_ENCRYPTION, WEAK_SIGNATURE
[2026-06-08 14:32:16] [INFO] Checking for OAuth vulnerabilities
[2026-06-08 14:32:45] [INFO] OAuth open redirect found: https://example.com/oauth -> https://evil.com
[2026-06-08 14:33:00] [INFO] SSO vulnerability scan completed
[2026-06-08 14:33:01] [INFO] Report saved to report.json
```

---

## Next Steps

1. **Review Results**: Analyze JSON report for vulnerabilities
2. **Prioritize**: Focus on critical findings first
3. **Report**: Document findings in security assessment
4. **Remediate**: Work with development team to fix issues
5. **Verify**: Rerun scan after fixes to confirm resolution

