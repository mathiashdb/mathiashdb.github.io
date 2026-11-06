#!/usr/bin/env python3
"""Compatibility entry point for the shared publication generator."""
from pathlib import Path
import subprocess
import sys

if __name__ == '__main__':
    root = Path(__file__).resolve().parent.parent
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else root / 'cv' / 'web-publications.bib'
    sys.exit(subprocess.call([
        sys.executable, str(root / 'generate_publications.py'), '--bib-output', str(output)
    ]))
