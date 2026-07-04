#!/usr/bin/env bash

CURRENT_MSC="current-msc.html"
PAST_MSC="past-msc.html"

echo "=== Move a Master card to Past Projects ==="
read -rp "Enter the exact Master student name to move: " NAME

if [[ -z "$NAME" ]]; then
  echo "No name given. Aborting."
  exit 1
fi

# Backup current file
cp "$CURRENT_MSC" "$CURRENT_MSC.bak"
echo "Backup created: $CURRENT_MSC.bak"

# Temporary files
TEMP_FOUND=$(mktemp)
TEMP_REMAINING=$(mktemp)

# Extract matching cards.
awk -v name="$NAME" '
  BEGIN { RS="</article>"; FS="\n" }

  # Skip pure whitespace records (fixes trailing empty article issue)
  /^[[:space:]]*$/ { next }

  {
    is_target = ($0 ~ "<h3 class=\"master-name\">" name "</h3>")
    out = is_target ? "'"$TEMP_FOUND"'" : "'"$TEMP_REMAINING"'"

    print $0 "</article>" > out
    print "" > out
  }
' "$CURRENT_MSC"

# Check if we found any cards
if [[ ! -s "$TEMP_FOUND" ]]; then
  echo "No Master card found with name: $NAME"
  rm "$TEMP_FOUND" "$TEMP_REMAINING"
  exit 1
fi

echo
echo "=== Found card(s) for \"$NAME\" ==="
cat "$TEMP_FOUND"
echo "==================================="
echo

# PREPEND to past-msc.html
TEMP_NEW=$(mktemp)

# Write found cards FIRST
cat "$TEMP_FOUND" > "$TEMP_NEW"

# Then append existing past-msc.html
if [[ -f "$PAST_MSC" ]]; then
  echo "" >> "$TEMP_NEW"
  cat "$PAST_MSC" >> "$TEMP_NEW"
fi

# Replace past-msc.html with the new file
mv "$TEMP_NEW" "$PAST_MSC"

# Replace current-msc.html with remaining cards
cp "$TEMP_REMAINING" "$CURRENT_MSC"

# Cleanup temp files
rm "$TEMP_FOUND" "$TEMP_REMAINING"

echo "Done. $NAME has been moved to the TOP of $PAST_MSC."
