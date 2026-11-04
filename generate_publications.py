#!/usr/bin/env python3
"""
Generate publications.html from BibTeX source files.
Run from the website root: python3 generate_publications.py
"""

import re
from pathlib import Path
import argparse
import sys
from html import escape

SCRIPT_DIR = Path(__file__).parent
MY_NAME = 'Hudoba de Badyn'

BIB_SOURCES = [
    ('preprint',   SCRIPT_DIR / 'cv' / '5-under-review.bib'),
    ('journal',    SCRIPT_DIR / 'cv' / '1-journal-papers.bib'),
    ('conference', SCRIPT_DIR / 'cv' / '2-conference-papers.bib'),
    ('nonpeer',    SCRIPT_DIR / 'cv' / '3-nonpeer-conf.bib'),
    ('thesis',     SCRIPT_DIR / 'cv' / '6-theses.bib'),
]

SECTION_ORDER    = ['preprint', 'journal', 'conference', 'nonpeer', 'thesis']
SECTION_HEADINGS = {
    'preprint':   'Preprints',
    'journal':    'Journal Articles',
    'conference': 'Conference Papers',
    'nonpeer':    'Non-Peer-Reviewed Conference Papers',
    'thesis':     'Dissertation &amp; Theses',
}
# ---------------------------------------------------------------------------
# BibTeX parser (no external dependencies; handles custom entry types)
# ---------------------------------------------------------------------------

def parse_bib_file(path):
    text = Path(path).read_text(encoding='utf-8')
    text = re.sub(r'(?<!\\)%[^\n]*', '', text)          # strip % comments
    entries, pos = [], 0
    while pos < len(text):
        at = text.find('@', pos)
        if at == -1:
            break
        brace = text.find('{', at)
        if brace == -1:
            break
        entry_type = text[at + 1:brace].strip().lower()
        if entry_type in ('comment', 'string', 'preamble'):
            pos = brace + 1
            continue
        # balanced-brace scan
        depth, i = 0, brace
        while i < len(text):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        if depth != 0:
            raise ValueError(f'{path}: unclosed entry at offset {at}')
        entry = _parse_body(text[brace + 1:i])
        entry['_type'] = entry_type
        entry['_source'] = str(path)
        entries.append(entry)
        pos = i + 1
    return entries


def _parse_body(body):
    result = {}
    body = body.strip()
    comma = body.find(',')
    if comma == -1:
        return result
    result['_key'] = body[:comma].strip()
    rest = body[comma + 1:]
    n, i = len(rest), 0
    while i < n:
        while i < n and rest[i] in ' \t\n\r,':
            i += 1
        if i >= n or rest[i] == '}':
            break
        eq = rest.find('=', i)
        if eq == -1:
            break
        field = rest[i:eq].strip().lower()
        i = eq + 1
        while i < n and rest[i] in ' \t\n\r':
            i += 1
        if i >= n:
            break
        if rest[i] == '{':
            depth, start = 0, i
            while i < n:
                if rest[i] == '{':
                    depth += 1
                elif rest[i] == '}':
                    depth -= 1
                    if depth == 0:
                        break
                i += 1
            value = rest[start + 1:i]
            i += 1
        elif rest[i] == '"':
            i += 1
            start = i
            while i < n and rest[i] != '"':
                i += 1
            value = rest[start:i]
            i += 1
        else:
            start = i
            while i < n and rest[i] not in ',}\n':
                i += 1
            value = rest[start:i].strip()
        if field:
            result[field] = value
    return result

# ---------------------------------------------------------------------------
# LaTeX → HTML
# ---------------------------------------------------------------------------

_ACUTE   = dict(zip('aeiouyAEIOUY', 'áéíóúýÁÉÍÓÚÝ'))
_GRAVE   = dict(zip('aeiouAEIOU',   'àèìòùÀÈÌÒÙ'))
_UMLAUT  = dict(zip('aeiouAEIOU',   'äëïöüÄËÏÖÜ'))
_CEDILLA = {'c': 'ç', 'C': 'Ç'}


def _apply_accents(s):
    for d, pfx in [(_ACUTE, "\\'"), (_GRAVE, '\\`'), (_UMLAUT, '\\"'), (_CEDILLA, '\\c')]:
        for c, r in d.items():
            s = s.replace(f'{pfx}{{{c}}}', r)
            s = s.replace(f'{pfx}{c}',     r)
    return s


