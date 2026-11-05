"""Compact generated HTML attributes while preserving parsed page contents."""
from html.parser import HTMLParser
import re


ATTRIBUTE = re.compile(r'''\s+[^\s=/>]+(?:\s*=\s*(?P<value>"[^"]*"|'[^']*'|[^\s>]+))?''')
UNQUOTED = re.compile(r'[A-Za-z0-9_./:#?&;,%+-]+')


class PageTokens(HTMLParser):
    def __init__(self, text, *, compact=False):
        super().__init__(convert_charrefs=False)
        self.tokens = []
        self.removals = []
        self.compact = compact
        self.offsets = [0] + [match.end() for match in re.finditer('\n', text)]
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        self.tokens.append(('start', tag, attrs))
        if not self.compact:
            return
        raw = self.get_starttag_text()
        position = re.match(r'<[^\s/>]+', raw).end()
        line, column = self.getpos()
        offset = self.offsets[line - 1] + column
        while match := ATTRIBUTE.match(raw, position):
            value = match.group('value')
            if value and value[0] in {'"', "'"} and UNQUOTED.fullmatch(value[1:-1]):
                start, end = match.span('value')
                # A slash directly before /> would become part of an unquoted value.
                if raw[end:].startswith('/>'):
                    position = match.end()
                    continue
                self.removals.extend((offset + start, offset + end - 1))
            position = match.end()

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.tokens.append(('end', tag))

    def handle_endtag(self, tag):
        self.tokens.append(('end', tag))

    def handle_data(self, data):
        self.tokens.append(('text', data))

    def handle_entityref(self, name):
        self.tokens.append(('entity', name))

    def handle_charref(self, name):
        self.tokens.append(('char', name))

    def handle_comment(self, data):
        self.tokens.append(('comment', data))

    def handle_decl(self, decl):
        self.tokens.append(('declaration', decl))

    def handle_pi(self, data):
        self.tokens.append(('instruction', data))


def compact_html(text):
    original = PageTokens(text, compact=True)
    pieces, previous = [], 0
    for position in original.removals:
        pieces.append(text[previous:position])
        previous = position + 1
    pieces.append(text[previous:])
    result = ''.join(pieces)
    if original.tokens != PageTokens(result).tokens:
        raise ValueError('HTML compaction changed parsed page contents')
    return result


def compact_tree(root):
    files, savings = 0, 0
    for path in sorted(root.rglob('*.html')):
        # Retained source/download bytes and pinned vendor runtimes are immutable.
        if path.relative_to(root).parts[0] in {'assets', 'documents', 'downloads'}:
            continue
        before = path.read_bytes()
        after = compact_html(before.decode('utf-8')).encode('utf-8')
        if after != before:
            path.write_bytes(after)
            files += 1
            savings += len(before) - len(after)
    return dict(files=files, saved_bytes=savings, parsed_contents_preserved=True)
