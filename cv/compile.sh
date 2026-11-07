#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

python3 -c 'import sys; sys.path.insert(0, ".."); from generate_publications import load_sections; load_sections()'
python3 generate_grants_table.py

rm -f -- cv-hudoba-de-badyn.bbl cv-hudoba-de-badyn.aux
xelatex -interaction=nonstopmode -halt-on-error cv-hudoba-de-badyn.tex
xelatex -interaction=nonstopmode -halt-on-error cv-hudoba-de-badyn.tex
biber cv-hudoba-de-badyn
xelatex -interaction=nonstopmode -halt-on-error cv-hudoba-de-badyn.tex
xelatex -interaction=nonstopmode -halt-on-error cv-hudoba-de-badyn.tex

python3 "$SCRIPT_DIR/../generate_publications.py"

python3 "$SCRIPT_DIR/../generate_project_pages.py"
