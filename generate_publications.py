#!/usr/bin/env python3
"""
Generate publications.html from BibTeX source files.
Run from the website root: python3 generate_publications.py
"""

import re
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
MY_NAME = 'Hudoba de Badyn'

BIB_SOURCES = [
    ('journal',    SCRIPT_DIR / 'cv' / '1-journal-papers.bib'),
    ('conference', SCRIPT_DIR / 'cv' / '2-conference-papers.bib'),
    ('nonpeer',    SCRIPT_DIR / 'cv' / '3-nonpeer-conf.bib'),
    ('thesis',     SCRIPT_DIR / 'cv' / '6-theses.bib'),
]

ENTRY_TYPE_TO_CAT = {
    'articlearxiv': 'journal',
    'article':      'journal',
    'inproceedings':'conference',
    'conf':         'nonpeer',
    'thesis':       'thesis',
    'phdthesis':    'thesis',
    'mastersthesis':'thesis',
}

SECTION_ORDER    = ['journal', 'conference', 'nonpeer', 'thesis']
SECTION_HEADINGS = {
    'journal':    'Journal Articles',
    'conference': 'Conference Papers',
    'nonpeer':    'Non-Peer-Reviewed Conference Papers',
    'thesis':     'Dissertation &amp; Theses',
}
BADGE_STYLE = {
    'journal':    ('#2563eb', 'Journal'),
    'conference': ('#059669', 'Conference'),
    'nonpeer':    ('#7c3aed', 'Non-peer conf.'),
    'thesis':     ('#b45309', 'Thesis'),
}

# ---------------------------------------------------------------------------
# BibTeX parser (no external dependencies; handles custom entry types)
# ---------------------------------------------------------------------------

def parse_bib_file(path):
    text = Path(path).read_text(encoding='utf-8')
    text = re.sub(r'%[^\n]*', '', text)          # strip % comments
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
        entry = _parse_body(text[brace + 1:i])
        entry['_type'] = entry_type
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
    return s.strip()

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


def build_links(entry, cat=None):
    links = []
    doi_url = _doi_url(entry.get('doi'))
    if doi_url:
        links.append(('Paper', doi_url, 'pub-link-paper'))
    eprint  = (entry.get('eprint')        or '').strip()
    archive = (entry.get('archiveprefix') or '').strip().lower()
    if eprint and archive == 'arxiv':
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
    if cat == 'journal':
        journal = re.sub(r'^in\s+', '', latex_to_html(entry.get('journal', '')), flags=re.I)
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
        f'<a class="pub-link {cls}" href="{url}" target="_blank" rel="noopener">{text}</a>'
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

PAGE_CSS = """
<style>
.pub-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: 1rem 0 2rem;
  padding: 0;
}
.pub-card {
  border-radius: 10px;
  border: 1px solid #ddd;
  padding: 1rem 1.25rem;
  background: #ffffff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.pub-title {
  margin: 0 0 0.3rem 0;
  font-size: 1rem;
  line-height: 1.45;
  font-weight: 600;
}
.pub-authors {
  margin: 0 0 0.2rem 0;
  font-size: 0.875rem;
  line-height: 1.4;
}
.pub-venue {
  margin: 0.1rem 0 0.55rem 0;
  font-size: 0.84rem;
  opacity: 0.72;
}
.pub-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.35rem;
}
.pub-link {
  display: inline-block;
  font-size: 0.77rem;
  font-weight: 700;
  padding: 0.18rem 0.6rem;
  border-radius: 4px;
  text-decoration: none;
  letter-spacing: 0.02em;
  transition: opacity 0.15s;
}
.pub-link:hover { opacity: 0.82; }
.pub-link-paper    { background: #dbeafe; color: #1e40af; }
.pub-link-preprint { background: #ffedd5; color: #9a3412; }
.pub-link-code     { background: #dcfce7; color: #14532d; }
</style>"""