def latex_to_html(s):
    if not s:
        return ''
    s = re.sub(r'\s+', ' ', s).strip()
    # Math: \mathcal{H} subscript variants
    s = re.sub(r'\$\{?\\mathcal\{H\}\}?_?\\infty\$',    'ℋ<sub>∞</sub>', s)
    s = re.sub(r'\$\{?\\mathcal\{H\}\}?_?2\$',           'ℋ<sub>2</sub>',  s)
    s = re.sub(r'\$\{\\mathcal\{H\}_2\}\$',               'ℋ<sub>2</sub>',  s)
    s = re.sub(r'\$\{\\mathcal\{H\}_\{\\infty\}\}\$',     'ℋ<sub>∞</sub>', s)
    s = re.sub(r'\$([^$]+)\$',                             r'\1',            s)
    s = _apply_accents(s)
    s = s.replace(r'{\&}', '&amp;').replace(r'\&', '&amp;')
    s = s.replace(r'{\%}', '%').replace(r'\%', '%')
    s = s.replace('~', ' ')          # LaTeX non-breaking space → plain space
    # Strip case-preservation braces iteratively
    for _ in range(6):
        prev = s
        s = re.sub(r'\{([^{}]*)\}', r'\1', s)
        if s == prev:
            break
    s = re.sub(r'\\[a-zA-Z]+\s*', '', s)   # any remaining control sequences
    return escape(s.strip(), quote=True).replace('&amp;amp;', '&amp;').replace('&lt;sub&gt;', '<sub>').replace('&lt;/sub&gt;', '</sub>')

# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def format_authors(author_str):
    if not author_str:
        return ''
    parts = re.split(r'\s+and\s+', author_str)
    result = []
    for raw in parts:
        raw = raw.strip()
        name = latex_to_html(raw)
        if ',' in name:
            last, _, first = name.partition(',')
            inits = ' '.join(p[0] for p in first.strip().split() if p)
            display = f'{inits} {last.strip()}' if inits else last.strip()
        else:
            words = name.split()
            if len(words) >= 2:
                inits = ' '.join(p[0] for p in words[:-1] if p)
                display = f'{inits} {words[-1]}' if inits else name
            else:
                display = name
        if MY_NAME in raw or MY_NAME in display:
            display = f'<strong>{display}</strong>'
        result.append(display)
    return ', '.join(result)


def _doi_url(doi):
    doi = (doi or '').strip()
    if not doi:
        return None
    return doi if doi.startswith('http') else f'https://doi.org/{doi}'


def has_arxiv_preprint(entry):
    return (
        (entry.get('archiveprefix') or '').strip().lower() == 'arxiv'
        and bool((entry.get('eprint') or '').strip())
    )


def build_links(entry, cat=None):
    links = []
    doi_url = _doi_url(entry.get('doi'))
    if doi_url:
        links.append(('Paper', doi_url, 'pub-link-paper'))
    eprint  = (entry.get('eprint')        or '').strip()
    if has_arxiv_preprint(entry):
        links.append(('Preprint', f'https://arxiv.org/abs/{eprint}', 'pub-link-preprint'))
    code = (entry.get('code') or '').strip()
    if code:
        links.append(('Code', code, 'pub-link-code'))
    url = (entry.get('url') or '').strip()
    if url and not doi_url:
        label = 'Thesis' if cat == 'thesis' else 'Link'
        links.append((label, url, 'pub-link-paper'))
    return links


def venue_str(entry, cat):
    if cat == 'preprint':
        # Do not expose the confidential submission venue on the website.
        return f"arXiv preprint, {safe_year(entry)}" if safe_year(entry) else 'arXiv preprint'

    if cat == 'journal':
        journal = re.sub(r'^in\s+(?!press\b)', '', latex_to_html(entry.get('journal', '')), flags=re.I)
        vol, num = entry.get('volume', ''), entry.get('number', '')
        pages = (entry.get('pages') or '').replace('--', '–')
        year  = entry.get('year', '')
        parts = []
        if journal:
            parts.append(f'<em>{journal}</em>')
        if vol and num:
            parts.append(f'vol.&nbsp;{vol}({num})')
        elif vol:
            parts.append(f'vol.&nbsp;{vol}')
        if pages:
            parts.append(f'pp.&nbsp;{pages}')
        if year:
            parts.append(str(year))
        return ', '.join(parts)

    if cat in ('conference', 'nonpeer'):
        bt = latex_to_html(entry.get('booktitle', ''))
        bt = re.sub(r'^To appear in (the\s+)?', '', bt, flags=re.I).strip()
        pages = (entry.get('pages') or '').replace('--', '–')
        vol   = entry.get('volume', '')
        parts = []
        if bt:
            parts.append(f'<em>{bt}</em>')
        if vol:
            parts.append(f'vol.&nbsp;{vol}')
        if pages:
            parts.append(f'pp.&nbsp;{pages}')
        return ', '.join(parts)

    if cat == 'thesis':
        ttype  = latex_to_html(entry.get('type', 'Thesis'))
        school = latex_to_html(entry.get('school', ''))
        year   = entry.get('year', '')
        parts  = [f'<em>{ttype}</em>']
        if school:
            parts.append(school)
        if year:
            parts.append(str(year))
        return ', '.join(parts)

    return ''

# ---------------------------------------------------------------------------
# Card rendering
# ---------------------------------------------------------------------------

