#!/usr/bin/env python3
"""
Extract server IP addresses from the FreeOllama server list page.
"""

import re
import sys
import warnings
from urllib.parse import urljoin

# Suppress SSL warnings due to expired certificate
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing required dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4", "requests"])
    from bs4 import BeautifulSoup

try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests


def extract_server_ips(html_content, base_url="https://freeollama.oneplus1.top/"):
    """Extract server IP addresses from HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all links or server list items
    servers = set()

    # Try common patterns: <a href="http://IP:PORT">
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Check if href looks like a server URL
        server_match = re.match(r'^https?://([^:]+):(\d+)(/.*)?$', href)
        if server_match:
            ip = server_match.group(1)
            port = server_match.group(2)
            servers.add(f"{ip}:{port}")

    # Try to find IPs in text content
    text_content = soup.get_text()
    ip_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{2,5})')
    for match in ip_pattern.finditer(text_content):
        ip = match.group(1)
        port = match.group(2)
        servers.add(f"{ip}:{port}")

    return sorted(servers)


def main():
    url = "https://freeollama.oneplus1.top/?search=qwen3.5&page_size=100"

    print(f"Fetching {url}...")
    try:
        # Disable SSL verification due to expired certificate
        response = requests.get(url, timeout=30, verify=False)
        response.raise_for_status()
        print(f"✓ Page fetched successfully (status: {response.status_code})")
    except requests.RequestException as e:
        print(f"✗ Failed to fetch page: {e}")
        sys.exit(1)

    servers = extract_server_ips(response.text)

    print(f"\nFound {len(servers)} server(s):")
    print("=" * 60)
    for server in servers:
        print(server)

    # Save to file
    output_file = "servers.txt"
    with open(output_file, 'w') as f:
        for server in servers:
            f.write(f"{server}\n")
    print(f"\n✓ Servers saved to {output_file}")


if __name__ == "__main__":
    main()