PAGE_HEAD = """\
<!DOCTYPE html>
<html class="no-js"><head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<meta charset="utf-8">
    <title>Mathias Hudoba de Badyn | Publications | University of Oslo</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="format-detection" content="telephone=no">
    <meta name="keywords" content="hudoba de badyn, hudoba, badyn, de badyn, mathias, network, control, distributed, optimal transport, university of washington, eth, eth zurich, uio, university of oslo, its, department of technology systems">
    <link rel="stylesheet" href="index_files/mainv2.css">
    <link rel="stylesheet" href="index_files/all.css" integrity="sha384-5sAR7xN1Nv6T6+dT2mhtzEpVJvfS3NScPQTrOxhwjIuvcA67KV2R5Jz6kr4abQsz" crossorigin="anonymous">
    <link href="index_files/css.css" rel="stylesheet">
    <meta name="google-site-verification" content="_KH-p71nZffLu0IbnxfE_Vmqx0rOwxnGW8XJXsGJ83k">
"""

PAGE_NAV = """\
<body>
<div class="Container">
  <div class="Left">
    <h1 class="nav">Mathias Hudoba de Badyn</h1>
    <h3 class="nav">Associate Professor – UiO</h3>
    <br><hr><br>
    <h2 class="nav"><a href="http://mathiashdb.github.io/index.html">About</a></h2>
    <h2 class="nav"><a href="http://mathiashdb.github.io/publications.html">Publications</a></h2>
    <h2 class="nav"><a href="http://mathiashdb.github.io/teaching.html">Research Group</a></h2>
    <h2 class="nav"><a href="http://mathiashdb.github.io/contact.html">Contact</a></h2>
    <br><hr><hr>
  </div>
  <div class="Middle">
    <h1>Publications</h1>
    <div class="text">
      <p>Due to webscraping issues with my email address, Google Scholar and many other publication venues incorrectly parse my last name as &#8220;De Badyn&#8221; or &#8220;de Badyn&#8221;, instead of &#8220;Hudoba de Badyn&#8221;. If you are going to cite my papers, kindly make sure that the citation key is corrected. I have prepared a biblatex file with my name corrected <a href="publications_files/hudoba-de-badyn.bib">here</a> using the <a href="https://retorque.re/zotero-better-bibtex/">BetterBibtex</a> extension for <a href="https://www.zotero.org/">Zotero</a>, for your convenience.</p>
      <p>Most of my papers are available as preprints on the arXiv. A more-or-less complete list can be found <a href="https://arxiv.org/a/0000-0003-0955-2381.html">here</a>.</p>
    </div>
"""

PAGE_FOOT = """\
    <br><hr><hr>
  </div>
</div>
</body></html>
"""


def generate_html(sections_data):
    body = ''
    for cat in SECTION_ORDER:
        entries = sections_data.get(cat, [])
        if not entries:
            continue
        cards = '\n'.join(render_card(e, cat) for e in entries)
        body += f'    <h2>{SECTION_HEADINGS[cat]}</h2>\n    <div class="pub-list">\n{cards}\n    </div>\n\n'

    date = datetime.now().strftime('%Y-%m-%d')
    body += f'    <p style="font-size:0.75rem;opacity:0.45;margin-top:1.5rem">Generated {date}</p>\n'

    return PAGE_HEAD + PAGE_CSS + '\n</head>\n' + PAGE_NAV + body + PAGE_FOOT


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def safe_year(entry):
    try:
        return int(entry.get('year') or 0)
    except (ValueError, TypeError):
        return 0


def main():
    sections = {cat: [] for cat in SECTION_ORDER}

    for file_cat, path in BIB_SOURCES:
        for entry in parse_bib_file(path):
            cat = ENTRY_TYPE_TO_CAT.get(entry.get('_type', ''), file_cat)
            sections.setdefault(cat, []).append(entry)

    for cat in sections:
        sections[cat].sort(key=lambda e: -safe_year(e))

    html = generate_html(sections)
    out  = SCRIPT_DIR / 'publications.html'
    out.write_text(html, encoding='utf-8')
    print(f'Written: {out}')
    for cat in SECTION_ORDER:
        n = len(sections.get(cat, []))
        if n:
            print(f'  {SECTION_HEADINGS[cat]}: {n}')


if __name__ == '__main__':
    main()
