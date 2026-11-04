#!/usr/bin/env bash
# Add a PhD card and matching entry in cv/11-phd.bib (unless the student already exists).
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/scripts/add_student.py" phd
