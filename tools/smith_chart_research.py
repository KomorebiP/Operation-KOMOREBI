"""Build a source-bound reading from the retained Smith chart research archive."""
from __future__ import annotations

import base64
import hashlib
import html
from pathlib import PurePosixPath
import re
from urllib.parse import quote
import zipfile

ARCHIVE = 'research/smith-chart/SmithChart_Complete.zip'
ROOT = 'Smith_Chart_Research_2026-11-11/'
ARCHIVE_SHA256 = '39fd0d659ef6c006eebb129e08a9b2ced72ce5b857ba846d6481711c951c371e'
HTML_NAME = 'Smith_Chart_Extended_Seven_Reactive_Exact.html'
HTML_SHA256 = '414ec71334d442c32d82c35c86b5a884fd027e211745fe9581b443c401cd895f'
MANUSCRIPT = 'Smith_Chart_Extended_Seven_Reactive_Exact.md'
CERTIFICATE = 'downloads/Smith_Chart_Exact_Certificate.zip'
PAGE = 'read/smith-chart/research.html'


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def raw_url(revision, path):
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('A full source revision is required')
    return 'https://raw.githubusercontent.com/KomorebiP/Operation-KOMOREBI/' + revision + '/' + quote(path, safe='/')


def archive_contents(root):
    """Validate the retained ZIP and all manifest entries, then return its files."""
    archive = root / ARCHIVE
    if sha256(archive.read_bytes()) != ARCHIVE_SHA256:
        raise ValueError('Smith chart research archive checksum mismatch')
    with zipfile.ZipFile(archive) as z:
        infos = z.infolist()
        if len(infos) != 172 or len({i.filename for i in infos}) != len(infos):
            raise ValueError('Unexpected or duplicate archive entries')
        if sum(i.file_size for i in infos) > 30_000_000:
            raise ValueError('Unexpected archive size')
        files = {}
        for i in infos:
            path = PurePosixPath(i.filename)
            if (i.is_dir() or path.is_absolute() or '..' in path.parts or '\\' in i.filename
                    or ':' in i.filename or not i.filename.startswith(ROOT)
                    or (i.external_attr >> 16) & 0o170000 == 0o120000):
                raise ValueError('Unsafe archive entry')
            files[i.filename[len(ROOT):]] = z.read(i)
    manifest = {}
    for line in files['MANIFEST.sha256'].decode('utf-8').splitlines():
        match = re.fullmatch(r'([0-9a-f]{64})  (.+)', line)
        if not match or match[2] in manifest:
            raise ValueError('Invalid archive manifest')
        manifest[match[2]] = match[1]
    if len(manifest) != 170 or set(files) - set(manifest) != {'MANIFEST.sha256', 'PACKAGE_VALIDATION.json'}:
        raise ValueError('Unexpected archive manifest coverage')
    for name, expected in manifest.items():
        if name not in files or sha256(files[name]) != expected:
            raise ValueError('Archive manifest mismatch: ' + name)
    if sha256(files[HTML_NAME]) != HTML_SHA256:
        raise ValueError('Unexpected reading edition')
    # Public figure and download URLs must serve the exact archived bytes.
    for name in [n for n in files if n.startswith('figures/')] + [MANUSCRIPT, CERTIFICATE]:
        target = root / 'research/smith-chart' / name
        if not target.is_file() or target.read_bytes() != files[name]:
            raise ValueError('Published source differs from archive: ' + name)
    return files


