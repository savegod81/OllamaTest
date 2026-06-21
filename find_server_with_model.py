#!/usr/bin/env python3
"""
Find Ollama servers that have a specific model deployed.
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


def extract_server_ips(html_content, base_url="https://freeollama.oneplus1.top/"):
    """Extract server IP addresses from HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    servers = set()

    # Try common patterns: <a href="http://IP:PORT">
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


def query_server_models(server_url, model_key):
    """Query a server for its deployed models and filter for specific model."""
    try:
        # Try different API endpoints
        endpoints = [
            f"http://{server_url}/api/tags",
            f"http://{server_url}/api/v1/tags",
        ]

        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=2, verify=False)
                if response.status_code == 200:
                    data = response.json()
                    models = data.get('models', [])
                    # Filter models that contain the key
                    model_names = [m.get('name', '') for m in models if model_key in m.get('name', '')]
                    return model_names
            except requests.RequestException:
                continue

    except Exception as e:
        print(f"    ✗ Error querying {server_url}: {e}")
    return []


def test_reachability(server_url):
    """Test if a server is reachable."""
    try:
        # Build proper URL with http:// prefix
        url = f"http://{server_url}/api/tags"
        response = requests.get(url, timeout=5, verify=False) 
        return response.status_code == 200
    except requests.RequestException as e: 
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python find_server_with_model.py <model_name>")
        print("Example: python find_server_with_model.py glm-4.7-flash")
        sys.exit(1)

    model_key = sys.argv[1]
    search_url = f"https://freeollama.oneplus1.top/?search={model_key}&page_size=50"

    print(f"Fetching {search_url}...")
    print(f"Looking for model: '{model_key}'")
    try:
        response = requests.get(search_url, timeout=30, verify=False)
        response.raise_for_status()
        print(f"✓ Page fetched successfully (status: {response.status_code})")
    except requests.RequestException as e:
        print(f"✗ Failed to fetch page: {e}")
        sys.exit(1)

    servers = extract_server_ips(response.text)

    print(f"\nFound {len(servers)} server(s), querying for model '{model_key}'...")
    print("=" * 80)

    results = []
    for i, server in enumerate(servers, 1):
        print(f"[{i}/{len(servers)}] {server}", end=' ')
        time.sleep(0.5)  # Rate limiting

        # First test reachability
        if not test_reachability(server):
            print("✗ Not reachable, skipping")
            continue

        models = query_server_models(server, model_key)

        if models:
            print(f"✓ Found {len(models)} model(s):")
            for model in models:
                results.append(f"{server}|{model}")
                print(f"    - {model}")
        else:
            print("✗ No matching models")

    # Save to file
    output_file = "found_servers.txt"
    with open(output_file, 'w') as f:
        for item in results:
            f.write(f"{item}\n")
    print(f"\n{'=' * 80}")
    print(f"✓ Results saved to {output_file}")
    print(f"Found {len(results)} reachable server-model pairs")

    # Print summary
    if results:
        print(f"\n{'=' * 80}")
        print("Server-Model Pairs (Server | Model):")
        print("=" * 80)
        for item in sorted(results):
            server, model = item.split('|')
            print(f"{server} -> {model}")


if __name__ == "__main__":
    main()