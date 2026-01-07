#!/usr/bin/env bash
set -euo pipefail

OUT="${1:-pubs.bib}"

FILES=(
  "1-journal-papers.bib"
  "2-conference-papers.bib"
  "3-nonpeer-conf.bib"
)

for f in "${FILES[@]}"; do
  [[ -f "$f" ]] || { echo "Missing file: $f" >&2; exit 1; }
done

awk '
BEGIN {
  print "% Auto-generated: merged + normalized entry types"
  print "% 1-journal-papers.bib -> @article"
  print "% 2-*.bib and 3-*.bib  -> @inproceedings"
  print ""
}

function desired_type(fn) {
  return (fn ~ /(^|\/)1-journal-papers\.bib$/) ? "article" : "inproceedings"
}

{
  sub(/\r$/, "")   # strip CR if Windows line endings
  want = desired_type(FILENAME)

  # Match BibTeX entry headers
  if ($0 ~ /^[ \t]*@/) {
    if (match($0, /^[ \t]*@([A-Za-z][A-Za-z0-9_-]*)[ \t]*[\{\(]/, m)) {
      t = tolower(m[1])
      if (t != "string" && t != "preamble" && t != "comment") {
        # Replace "@<anything>" up to the brace/paren
        sub(/^[ \t]*@[A-Za-z][A-Za-z0-9_-]*/, "@" want)
      }
    }
  }

  print
}

ENDFILE { print "" }
' "${FILES[@]}" > "$OUT"

echo "Wrote: $OUT"
