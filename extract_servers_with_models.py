#!/usr/bin/env python3
"""
Extract server IP addresses and their deployed models (starting with qwen3.6).
"""

import re
import sys
import warnings
import time
from urllib.parse import urljoin

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

# Suppress SSL warnings due to expired certificate
warnings.filterwarnings('ignore', message='Unverified HTTPS request')


def extract_server_ips(html_content):
    """Extract server IP addresses from HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    servers = set()

    # Find all links or server list items
    for link in soup.find_all('a', href=True):
        href = link['href']
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


def query_server_models(server_url):
    """Query a server for its deployed models using Ollama API."""
    try:
        # Try different API endpoints
        endpoints = [
            f"{server_url}/api/tags",
            f"{server_url}/api/v1/tags",
            f"http://{server_url}/api/tags",
            f"https://{server_url}/api/tags",
        ]

        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=2, verify=False)
                if response.status_code == 200:
                    data = response.json()
                    models = data.get('models', [])
                    model_names = [m.get('name', '') for m in models]
                    return model_names
            except requests.RequestException:
                continue

    except Exception as e:
        print(f"    ✗ Error querying {server_url}: {e}")
    return []


def filter_models(model_names, key : None):
    """Filter models that contain 'qwen3.6' (not 'qwen3.5')."""
    return [model for model in model_names if key in model]


def main():
    base_url = "https://freeollama.oneplus1.top/?search=glm-4.7&page_size=100"

    print(f"Fetching {base_url}...")
    try:
        response = requests.get(base_url, timeout=30, verify=False)
        response.raise_for_status()
        print(f"✓ Page fetched successfully (status: {response.status_code})")
    except requests.RequestException as e:
        print(f"✗ Failed to fetch page: {e}")
        sys.exit(1)

    servers = extract_server_ips(response.text)

    print(f"\nFound {len(servers)} server(s), querying for models...")
    print("=" * 80)

    results = []
    for i, server in enumerate(servers, 1):
        print(f"[{i}/{len(servers)}] {server}", end=' ')
        time.sleep(0.5)  # Rate limiting

        models = query_server_models(server)
        models = filter_models(models,key="glm-4.7")

        if models:
            print(f"✓ {len(models)} found model(s)")
            for model in models:
                results.append(f"{server}|{model}")
        else:
            print(f"✗ No models")

    # Save to file
    output_file = "server_models.txt"
    with open(output_file, 'w') as f:
        for item in results:
            f.write(f"{item}\n")
    print(f"\n{'=' * 80}")
    print(f"✓ Results saved to {output_file}")
    print(f"Found {len(results)} server-model pairs ")

    # Print summary
    print(f"\n{'=' * 80}")
    print("Server-Model Pairs (Server | Model):")
    print("=" * 80)
    for item in sorted(results):
        server, model = item.split('|')
        print(f"{server} -> {model}")


if __name__ == "__main__":
    main()