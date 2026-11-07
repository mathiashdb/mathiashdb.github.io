#!/usr/bin/env bash
# Compatibility entry point; the website generator owns bibliography conversion.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/../generate_publications.py" --bib-output "${1:-pubs.bib}"
