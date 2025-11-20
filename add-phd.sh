#!/usr/bin/env bash

# Simple script to append a new PhD card to phd-cards.html

PHDCARDS_FILE="phd-cards.html"

echo "=== Add a new PhD card ==="

read -rp "PhD name: " NAME
read -rp "Start year (e.g. 2025): " START_YEAR
read -rp "Profile photo filename (e.g. phd_johan.jpg): " PHOTO_FILE

read -rp "Project name: " PROJECT_NAME
read -rp "Project website (leave empty if none): " PROJECT_URL

read -rp "Co-supervisor name: " COSUP_NAME
read -rp "Co-supervisor website (leave empty if none): " COSUP_URL

# Optional: one-line topic/description (you can remove this if you prefer to edit manually)
read -rp "One-line PhD topic (for the card body): " TOPIC_LINE

# Build project text (with or without link)
if [[ -n "$PROJECT_NAME" && -n "$PROJECT_URL" ]]; then
  PROJECT_TEXT="<a href=\"$PROJECT_URL\">$PROJECT_NAME</a>"
else
  PROJECT_TEXT="$PROJECT_NAME"
fi

# Build co-supervisor text (with or without link)
if [[ -n "$COSUP_NAME" && -n "$COSUP_URL" ]]; then
  COSUP_TEXT="<a href=\"$COSUP_URL\">$COSUP_NAME</a>"
else
  COSUP_TEXT="$COSUP_NAME"
fi

# Build meta line (you can adjust punctuation / bullets as you like)
META_LINE="Start: $START_YEAR"
if [[ -n "$PROJECT_TEXT" ]]; then
  META_LINE+=" · Project: $PROJECT_TEXT"
fi
if [[ -n "$COSUP_TEXT" ]]; then
  META_LINE+=" · Co-supervised with $COSUP_TEXT"
fi

echo
echo "Appending new card to $PHDCARDS_FILE..."
echo

cat >> "$PHDCARDS_FILE" <<EOF

<article class="phd-card">
  <div class="phd-main">
    <div class="phd-media">
      <img
        src="img/$PHOTO_FILE"
        alt="Portrait of $NAME"
        class="phd-photo"
      >
    </div>
    <div class="phd-content">
      <h3 class="phd-name">$NAME</h3>
      <p class="phd-topic">
        $TOPIC_LINE
      </p>
    </div>
  </div>
  <p class="phd-meta">
    $META_LINE
  </p>
</article>
EOF

echo "Done. Check $PHDCARDS_FILE for the newly added card."
