#!/usr/bin/env bash

# Prepends a new project card to project-cards.html

PROJECT_CARDS="project-cards.html"

echo "=== Add a new project card ==="
echo

read -rp "Project name: " NAME
read -rp "Funding agency: " AGENCY
read -rp "Image filename (e.g. project_censss.jpg): " IMG_FILE
read -rp "Date range (e.g. 2023–2028): " DATES
read -rp "Project website (leave empty if none): " WEBSITE

# Project name — linked if a URL was given
if [[ -n "$WEBSITE" ]]; then
  NAME_HTML="<a href=\"$WEBSITE\">$NAME</a>"
else
  NAME_HTML="$NAME"
fi

# Back up before modifying
cp "$PROJECT_CARDS" "$PROJECT_CARDS.bak"
echo "Backup created: $PROJECT_CARDS.bak"

TEMP=$(mktemp)

cat > "$TEMP" <<EOF

<article class="project-card">
  <div class="project-img-wrap">
    <img
      src="img/$IMG_FILE"
      alt="$NAME"
      class="project-img"
    >
  </div>
  <div class="project-info">
    <h3 class="project-name">$NAME_HTML</h3>
    <p class="project-agency">$AGENCY</p>
    <p class="project-dates">$DATES</p>
  </div>
</article>

EOF

cat "$PROJECT_CARDS" >> "$TEMP"
mv "$TEMP" "$PROJECT_CARDS"

echo
echo "Done. New project card added to the top of $PROJECT_CARDS."
