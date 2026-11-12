"""Source-bound 12 November Smith/RLC continuation. Author: Komorebi P."""
from __future__ import annotations

import hashlib
import html
import json
from pathlib import PurePosixPath
import posixpath
import re
from urllib.parse import quote, unquote, urlsplit
import zipfile

BASE = 'research/smith-chart/continuation'
PAGE = 'read/smith-chart/continuation.html'


def load(root):
    """Authenticate complete archives and selected statements before rendering."""
    manifest = json.loads((root / BASE / 'manifest.json').read_bytes())
    files = {}
    for name, record in manifest['archives'].items():
        path = root / BASE / 'archives' / name
        if path.name != name or hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('Smith continuation archive checksum mismatch: ' + name)
        with zipfile.ZipFile(path) as z:
            infos = z.infolist()
            if len(infos) != record['files'] or len({i.filename for i in infos}) != len(infos):
                raise ValueError('Unexpected Smith continuation archive inventory')
            if sum(i.file_size for i in infos) > 40_000_000:
                raise ValueError('Smith continuation archive exceeds resource cap')
            content = {}
            for info in infos:
                p = PurePosixPath(info.filename)
                if (info.is_dir() or p.is_absolute() or '..' in p.parts or ':' in info.filename
                        or '\\' in info.filename or not info.filename.startswith(record['prefix'])
                        or (info.external_attr >> 16) & 0o170000 == 0o120000):
                    raise ValueError('Unsafe Smith continuation archive entry')
                member = info.filename[len(record['prefix']):]
                if not member or member.lower().endswith(('.pdf', '.html', '.htm')):
                    raise ValueError('Unexpected document in authored checkpoint')
                content[member] = z.read(info)
            files[name] = content
    for chapter in manifest['chapters']:
        raw = files[chapter['archive']][chapter['member']]
        if hashlib.sha256(raw).hexdigest() != chapter['source_sha256']:
            raise ValueError('Smith continuation chapter checksum mismatch')
    for name, checksum in manifest['handoff_records'].items():
        if hashlib.sha256((root / BASE / name).read_bytes()).hexdigest() != checksum:
            raise ValueError('Smith continuation handoff record mismatch')
    return manifest, files


def source_directory(manifest, archive):
    # Use the first chapter's stable slug for this archive, shared by both composition notes.
    return 'documents/smith-rlc/' + next(c['slug'] for c in manifest['chapters'] if c['archive'] == archive)


def render(text):
    import markdown
    from build_reader_site import math_fences, slugify
    return math_fences(markdown.markdown(text, extensions=['tables', 'fenced_code', 'toc', 'pymdownx.arithmatex'],
        extension_configs={'toc': {'slugify': slugify}, 'pymdownx.arithmatex': {'generic': True}}))


