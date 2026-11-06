#!/usr/bin/env bash
# Add a current master student card and matching CV supervision entry.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/scripts/add_student.py" msc