def reading_body(root, revision):
    files = archive_contents(root)
    source = files[HTML_NAME].decode('utf-8')
    if any(source.count(s) != 1 for s in ('<main class="page">', '</main>', '<dialog id="figure-dialog"', '</dialog>')):
        raise ValueError('Unexpected source document structure')
    main = source.split('<main class="page">', 1)[1].split('</main>', 1)[0]
    dialog = '<dialog id="figure-dialog"' + source.split('<dialog id="figure-dialog"', 1)[1].split('</dialog>', 1)[0] + '</dialog>'
    figures = {}
    for name, content in files.items():
        if name.startswith('figures/'):
            figures.setdefault(sha256(content), []).append(name)
    replacements = {'figures': 0, 'manuscript': 0, 'certificate': 0}

    def replace_data(match):
        attr, mime, data = match.groups()
        decoded = base64.b64decode(data, validate=True)
        if attr == 'src' and mime in {'image/png', 'image/svg+xml'}:
            matches = figures.get(sha256(decoded), [])
            if len(matches) != 1 or files[matches[0]] != decoded:
                raise ValueError('Embedded figure does not match one source figure')
            name = matches[0]
            replacements['figures'] += 1
        elif attr == 'href' and mime == 'text/markdown' and decoded == files[MANUSCRIPT]:
            name = MANUSCRIPT
            replacements['manuscript'] += 1
        elif attr == 'href' and mime == 'application/zip' and decoded == files[CERTIFICATE]:
            name = CERTIFICATE
            replacements['certificate'] += 1
        else:
            raise ValueError('Unexpected embedded source or download')
        return attr + '="' + raw_url(revision, 'research/smith-chart/' + name) + '"'

    main = re.sub(r'(src|href)="data:([^;,]+);base64,([A-Za-z0-9+/=]+)"', replace_data, main)
    if replacements != {'figures': 42, 'manuscript': 1, 'certificate': 1} or '="data:' in main:
        raise ValueError('Unexpected embedded asset inventory')
    if main.count('class="math inline"') != 1328 or main.count('class="math display"') != 340:
        raise ValueError('Unexpected mathematics inventory')
    main = main.replace('class="math inline"', 'class="math inline arithmatex"')
    main = main.replace('class="math display"', 'class="math display arithmatex"')
    zip_url = html.escape(raw_url(revision, ARCHIVE), quote=True)
    replay_url = 'https://github.com/KomorebiP/Operation-KOMOREBI/blob/' + revision + '/research/smith-chart/README.md'
    note = ('<aside class="research-notice" aria-label="Source and research status">'
            '<p><strong>Research draft, 11 November 2026.</strong> This reading preserves the archived manuscript. '
            'Its circuit claims, finite diagnostics, and open questions have different scopes. '
            'For the degree-six target, the draft describes a six-reactive realization using an ideal transformer. '
            'A transformer-free RLC-only realization with six reactive elements remains open. '
            'Historical novelty has not been established. '
            'The existing Lean companion covers selected results, not this entire draft.</p>'
            '<p>Figures load from the source repository. The complete archive includes a self-contained offline reading, '
            'all source files, and the original checksums.</p>'
            '<p><a href="' + zip_url + '">Download the complete research ZIP</a> · '
            '<a href="' + replay_url + '">Replay and source record</a> · '
            '<a href="../../smith-chart.html">Open the Smith chart laboratory</a> · '
            '<a href="../../collection/demonstrations/SMITH_CHART.html">Read the shorter companion guide</a>'
            '<span class="research-print"> · <button type="button" id="print-reading">Print reading</button></span></p>'
            '<details><summary>Archive checksum</summary><p>SHA-256: <code>' + ARCHIVE_SHA256 + '</code></p></details></aside>')
    cover_end = main.find('</section>')
    if cover_end < 0:
        raise ValueError('Missing source cover')
    cover_end += len('</section>')
    main = main[:cover_end] + note + main[cover_end:]
    return '<div id="smith-research"><div class="page">' + main + '</div>' + dialog + '</div>'


def publish(site):
    revision = site.revision
    body = reading_body(site.root, revision)
    for name in ('smith-research.css', 'smith-research.js'):
        path = 'assets/' + name
        value = site.rel(path, PAGE) + '?v=' + sha256((site.root / 'website' / path).read_bytes())[:12]
        body = ('<link rel="stylesheet" href="' + value + '">' + body) if name.endswith('.css') else (body + '<script defer src="' + value + '"></script>')
    site.page(PAGE, 'Smith chart: complete research reading', body,
              'https://github.com/KomorebiP/Operation-KOMOREBI/blob/' + revision + '/' + ARCHIVE)
    site.search.append(dict(title='Smith chart: complete research reading', group='Collection', kind='Examples',
                            url=PAGE, work_ids=[], text='Smith chart cyclic packets passive completion exact seven reactive circuit rational certificate six element open order separation infeasibility boundaries examples'))
