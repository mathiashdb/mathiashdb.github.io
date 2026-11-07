# Updating publications

For tag naming and BibTeX examples, see the [project tagging guide](README.md#create-a-project-tag).

The CV files are the source of truth. Do not edit `publications.html` or
`publications_files/hudoba-de-badyn.bib` directly.

- `cv/1-journal-papers.bib`: journal articles, including accepted/in-press papers.
- `cv/2-conference-papers.bib`: peer-reviewed conference papers.
- `cv/3-nonpeer-conf.bib`: other conference papers.
- `cv/5-under-review.bib`: submissions; only records with `archivePrefix = {arXiv}`
  and a valid `eprint` identifier appear publicly, in Preprints.
- `cv/6-theses.bib`: theses.

In-preparation papers, private submissions, talks, and supervision records are
excluded from the public outputs. Submission venues are omitted for preprints.
The downloadable bibliography uses standard BibLaTeX types, preserves full author
names and LaTeX text, and contains the same records as the page.

After acceptance, move the record from the under-review file to its journal or
conference file, change its entry type to the appropriate CV type, and update
its venue, year, and DOI. Keep its citation key and arXiv fields. Remove the old
record so the paper appears once. Citation keys must be unique across these files.

Run from the website root:

```bash
python3 generate_publications.py
python3 generate_publications.py --check
python3 -m unittest discover -s tests
```

The first command updates both public outputs. The second validates sources and
fails if either output is stale; it is suitable for a future publishing/CI check.
The generator uses Python's standard library and can be invoked from any directory.
It sorts newest year first, then by citation key, and avoids timestamps so unchanged
sources produce unchanged outputs.

<<<<<<< HEAD
`./cv/compile.sh` first checks that student project tags agree between supervision
bibliographies and personnel cards. It also validates publication sources, builds
the CV, then regenerates both
`./cv/compile.sh` also validates the sources, builds the CV, then regenerates both
public outputs after a successful build. It works from any directory. Review and
commit the source and generated changes together, then publish as usual. Compiling
does not push or publish the site.

Edit `templates/publications.html` for page layout, navigation, and CSS. Keep the
`{{PUBLICATION_SECTIONS}}` placeholder for generated cards.

The old `cv/bib-convert.sh [output.bib]` and `cv/merge_bib_for_web.py [output.bib]`
now delegate to the same generator, updating the public outputs and an additional
bibliography copy. Historical `cv/website-pubs.bib` and `cv/web-publications.bib`
are not inputs; use the public downloadable bibliography as the canonical export.

Validation reports missing titles/authors, missing or invalid years, duplicate
keys, incomplete arXiv metadata, malformed arXiv identifiers, and unclosed entries.
The parser supports the brace-delimited records and literal fields used in this
CV; BibTeX string macros and concatenated fields are not supported.
