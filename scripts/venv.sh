#!/usr/bin/env bash
set -e
if [ ! -d ".venv" ]; then python3 -m venv .venv; fi
source .venv/bin/activate
if [ "$1" = "--install" ]; then pip install -r requirements.txt; fi
