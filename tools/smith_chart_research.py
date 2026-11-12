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


def historical_body(root, revision):
    files = archive_contents(root)
    from smith_chart_edition import load, edit_prose
    figure_edition, prose = load(root, files, HTML_NAME)
    source = edit_prose(files[HTML_NAME].decode('utf-8'), prose)
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
        original = raw_url(revision, 'research/smith-chart/' + name)
        if attr == 'src':
            item = figure_edition[name]
            mobile = (' data-mobile-figure="' + raw_url(revision, 'research/smith-chart/' + item['mobile']) + '"') if 'mobile' in item else ''
            return ('src="' + raw_url(revision, 'research/smith-chart/' + item['desktop']) +
                    '" data-source-figure="' + original + '" data-figure-number="' + name[8:10] + '"' + mobile)
        return attr + '="' + original + '"'

    main = re.sub(r'(src|href)="data:([^;,]+);base64,([A-Za-z0-9+/=]+)"', replace_data, main)
    def responsive_figure(match):
        image = match[0]
        mobile = re.search(r'data-mobile-figure="([^"]+)"', image)
        return ('<picture><source media="(max-width: 600px)" srcset="' + mobile[1] + '">' + image + '</picture>') if mobile else image
    main = re.sub(r'<img\b[^>]*>', responsive_figure, main)
    def figure_header(match):
        figure = match.group(0)
        original = re.search(r'data-source-figure="([^"]+)"', figure)
        number = re.search(r'data-figure-number="([^"]+)"', figure)
        if not original or not number:
            raise ValueError('Missing vector figure source identity')
        header = ('<div class="figure-heading"><span>Figure ' + str(int(number[1])) + '</span>'
                  '<a href="' + original[1] + '">Original figure</a></div>')
        return figure.replace('>', '>' + header, 1)
    main = re.sub(r'<figure\b[^>]*>.*?</figure>', figure_header, main, flags=re.S)
    if replacements != {'figures': 42, 'manuscript': 1, 'certificate': 1} or '="data:' in main:
        raise ValueError('Unexpected embedded asset inventory')
    if main.count('class="math inline"') != 1328 or main.count('class="math display"') != 340:
        raise ValueError('Unexpected mathematics inventory')
    main = main.replace('class="math inline"', 'class="math inline arithmatex"')
    main = main.replace('class="math display"', 'class="math display arithmatex"')
    old_image_wrap = '<div id="dialog-image-wrap" class="dialog-image-wrap dialog-fit">'
    if dialog.count(old_image_wrap) != 1:
        raise ValueError('Unexpected figure dialog structure')
    dialog = dialog.replace(old_image_wrap,
        '<div id="dialog-image-wrap" class="dialog-image-wrap dialog-fit" tabindex="0" '
        'role="region" aria-label="Expanded figure; scroll to explore at full resolution">')
    dialog = dialog.replace('aria-label="Expanded mathematical figure"',
                            'aria-label="Expanded mathematical figure" aria-describedby="dialog-caption"', 1)
    zip_url = html.escape(raw_url(revision, ARCHIVE), quote=True)
    replay_url = 'https://github.com/KomorebiP/Operation-KOMOREBI/blob/' + revision + '/research/smith-chart/README.md'
    census_url = 'https://github.com/KomorebiP/Operation-KOMOREBI/blob/' + revision + '/research/smith-chart/computations/README.md'
    note = ('<aside class="research-notice" aria-label="Source and research status">'
            '<div class="research-notice-copy"><p class="research-notice-label">Historical research reading · updated 12 November 2026</p>'
            '<p>Revised prose and vector diagrams accompany the complete research draft. '
            'New supplements complete selected circuit and singular-interpolation arguments.</p>'
            '<p><strong>The six-reactive gap is closed.</strong> The newer checkpoint gives the degree-six target '
            'an exact transformer-free circuit with three inductors, three capacitors and seven positive resistors. '
            'The degree lower bound establishes a reactive minimum of six. '
            '<a href="continuation.html">Read the closure and the current RLC continuation.</a> '
            'Earlier open-status statements below are retained as history.</p>'
            '<details><summary>Source and review scope</summary><p>The archive retains the original text and artwork. '
            'The draft also describes a six-reactive realization using an ideal transformer. '
            'The Lean companions cover selected statements, not this entire draft. Historical novelty has not been established.</p>'
            '<p>SHA-256: <code>' + ARCHIVE_SHA256 + '</code></p></details></div>'
            '<nav class="research-actions" aria-label="Research reading resources">'
            '<a class="research-download" href="' + zip_url + '">Download full archive<span>172 files · offline reading</span></a>'
            '<a href="' + replay_url + '">Replay and source record</a>'
            '<a href="continuation.html">Current RLC results and exact-six closure</a>'
            '<a href="../../collection/demonstrations/SMITH_FIRST_ORDER_RL.html">One-inductor circuit proof</a>'
            '<a href="../../collection/demonstrations/SMITH_SINGULAR_COMPLETION.html">Singular-data completion proof</a>'
            '<a href="' + census_url + '">Five-node census check</a>'
            '<a href="../../smith-chart.html">Smith chart laboratory</a>'
            '<a href="../../collection/demonstrations/SMITH_CHART.html">Companion guide</a>'
            '<span class="research-print"><button type="button" id="print-reading">Print reading</button></span>'
            '</nav></aside>')
    cover_end = main.find('</section>')
    if cover_end < 0:
        raise ValueError('Missing source cover')
    cover_end += len('</section>')
    main = main[:cover_end] + note + main[cover_end:]
    marker = '<h3 id="numerical-conditioning-is-part-of-the-proof-obligation">'
    if main.count(marker) != 1:
        raise ValueError('Missing singular-completion insertion point')
    addition = ('<aside class="research-update" data-edition-addition="singular-completion">'
                '<p><strong>Completed in the supplement.</strong> A nullspace condition handles singular Pick matrices, '
                'and an exact curved boundary describes all feasible pairs of real packets at the two-node orbit. '
                '<a href="../../collection/demonstrations/SMITH_SINGULAR_COMPLETION.html">Read the proof and worked examples.</a></p></aside>')
    main = main.replace(marker, addition + marker, 1)
    update = ('<aside class="research-update" data-edition-addition="exact-six-closure">'
              '<p><strong>Later result: the reactive minimum is six.</strong> '
              'This section records the earlier state. The '
              '<a href="exact-six.html">positive eight-node circuit and exact root certificate</a> '
              'close the original target with three inductors and three capacitors.</p></aside>')
    for anchor in ('six-state-invariants', 'certified-cubic-extraction', 'seven-reactive-exact',
                   'what-has-been-settled-and-what-remains-open', 'suggested-reading-routes'):
        heading = re.search(r'<h2 id="' + anchor + r'">.*?</h2>', main)
        if not heading:
            raise ValueError('Missing historical-status insertion point: ' + anchor)
        main = main.replace(heading[0], heading[0] + update, 1)
    return ('<div id="smith-research"><div class="page">' + main + '</div>' + dialog +
            '<a class="research-contents-jump" href="#contents">↑ Contents</a></div>')


