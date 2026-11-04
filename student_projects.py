"""Shared project-tag syntax and student identity matching."""
from html import unescape
import re
import unicodedata
from generate_publications import latex_to_html

TAG_PATTERN = r'project:[a-z0-9]+(?:-[a-z0-9]+)*'


def project_tags(value, bib=False):
    parts = value.split(',') if bib else value.split()
    tags = set()
    for part in parts:
        part = part.strip().casefold()
        if not part:
            continue
        if bib and not part.startswith('project:'):
            continue
        if not re.fullmatch(TAG_PATTERN, part):
            raise ValueError(f'Invalid project tag {part!r}; use project:name (commas in BibTeX, spaces in HTML)')
        tags.add(part)
    return tags


def name_words(value):
    value = unicodedata.normalize('NFKD', unescape(latex_to_html(value))).casefold()
    return re.findall(r'[a-z0-9]+', ''.join(c for c in value if not unicodedata.combining(c)))


def same_student(a, b):
    left, right = name_words(a), name_words(b)
    # Existing website spellings differ from the CV in these cases.
    aliases = {'nicholas': 'nicolas', 'yogajarah': 'yogarajah',
               'muelebach': 'muhlebach', 'boesch': 'bosch'}
    left = [aliases.get(w, w) for w in left]
    right = [aliases.get(w, w) for w in right]
    return bool(left and right) and (left == right or
        (len(left) >= 2 and len(right) >= 2 and left[0] == right[0] and left[-1] == right[-1]))


def merge_keywords(value, tags):
    keywords = [part.strip() for part in value.split(',')
                if part.strip() and not part.strip().casefold().startswith('project:')]
    return ', '.join(keywords + sorted(tags))
