#!/usr/bin/env python3
"""Build static project pages from JSON, tagged personnel cards, and CV papers."""
import argparse
from html import escape, unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from string import Template
import sys

from generate_publications import load_sections, render_card, SECTION_ORDER, SECTION_HEADINGS

ROOT = Path(__file__).resolve().parent
PERSONNEL_SOURCES = (
    ('collab-cards.html', 'Research lead'),
    ('phd-cards.html', 'PhD researcher'),
    ('current-msc.html', 'Current student'),
    ('past-msc.html', 'Past student'),
)


class OpeningTag(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.attrs = {}
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag == 'article':
            self.attrs = dict(attrs)


def personnel_for(tag, root=ROOT):
    cards = []
    seen = set()
    for filename, role in PERSONNEL_SOURCES:
        source = (root / filename).read_text(encoding='utf-8')
        source = re.sub(r'<!--.*?-->', '', source, flags=re.S)
        for match in re.finditer(r'<article\b[^>]*>.*?</article\s*>', source, re.S | re.I):
            card = match.group()
            opening = re.match(r'<article\b[^>]*>', card, re.I).group()
            attrs = OpeningTag(opening).attrs
            if tag not in (attrs.get('data-projects') or '').casefold().split():
                continue
            name_match = re.search(r'<h3\b[^>]*>(.*?)</h3>', card, re.S)
            if not name_match:
                raise ValueError(f'{filename}: tagged card has no person heading')
            name = re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', '', name_match[1]))).strip().casefold()
            if name in seen:
                continue  # Prefer collaborator, then PhD, current, past if a person occurs twice.
            seen.add(name)
            content = card[len(opening):re.search(r'</article\s*>\s*$', card, re.I).start()]
            cards.append(f'<article class="person-card"><p class="person-role">{role}</p>{content}</article>')
    return cards


def keyword_tags(entry):
    # BibLaTeX keywords are comma-separated; tags are matched as whole keywords.
    return {part.strip().casefold() for part in entry.get('keywords', '').split(',') if part.strip()}


def visual_source(value):
    """Allow site-relative assets or HTTP(S) media URLs."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError('visual.src must be a nonempty image, video, or embed URL')
    value = value.strip()
    from urllib.parse import urlsplit
    parsed = urlsplit(value)
    if parsed.scheme and parsed.scheme.lower() not in ('http', 'https'):
        raise ValueError('visual.src must use a relative path or an HTTP(S) URL')
    return escape(value, quote=True)


def network_svg(visual, slug):
    import math
    import random

    layout = visual.get('layout', 'network')
    if layout not in ('network', 'ring', 'star', 'grid', 'classic'):
        raise ValueError('visual.layout must be network, ring, star, grid, or classic')
    count = visual.get('nodes', 8)
    if type(count) is not int or not 4 <= count <= 24:
        raise ValueError('visual.nodes must be an integer between 4 and 24')
    rng = random.Random(str(visual.get('seed', slug)))
    if layout == 'classic':
        points = [(60, 160), (135, 65), (230, 100), (160, 210), (320, 205), (340, 55)]
        edges = {(0, 1), (1, 2), (2, 5), (0, 3), (2, 3), (2, 4), (1, 3), (3, 4), (4, 5)}
    elif layout == 'grid':
        columns = math.ceil(math.sqrt(count))
        rows = math.ceil(count / columns)
        points = [(55 + (i % columns) * 290 / (columns - 1),
                   50 + (i // columns) * 170 / (rows - 1)) for i in range(count)]
        edges = {(i, i + 1) for i in range(count - 1) if (i + 1) % columns}
        edges |= {(i, i + columns) for i in range(count - columns)}
    else:
        phase = rng.uniform(0, math.tau)
        size = count - 1 if layout == 'star' else count
        points = [(200 + (110 if layout != 'network' else rng.uniform(75, 140)) * math.cos(phase + math.tau * i / size),
                   140 + (90 if layout != 'network' else rng.uniform(65, 105)) * math.sin(phase + math.tau * i / size)) for i in range(size)]
        if layout == 'star':
            points.append((200, 140))
            edges = {(i, count - 1) for i in range(count - 1)}
        else:
            edges = {tuple(sorted((i, (i + 1) % count))) for i in range(count)}
            if layout == 'network':
                edges |= {tuple(sorted((i, rng.randrange(count)))) for i in range(count)}
                edges = {(i, j) for i, j in edges if i != j}
    highlight = 2 if layout == 'classic' else (len(points) - 1 if layout == 'star' else rng.randrange(len(points)))
    lines = ''.join(f'<path d="M{points[i][0]:.1f} {points[i][1]:.1f} L{points[j][0]:.1f} {points[j][1]:.1f}"/>' for i, j in sorted(edges))
    nodes = ''
    for i, (x, y) in enumerate(points):
        if i == highlight:
            nodes += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="20" fill="var(--orange)" fill-opacity=".12"/>'
        fill = 'var(--orange)' if i == highlight else 'var(--paper)'
        stroke = 'var(--orange)' if i == highlight else 'var(--blue)'
        nodes += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>'
        nodes += f'<text x="{x + 12:.1f}" y="{y - 12:.1f}" fill="currentColor" font-family="monospace" font-size="9">{i + 1:02}</text>'
    alt = escape(visual.get('alt', 'Illustrative network of connected systems'))
    return (f'<svg viewBox="0 0 400 280" role="img" aria-label="{alt}" xmlns="http://www.w3.org/2000/svg">'
            '<defs><pattern id="network-grid" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="currentColor" opacity=".18"/></pattern></defs>'
            '<rect width="400" height="280" fill="url(#network-grid)"/>'
            '<g fill="none" stroke="currentColor" stroke-width="1.3" opacity=".6">' + lines
            + '<circle cx="200" cy="140" r="105" stroke-dasharray="3 7" opacity=".5"/></g>' + nodes + '</svg>')


def render_visual(config):
    visual = config.get('visual', {})
    if not isinstance(visual, dict):
        raise ValueError('visual must be a JSON object')
    kind = visual.get('type', 'network')
    if kind == 'none':
        return ''
    if kind == 'network':
        media = network_svg(visual, config['slug'])
    elif kind == 'image':
        if not isinstance(visual.get('alt'), str) or not visual['alt'].strip():
            raise ValueError('Image visuals require visual.alt describing the image')
        fit = visual.get('fit', 'contain')
        if fit not in ('contain', 'cover'):
            raise ValueError('visual.fit must be contain or cover')
        media = f'<img class="project-image fit-{fit}" src="{visual_source(visual.get("src"))}" alt="{escape(visual["alt"], quote=True)}">'
    elif kind == 'video':
        poster = f' poster="{visual_source(visual["poster"])}"' if visual.get('poster') else ''
        media = (f'<video controls preload="metadata" playsinline{poster} aria-label="{escape(visual.get("title", "Project video"))}">'
                 f'<source src="{visual_source(visual.get("src"))}">'
                 f'<a href="{visual_source(visual.get("src"))}">Watch project video</a></video>')
    elif kind == 'embed':
        if not isinstance(visual.get('title'), str) or not visual['title'].strip():
            raise ValueError('Embedded visuals require visual.title')
        media = (f'<iframe src="{visual_source(visual.get("src"))}" title="{escape(visual["title"], quote=True)}" '
                 'loading="lazy" sandbox="allow-scripts" allowfullscreen></iframe>')
    else:
        raise ValueError('visual.type must be network, image, video, embed, or none')
    label = escape(visual.get('label', 'Systems / connections' if kind == 'network' else 'Project / visual'))
    caption = escape(visual.get('caption', 'Networked systems & collective behaviour' if kind == 'network' else ''))
    return (f'<figure class="diagram visual-{kind}"><div class="diagram-label">{label}</div>{media}'
            + (f'<figcaption class="diagram-caption">{caption}</figcaption>' if caption else '') + '</figure>')


def render_project(config, sections, root=ROOT):
    required = ('slug', 'tag', 'code', 'title', 'subtitle', 'status', 'period', 'funding', 'lead', 'institution')
    for field in required:
        if not isinstance(config.get(field), str) or not config[field].strip():
            raise ValueError(f'Project requires a nonempty {field}')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', config['slug']):
        raise ValueError('Project slug must contain lowercase words separated by hyphens')
    tag = config['tag'].strip().casefold()
    if not re.fullmatch(r'project:[a-z0-9]+(?:-[a-z0-9]+)*', tag):
        raise ValueError('Project tag must have the form project:example-project')
    people = personnel_for(tag, root)
    publication_groups = []
    count = 0
    for cat in SECTION_ORDER:
        entries = [entry for entry in sections.get(cat, []) if tag in keyword_tags(entry)]
        if not entries:
            continue
        count += len(entries)
        publication_groups.append(
            f'<div class="publication-group"><h3>{SECTION_HEADINGS[cat]}</h3>'
            + '\n'.join(render_card(entry, cat) for entry in entries) + '</div>'
        )
    values = {field: escape(config[field], quote=True) for field in required}
    values['overview'] = '\n'.join(f'<p>{escape(p)}</p>' for p in config.get('overview', []))
    values['objectives'] = '\n'.join(
        f'<article class="objective"><span class="objective-label">Objective {i:02}</span>'
        f'<h3>{escape(obj["title"])}</h3><p>{escape(obj["text"])}</p></article>'
        for i, obj in enumerate(config.get('objectives', []), 1)
    )
    values['links'] = '\n'.join(
        f'<a href="{escape(link["url"], quote=True)}">{escape(link["label"])}</a>'
        for link in config.get('links', [])
    )
    values['visual'] = render_visual(config)
    values['hero_class'] = '' if values['visual'] else ' hero-text-only'
    values['personnel_count'] = str(len(people))
    values['personnel_noun'] = 'person' if len(people) == 1 else 'people'
    values['publication_count'] = str(count)
    values['personnel'] = ('<div class="personnel-grid">' + '\n'.join(people) + '</div>') if people else '<p class="empty">Project personnel will be announced here.</p>'
    values['publications'] = '\n'.join(publication_groups) if count else '<p class="empty">Project publications will be listed here as they become available.</p>'
    template = Template((root / 'templates/research-project.html').read_text(encoding='utf-8'))
    return template.substitute(values)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('configs', nargs='*', type=Path, help='JSON files; defaults to projects/*.json')
    parser.add_argument('--check', action='store_true', help='Check generated pages without writing')
    args = parser.parse_args()
    try:
        configs = args.configs or sorted((ROOT / 'projects').glob('*.json'))
        sections = load_sections()
        outputs = {}
        for path in configs:
            try:
                config = json.loads(path.read_text(encoding='utf-8'))
            except json.JSONDecodeError as exc:
                hint = (' Keep quoted text on one line or use an escaped \\n.'
                        if exc.msg.startswith('Invalid control character') else '')
                raise ValueError(
                    f'{path}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}.{hint}'
                ) from exc
            page = render_project(config, sections)
            output = ROOT / (config['slug'] + '.html')
            if output in outputs:
                raise ValueError(f'Duplicate project output: {output.name}')
            if output.exists() and '<!-- Generated by generate_project_pages.py' not in output.read_text(encoding='utf-8'):
                raise ValueError(f'Refusing to overwrite an existing non-generated page: {output.name}')
            outputs[output] = '<!-- Generated by generate_project_pages.py; edit projects JSON and templates instead. -->\n' + page
        stale = [path for path, page in outputs.items() if not path.exists() or path.read_text(encoding='utf-8') != page]
        if args.check and stale:
            raise ValueError('Project pages need updating: ' + ', '.join(p.name for p in stale))
        if args.check:
            print('Project pages are up to date.')
        else:
            for path in stale:
                path.write_text(outputs[path], encoding='utf-8')
                print(f'Written: {path.name}')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
