#!/usr/bin/env python3
from pathlib import Path

# Adjust these paths to where your CV bib files live (relative to this script)
SOURCE_BIBS = [
    Path("1-journal-papers.bib"),
    Path("2-conference-papers.bib"),
    Path("3-nonpeer-conf.bib"),
    Path("6-theses.bib"),
]

OUT_BIB = Path("web-publications.bib")

# Text-level replacements for non-standard entry types
ENTRYTYPE_REPLACEMENTS = {
    "@articlearxiv{": "@article{",
    "@conf{": "@inproceedings{",
    "@thesis{": "@phdthesis{",   # adjust if needed
}

def main():
    chunks = []

    for src in SOURCE_BIBS:
        text = src.read_text(encoding="utf-8")

        # Apply simple replacements
        for old, new in ENTRYTYPE_REPLACEMENTS.items():
            text = text.replace(old, new)

        # Optional: add a comment so you know which file it came from
        header = f"% ----- From {src.name} -----\n"
        chunks.append(header + text.strip() + "\n")

    merged = "\n\n".join(chunks) + "\n"

    OUT_BIB.write_text(merged, encoding="utf-8")
    print(f"Wrote merged/normalized bib to {OUT_BIB}")

if __name__ == "__main__":
    main()
