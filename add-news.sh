#!/usr/bin/env bash
# Prompt for a news item and prepend it to news-cards.html.
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Add a news card ==="
read -rp "Date (e.g. Nov 4, 2026): " NEWS_DATE
read -rp "News blurb: " NEWS_BLURB
read -rp "Link URL (leave blank for no link): " NEWS_URL
NEWS_LABEL=""
if [[ -n "$NEWS_URL" ]]; then
  read -rp "Link text (e.g. Read more): " NEWS_LABEL
fi

python3 - "$SCRIPT_DIR/news-cards.html" "$NEWS_DATE" "$NEWS_BLURB" "$NEWS_URL" "$NEWS_LABEL" <<'PY'
from html import escape
from pathlib import Path
import shutil
import sys

path = Path(sys.argv[1])
date, blurb, url, label = (value.strip() for value in sys.argv[2:])
if not date or not blurb:
    sys.exit('Date and news blurb are required. No changes made.')
if url and not label:
    sys.exit('Link text is required when a URL is supplied. No changes made.')

body = escape(blurb)
if url:
    body += f' <a href="{escape(url, quote=True)}">{escape(label)}</a>'
card = (
    '  <article class="news-card">\n'
    f'    <span class="news-date">{escape(date)}</span>\n'
    '    <p class="news-body">\n'
    f'      {body}\n'
    '    </p>\n'
    '  </article>\n\n'
)
existing = path.read_text(encoding='utf-8')
backup = path.with_suffix(path.suffix + '.bak')
shutil.copy2(path, backup)
path.write_text(card + existing, encoding='utf-8')
print(f'Added news to the top of {path.name}. Backup: {backup.name}')
PY
