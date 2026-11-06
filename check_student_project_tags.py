#!/usr/bin/env python3
"""Check project tags on student cards against CV supervision keywords."""
from html.parser import HTMLParser
from pathlib import Path
import sys

from generate_publications import parse_bib_file
from student_projects import project_tags, same_student

ROOT = Path(__file__).resolve().parent


class Cards(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.cards = []
        self.card = None
        self.heading = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'article' and {'phd-card', 'master-card'} & set(attrs.get('class', '').split()):
            self.card = {'name': '', 'tags': attrs.get('data-projects', ''), 'key': attrs.get('data-bib-key', '')}
        if self.card is not None and tag == 'h3':
            self.heading = True

    def handle_data(self, data):
        if self.card is not None and self.heading:
            self.card['name'] += data

    def handle_endtag(self, tag):
        if tag == 'h3':
            self.heading = False
        if tag == 'article' and self.card is not None:
            self.cards.append(self.card)
            self.card = None


def check(root=ROOT):
    errors = []
    for bibname, files, types in [
        ('11-phd.bib', ['phd-cards.html'], {'phdstudent'}),
        ('9-mentor.bib', ['current-msc.html', 'past-msc.html'], {'masterstudent', 'undergraduate'}),
    ]:
        entries = [e for e in parse_bib_file(root / 'cv' / bibname) if e['_type'] in types]
        bib_tags = []
        for entry in entries:
            try:
                bib_tags.append(project_tags(entry.get('keywords', ''), bib=True))
            except ValueError as exc:
                errors.append(f"{bibname}: {entry['_key']}: {exc}")
                bib_tags.append(set())
        seen = set()
        for filename in files:
            for card in Cards((root / filename).read_text(encoding='utf-8')).cards:
                context = f"{filename}: {card['name']}"
                try:
                    tags = project_tags(card['tags'])
                except ValueError as exc:
                    errors.append(f'{context}: {exc}')
                    continue
                candidates = [i for i, e in enumerate(entries)
                              if (e['_key'].casefold() == card['key'].casefold() if card['key']
                                  else same_student(e.get('student', ''), card['name']))]
                if len(candidates) > 1 and card['key']:
                    candidates = [i for i in candidates if same_student(entries[i].get('student', ''), card['name'])]
                if len(candidates) != 1:
                    if tags or card['key'] or any(bib_tags[i] for i in candidates):
                        errors.append(f'{context}: expected one match in {bibname}, found {len(candidates)}; use a unique data-bib-key')
                    continue
                index = candidates[0]
                seen.add(index)
                if tags != bib_tags[index]:
                    errors.append(f"{context} ↔ {bibname}: {entries[index]['_key']}: "
                                  f"card tags={sorted(tags)}, BibTeX tags={sorted(bib_tags[index])}")
        for i, entry in enumerate(entries):
            if bib_tags[i] and i not in seen:
                errors.append(f"{bibname}: {entry['_key']} ({entry.get('student', '')}): tagged student has no matching card")
    return errors


def main():
    try:
        errors = check()
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1
    if errors:
        print('Student project tags do not match:\n  ' + '\n  '.join(errors), file=sys.stderr)
        return 1
    print('Student project tags match between CV bibliographies and website cards.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
