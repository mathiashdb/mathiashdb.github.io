#!/usr/bin/env bash
# Add one shared collaborator card, or add projects to an existing collaborator.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/scripts/add_collaborator.py"