def render_card(entry, cat):
    title   = latex_to_html(entry.get('title',  ''))
    authors = format_authors(entry.get('author', ''))
    year    = str(entry.get('year', ''))
    venue   = venue_str(entry, cat)
    links   = build_links(entry, cat)

    links_html = ' '.join(
        f'<a class="pub-link {cls}" href="{escape(url, quote=True)}" target="_blank" rel="noopener">{text}</a>'
        for text, url, cls in links
    )
    venue_p  = f'\n      <p class="pub-venue">{venue}</p>'   if venue      else ''
    links_div = f'\n      <div class="pub-links">{links_html}</div>' if links_html else ''

    return (
        '    <article class="pub-card">\n'
        f'      <h3 class="pub-title">{title}</h3>\n'
        f'      <p class="pub-authors">{authors}</p>'
        f'{venue_p}{links_div}\n'
        '    </article>'
    )

# ---------------------------------------------------------------------------
# Page assembly
# ---------------------------------------------------------------------------



def generate_html(sections_data):
    body = ''
    for cat in SECTION_ORDER:
        entries = sections_data.get(cat, [])
        if not entries:
            continue
        cards = '\n'.join(render_card(e, cat) for e in entries)
        body += f'    <h2>{SECTION_HEADINGS[cat]}</h2>\n    <div class="pub-list">\n{cards}\n    </div>\n\n'

    template = (SCRIPT_DIR / 'templates' / 'publications.html').read_text(encoding='utf-8')
    return template.replace('{{PUBLICATION_SECTIONS}}', body)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def safe_year(entry):
    try:
        return int(entry.get('year') or 0)
    except (ValueError, TypeError):
        return 0


def load_sections():
    sections = {cat: [] for cat in SECTION_ORDER}
    seen = {}
    errors = []
    for file_cat, path in BIB_SOURCES:
        for entry in parse_bib_file(path):
            key = entry.get('_key', '')
            context = f"{path.name}: {key or '(missing key)'}"
            if not key:
                errors.append(f'{context}: missing citation key')
            elif key in seen:
                errors.append(f'{context}: duplicate citation key (also in {seen[key]})')
            seen[key] = path.name
            for field in ('title', 'author'):
                if not entry.get(field, '').strip():
                    errors.append(f'{context}: missing {field}')
            if not safe_year(entry):
                errors.append(f'{context}: missing or invalid year')
            archive = entry.get('archiveprefix', '').strip().lower()
            eprint = entry.get('eprint', '').strip()
            if archive == 'arxiv' and not eprint:
                errors.append(f'{context}: arXiv archivePrefix requires an eprint ID')
            if eprint and not archive:
                errors.append(f'{context}: eprint requires archivePrefix')
            if archive == 'arxiv' and eprint and not re.fullmatch(
                r'(?:\d{4}\.\d{4,5}|[a-zA-Z.-]+(?:[.-][A-Z]{2})?/\d{7})(?:v\d+)?', eprint
            ):
                errors.append(f'{context}: invalid arXiv ID {eprint!r}')
            if file_cat == 'preprint':
                if not has_arxiv_preprint(entry):
                    continue
                cat = 'preprint'
            else:
                cat = file_cat
            sections[cat].append(entry)
    if errors:
        raise ValueError('Publication validation failed:\n  ' + '\n  '.join(errors))
    for entries in sections.values():
        entries.sort(key=lambda e: (-safe_year(e), e.get('_key', '').casefold()))
    return sections


def generate_bib(sections):
    # Standard BibLaTeX entry types, retaining LaTeX spelling and full names.
    types = {'preprint': 'misc', 'journal': 'article',
             'conference': 'inproceedings', 'nonpeer': 'inproceedings', 'thesis': 'thesis'}
    chunks = ['% Generated from CV BibTeX sources by generate_publications.py. Do not edit.\n']
    for cat in SECTION_ORDER:
        for entry in sections[cat]:
            fields = {k: re.sub(r'\s+', ' ', v).strip()
                      for k, v in entry.items() if not k.startswith('_')}
            if cat == 'preprint':
                fields.pop('journal', None)
                fields.pop('booktitle', None)
                fields['pubstate'] = 'prepublished'
            fields.pop('keywords', None)
            body = ',\n'.join(f'  {k} = {{{v}}}' for k, v in sorted(fields.items()))
            chunks.append(f"@{types[cat]}{{{entry['_key']},\n{body}\n}}\n")
    return '\n'.join(chunks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check validation and generated files without writing')
    parser.add_argument('--bib-output', type=Path, help='Also write the bibliography to this legacy/custom path')
    args = parser.parse_args()
    try:
        sections = load_sections()
        outputs = {
            SCRIPT_DIR / 'publications.html': generate_html(sections),
            SCRIPT_DIR / 'publications_files' / 'hudoba-de-badyn.bib': generate_bib(sections),
        }
        if args.bib_output:
            outputs[args.bib_output.resolve()] = generate_bib(sections)
        stale = []
        for path, content in outputs.items():
            if not path.exists() or path.read_text(encoding='utf-8') != content:
                stale.append(path)
        if args.check:
            if stale:
                raise ValueError('Generated files need updating:\n  ' + '\n  '.join(map(str, stale)))
            print('Publication sources and generated files are up to date.')
        else:
            for path in stale:
                path.write_text(outputs[path], encoding='utf-8')
                print(f'Written: {path}')
        for cat in SECTION_ORDER:
            print(f'  {SECTION_HEADINGS[cat]}: {len(sections[cat])}')
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