def reading_body(root, revision, site=None):
    from smith_chart_unified import build
    if site is None:
        raise ValueError('The consolidated reading requires the site source resolver')
    return build(site)


def publish(site):
    revision = site.revision
    from smith_chart_unified import TITLE
    body = reading_body(site.root, revision, site)
    for name in ('smith-research.css', 'smith-book.css', 'smith-research.js'):
        path = 'assets/' + name
        value = site.rel(path, PAGE) + '?v=' + sha256((site.root / 'website' / path).read_bytes())[:12]
        body = ('<link rel="stylesheet" href="' + value + '">' + body) if name.endswith('.css') else (body + '<script defer src="' + value + '"></script>')
    site.page(PAGE, TITLE, body,
              'https://github.com/KomorebiP/Operation-KOMOREBI/tree/' + revision + '/research/smith-chart/unified')
    site.search.append(dict(title=TITLE, group='Collection', kind='Examples', url=PAGE, work_ids=[],
        text='Smith chart exact six reactive closure deterministic certified family synthesis compact physical boundaries Hughes margin packet transfer'))
    for slug in ('exact-six','composition','low-order-synthesis','families','deterministic-family','obstruction','quantitative-transfer','effective-margin','compact-model-audit','formal-graph-core','typed-margins','component-tolerances','singular-completion','one-inductor','companion-guide'):
        marker = re.search(r'<h2 id="'+slug+r'">(.*?)</h2>',body,re.S)
        if marker:
            end = re.search(r'<h2\b',body[marker.end():])
            content = body[marker.end():marker.end()+end.start()] if end else body[marker.end():]
            site.search.append(dict(title=re.sub('<[^>]+>','',marker[1]), group='Collection', kind='Examples',
                url=PAGE+'#'+slug,work_ids=[],text=html.unescape(re.sub('<[^>]+>',' ',content))[:50000]))


def decorate_supplement(site, page, body):
    """Use the same readable article and touch-sized heading controls as the draft."""
    if body.count('<article>') != 1:
        raise ValueError('Unexpected first-order supplement structure')
    body = body.replace('<article>', '<article class="manuscript">', 1)
    css = 'assets/smith-research.css'
    value = site.rel(css, page) + '?v=' + sha256((site.root / 'website' / css).read_bytes())[:12]
    return '<link rel="stylesheet" href="' + value + '"><div id="smith-research" class="smith-supplement">' + body + '</div>'


def reading_chrome(body):
    """Keep shared reading actions together below the article's author line."""
    def arrange(match):
        cover=match[0]
        side=re.findall(r'<p class="side-launch">.*?</p>',cover,re.S)
        save=re.findall(r'<div class="reading-save"[^>]*>.*?</div>',cover,re.S)
        if len(side)!=1 or len(save)!=1:
            raise ValueError('Unexpected shared actions in Smith reading cover')
        cover=cover.replace(side[0],'',1).replace(save[0],'',1)
        controls='<div class="edition-reading-controls">'+save[0]+side[0]+'</div>'
        cover,count=re.subn(r'(<p class="author-line">.*?</p>)',lambda m:m[0]+controls,cover,count=1,flags=re.S)
        if count!=1:raise ValueError('Missing Smith reading author line')
        return cover
    result,count=re.subn(r'<section class="cover">.*?</section>',arrange,body,count=1,flags=re.S)
    if count!=1:raise ValueError('Missing Smith reading cover')
    return result
