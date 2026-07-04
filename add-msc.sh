#!/usr/bin/env bash

MSCCARDS="current-msc.html"

echo "=== Add a new Master student card ==="

read -rp "Student name: " NAME
read -rp "Project / thesis title: " TITLE
read -rp "Project website (leave empty if none): " PROJ_URL

read -rp "Type (e.g. Master's Thesis, Semester Project): " TYPE
read -rp "Period (e.g. 2024–2025): " PERIOD

read -rp "Co-supervisor name (leave empty if none): " COSUP_NAME
read -rp "Co-supervisor website (leave empty if none): " COSUP_URL

# Build title line, optionally linked
if [[ -n "$TITLE" && -n "$PROJ_URL" ]]; then
  TITLE_HTML="<a href=\"$PROJ_URL\">$TITLE</a>"
else
  TITLE_HTML="$TITLE"
fi

# Build co-supervisor text (with or without link)
COSUP_TEXT=""
if [[ -n "$COSUP_NAME" && -n "$COSUP_URL" ]]; then
  COSUP_TEXT=" · Co-supervised with <a href=\"$COSUP_URL\">$COSUP_NAME</a>"
elif [[ -n "$COSUP_NAME" ]]; then
  COSUP_TEXT=" · Co-supervised with $COSUP_NAME"
fi

# Make a backup before modifying
cp "$MSCCARDS" "$MSCCARDS.bak"
echo "Backup created: $MSCCARDS.bak"

# Create a temp file for new content
TEMP_NEW=$(mktemp)

# Write the new card FIRST (prepend)
cat > "$TEMP_NEW" <<EOF

<article class="master-card">
  <h3 class="master-name">$NAME</h3>
  <p class="master-topic">
    $TITLE_HTML
  </p>
  <p class="master-meta">
    $TYPE · $PERIOD$COSUP_TEXT
  </p>
</article>

EOF

# Append the old file after the new card
cat "$MSCCARDS" >> "$TEMP_NEW"

# Replace original file
mv "$TEMP_NEW" "$MSCCARDS"

echo "Done. New card added to the TOP of $MSCCARDS."
