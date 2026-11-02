"""Apply reviewed comma insertions to source-bound HTML prose, never to mathematics."""
import hashlib
import json
import re
from html.parser import HTMLParser

MANIFEST = 'manifests/reader-copyediting.json'
REPORT = 'documents/reader-copyediting.json'
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


def validate(data):
    if data.get('schema') != 1 or data.get('mathematical_token_changes') != 0:
        raise ValueError('Unknown copyediting record schema')
    seen = set()
    for row in data['changes']:
        if row['id'] in seen:
            raise ValueError('Duplicate copyediting correction')
        seen.add(row['id'])
        if not re.fullmatch(r'read/paper-[ivx]+/[a-z0-9/-]+\.html', row['page']):
            raise ValueError('Copyediting is limited to core reading chapters')
        if not re.fullmatch(r'L[1-9][0-9]*(?:-[1-9][0-9]*)?', row['anchor']):
            raise ValueError('Copyediting requires a source-passage anchor')
        before, after = row['before'], row['after']
        # This pass permits comma insertions only, with every letter and space retained.
        if not before or before == after or after.replace(',', '') != before.replace(',', '') or after.count(',') <= before.count(','):
            raise ValueError('Copyediting may only insert reviewed commas')
        cursor = 0
        for char in after:
            if cursor < len(before) and char == before[cursor]:
                cursor += 1
            elif char != ',':
                raise ValueError('Copyediting changed text other than commas')
        if cursor != len(before) or type(row['count']) is not int or row['count'] < 1:
            raise ValueError('Invalid copyediting correction')
    return data


class Prose(HTMLParser):
    def __init__(self, body, changes, reverse=False):
        super().__init__(convert_charrefs=False)
        self.body, self.changes, self.reverse = body, changes, reverse
        self.lines = [0] + [match.end() for match in re.finditer('\n', body)]
        self.stack, self.edits = [], []
        self.counts = {row['id']: 0 for row in changes}

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, dict(attrs)))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        for index in range(len(self.stack)-1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        article = any(attrs.get('id') == 'chapter-text' for _, attrs in self.stack)
        target = next((attrs.get('href', '')[1:] for tag, attrs in reversed(self.stack)
                       if tag == 'a' and attrs.get('href', '').startswith('#L')), None)
        if not article and target is None:
            return
        if any(tag in {'code', 'pre', 'script', 'style', 'button'} or
               {'arithmatex', 'passage-links', 'passage-tools'} & set(attrs.get('class', '').split())
               for tag, attrs in self.stack):
            return
        anchor = next((attrs['id'] for _, attrs in reversed(self.stack)
                       if re.fullmatch(r'L[1-9][0-9]*(?:-[1-9][0-9]*)?', attrs.get('id', ''))), None) if article else target
        revised = data
        for row in self.changes:
            if row['anchor'] != anchor:
                continue
            before, after = (row['after'], row['before']) if self.reverse else (row['before'], row['after'])
            count = revised.count(before)
            if article:self.counts[row['id']] += count
            revised = revised.replace(before, after)
        if revised != data:
            line, column = self.getpos()
            start = self.lines[line-1] + column
            self.edits.append((start, start+len(data), revised))


def transform(body, changes, reverse=False):
    parser = Prose(body, changes, reverse)
    parser.feed(body)
    for row in changes:
        if parser.counts[row['id']] != row['count']:
            raise ValueError('Review copyediting passage or count: '+row['id'])
    for start, end, text in reversed(parser.edits):
        body = body[:start]+text+body[end:]
    return body


def prepare(reader):
    path = reader.site.root/MANIFEST
    reader.copyediting = []
    reader.applied_copyediting = set()
    if not path.is_file():
        return
    data = validate(json.loads(path.read_bytes()))
    chapters = {spec['url']: (spec, raw) for book in reader.readable_books.values()
                for spec, raw, _ in book['chapters']}
    for row in data['changes']:
        if row['page'] not in chapters:
            continue  # A deliberately selected subset of books may be built independently.
        spec, raw = chapters[row['page']]
        if spec['source'] != row['source'] or hashlib.sha256(raw).hexdigest() != row['source_sha256']:
            raise ValueError('Review stale copyediting source: '+row['id'])
        reader.copyediting.append(row)


def apply(reader, page, body):
    changes = [row for row in getattr(reader, 'copyediting', []) if row['page'] == page]
    if not changes:
        return body
    body = transform(body, changes)
    reader.applied_copyediting.update(row['id'] for row in changes)
    note = ('<p class="copyediting-note">This HTML chapter includes reviewed punctuation corrections. '
            '<a href="'+reader.site.rel(REPORT, page)+'">View the correction record</a>.</p>')
    return body.replace('<article id="chapter-text"', note+'<article id="chapter-text"', 1)


def publish(reader):
    changes = getattr(reader, 'copyediting', [])
    if getattr(reader, 'applied_copyediting', set()) != {row['id'] for row in changes}:
        raise ValueError('Every selected copyediting correction must be applied')
    reader.site.write(REPORT, json.dumps(dict(schema=1, collection_revision=reader.site.revision,
        mathematical_token_changes=0, changes=changes), ensure_ascii=False, indent=2)+'\n')


def verify(root, documents, pages):
    data = validate(json.loads((root/REPORT).read_bytes()))
    assert data['collection_revision'] == documents['source_revision']
    sources = {row['repository_path']: row for row in documents['files']}
    grouped = {}
    for row in data['changes']:
        raw = (root/sources[row['source']]['file_url']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row['source_sha256']
        assert row['anchor'] in pages[row['page']].ids
        grouped.setdefault(row['page'], []).append(row)
    for page, changes in grouped.items():
        body = (root/page).read_text(encoding='utf-8')
        restored = transform(body, changes, reverse=True)
        assert transform(restored, changes) == body
    return dict(corrections=len(data['changes']), chapters=len(grouped), mathematical_token_changes=0)
