# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This is a tool for discovering and querying Ollama servers that host specific AI models. It scrapes a public server list and queries each server's API to check for deployed models.

## Dependencies

This project requires a Python virtual environment. The virtual environment is located in the `venv312/` directory and uses Python 3.12.

All dependencies are managed via pip in the virtual environment. Required packages include `requests`, `beautifulsoup4`, and `ollama`.

## Usage

- `extract_servers.py` - Scrape server IP addresses from freeollama.oneplus1.top
- `extract_servers_with_models.py` - Scrape server IPs and query each for available models (filters for glm-4.7)
- `debug_models.py` - Simple test to check connectivity to a specific server
- `ollama_gui.py` - Python GUI application for chatting with Ollama models

All scripts use SSL verification disabled due to expired certificates on the target site.

## Common Tasks

- **Activate Python environment** - Always activate the virtual environment before running any Python scripts:
  ```bash
  source venv312/bin/activate
  ```
  (or `source venv312/Scripts/activate` on Windows)

- **Run scripts** - After activating the virtual environment:
  ```bash
  python extract_servers.py
  python extract_servers_with_models.py
  python debug_models.py
  python ollama_gui.py
  ```

- **Install dependencies** - After activating the virtual environment:
  ```bash
  pip install -r requirements.txt
  pip install -r requirements_gui.txt
  ```