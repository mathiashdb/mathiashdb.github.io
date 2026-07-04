#!/usr/bin/env bash

PHDCARDS="phd-cards.html"
ALUMNICARDS="alumni-cards.html"

echo "=== Move a PhD to Alumni ==="
read -rp "Enter the exact PhD name to move: " NAME

if [[ -z "$NAME" ]]; then
  echo "No name given. Aborting."
  exit 1
fi

echo "Now enter dissertation info for $NAME."
read -rp "PhD dissertation title: " DISS_TITLE
read -rp "PhD dissertation website (leave empty if none): " DISS_URL
read -rp "Graduation year (e.g. 2029): " GRAD_YEAR

if [[ -z "$GRAD_YEAR" ]]; then
  echo "No graduation year given. Aborting."
  exit 1
fi

# Backup phd-cards.html
cp "$PHDCARDS" "$PHDCARDS.bak"
echo "Backup created: $PHDCARDS.bak"

# Temporary files
TEMP_FOUND=$(mktemp)
TEMP_REMAINING=$(mktemp)

awk -v name="$NAME" -v title="$DISS_TITLE" -v url="$DISS_URL" -v grad="$GRAD_YEAR" '
  BEGIN { RS="</article>"; FS="\n" }

  # >>> IMPORTANT FIX: skip records that are only whitespace <<<
  /^[[:space:]]*$/ { next }

  {
    is_target = ($0 ~ "<h3 class=\"phd-name\">" name "</h3>")
    out = is_target ? "'"$TEMP_FOUND"'" : "'"$TEMP_REMAINING"'"
    in_meta = 0

    for (i = 1; i <= NF; i++) {
      line = $i

      # Replace topic block with dissertation title / link
      if (is_target && line ~ /<p class="phd-topic">/) {
        print "      <p class=\"phd-topic\">" > out
        if (title != "") {
          if (url != "") {
            printf "        <a href=\"%s\">%s</a>\n", url, title > out
          } else {
            printf "        %s\n", title > out
          }
        }
        print "      </p>" > out

        # Skip original topic lines until </p>
        while (i <= NF && $i !~ /<\/p>/) {
          i++
        }
        # Skip the line containing </p> itself
        continue
      }

      # Detect start of meta block
      if (is_target && line ~ /<p class="phd-meta">/) {
        in_meta = 1
        print line > out
        continue
      }

      # Inside meta: swap Start: YYYY -> Graduation: GRAD_YEAR
      if (is_target && in_meta) {
        gsub(/Start:[^·<]*/, "Graduation: " grad, line)
        print line > out
        if (line ~ /<\/p>/) {
          in_meta = 0
        }
        continue
      }

      # Default: copy line as-is
      print line > out
    }

    # Re-add closing </article> and a blank line for all real records
    print "</article>" > out
    print "" > out
  }
' "$PHDCARDS"

if [[ ! -s "$TEMP_FOUND" ]]; then
  echo "No PhD card found with name: $NAME"
  rm "$TEMP_FOUND" "$TEMP_REMAINING"
  exit 1
fi

echo
echo "=== Found card(s) for \"$NAME\" (after updating topic + meta) ==="
cat "$TEMP_FOUND"
echo "================================================================"
echo

echo "Moving updated card to $ALUMNICARDS..."

echo "" >> "$ALUMNICARDS"
cat "$TEMP_FOUND" >> "$ALUMNICARDS"
echo "" >> "$ALUMNICARDS"

cp "$TEMP_REMAINING" "$PHDCARDS"

rm "$TEMP_FOUND" "$TEMP_REMAINING"

echo "Done. $NAME has been moved to alumni with dissertation info and graduation year."
