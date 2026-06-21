#!/usr/bin/env python3
"""
Debug script to see what models are available on each server.
"""

import requests
import warnings
import json

warnings.filterwarnings('ignore')

server = '82.156.240.252:11434'
try:
    resp = requests.get(f'http://{server}/api/tags', timeout=10, verify=False)
    print(f'Server {server} status: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        models = data.get('models', [])
        print(f'\nTotal models: {len(models)}')
        print('\nAll available models:')
        for i, model in enumerate(models[:10], 1):  # Show first 10
            name = model.get('name', 'N/A')
            size = model.get('size', 0)
            print(f'{i}. {name} ({size:,} bytes)')
        if len(models) > 10:
            print(f'\n... and {len(models) - 10} more models')
except Exception as e:
    print(f'Error: {e}')