def chapter_body(site, manifest, files, chapter):
    from build_reader_site import Rewriter, page_contents
    from smith_chart_research import raw_url, decorate_supplement
    page = 'read/smith-chart/' + chapter['slug'] + '.html'
    archive = chapter['archive']
    directory = source_directory(manifest, archive)
    rendered = render(files[archive][chapter['member']].decode('utf-8'))

    def resolve(target, image):
        parts = urlsplit(html.unescape(target))
        if parts.scheme or parts.netloc or not parts.path:
            return target
        member = posixpath.normpath(posixpath.join(posixpath.dirname(chapter['member']), unquote(parts.path)))
        if member not in files[archive]:
            raise ValueError('Unresolved Smith continuation source link: ' + member)
        match = next((c for c in manifest['chapters'] if c['archive'] == archive and c['member'] == member), None)
        dest = ('read/smith-chart/' + match['slug'] + '.html') if match and not image else directory + '/' + member
        return site.rel(dest, page) + ('#' + parts.fragment if parts.fragment else '')

    rewrite = Rewriter(resolve)
    rewrite.feed(rendered)
    content = ''.join(rewrite.out)
    table_class = 'table-wrap numeric-table' if chapter['slug'] == 'exact-six' else 'table-wrap'
    content = re.sub(r'<table>.*?</table>', lambda m: '<div class="' + table_class + '" tabindex="0" role="region" aria-label="Scrollable data table">' + m[0] + '</div>', content, flags=re.S)
    if chapter['slug'] == 'exact-six':
        diagram = site.rel(directory + '/figures/topology.svg', page)
        content = re.sub(r'(<img\b[^>]+>)', lambda m: m[1] +
            '</p><p><a href="' + diagram + '">Open the circuit diagram at full size</a>', content, count=1)
    archive_url = raw_url(site.revision, BASE + '/archives/' + archive)
    status = ('<aside class="research-update" aria-label="Current evidence status"><p><strong>12 November 2026.</strong> '
              + html.escape(chapter['status']) + ' This reading preserves the checkpoint statement. '
              'Its original review labels describe project records; this publication adds no outside peer review or Lean proof.</p></aside>')
    links = ('<nav class="research-actions" aria-label="Chapter resources">'
             '<a href="continuation.html">Current results and evidence</a>'
             '<a href="' + html.escape(archive_url, quote=True) + '">Download complete checkpoint</a>'
             '<a href="' + site.rel(directory + '/' + chapter['member'], page) + '">Original Markdown</a>'
             '<a href="research.html">Historical research reading</a></nav>')
    content = re.sub(r'(</h1>)', lambda m: m[1] + status + links + page_contents(content), content, count=1)
    index = manifest['chapters'].index(chapter)
    adjacent = []
    for offset, label in ((-1, 'Previous'), (1, 'Next')):
        if 0 <= index + offset < len(manifest['chapters']):
            c = manifest['chapters'][index + offset]
            adjacent.append('<a href="' + c['slug'] + '.html">' + label + ': ' + html.escape(c['title']) + '</a>')
    content += '<nav class="research-actions" aria-label="Continue reading">' + ''.join(adjacent) + '</nav>'
    return decorate_supplement(site, page, '<article>' + content + '</article>')


def publish(site):
    from build_reader_site import page_contents
    from smith_chart_research import decorate_supplement, raw_url
    manifest, files = load(site.root)
    # Serve the complete authored sources, retaining every byte and relative source path.
    for archive, members in files.items():
        directory = site.output / source_directory(manifest, archive)
        for member, raw in members.items():
            target = directory / member
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    hub = render((site.root / BASE / 'READING.md').read_text(encoding='utf-8'))
    hub = re.sub(r'<table>.*?</table>', lambda m: '<div class="table-wrap" tabindex="0" role="region" aria-label="Scrollable evidence table">' + m[0] + '</div>', hub, flags=re.S)
    hub = re.sub(r'(</h1>)', lambda m: m[1] + page_contents(hub), hub, count=1)
    body = decorate_supplement(site, PAGE, '<article>' + hub + '</article>')
    source = 'https://github.com/KomorebiP/Operation-KOMOREBI/blob/' + site.revision + '/' + BASE
    site.page(PAGE, 'Smith chart: RLC continuation and exact six-reactive closure', body, source)
    site.search.append(dict(title='Smith chart: RLC continuation and exact six-reactive closure', group='Collection', kind='Examples',
        url=PAGE, work_ids=[], text=html.unescape(re.sub('<[^>]*>', ' ', hub))))
    for chapter in manifest['chapters']:
        page = 'read/smith-chart/' + chapter['slug'] + '.html'
        body = chapter_body(site, manifest, files, chapter)
        site.page(page, chapter['title'], body, raw_url(site.revision, BASE + '/archives/' + chapter['archive']))
        site.search.append(dict(title=chapter['title'], group='Collection', kind='Examples', url=page, work_ids=[],
            text=html.unescape(re.sub('<[^>]*>', ' ', body))[:50000]))
