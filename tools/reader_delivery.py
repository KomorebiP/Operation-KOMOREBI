"""Package verified reader data without changing source or download contents.

Raw exports and ready-made ZIPs remain downloadable as revision-bound release
assets. Interactive indexes are stored locally as authenticated gzip files.
This runs only after the complete source, link and ZIP checks have passed.
"""
import base64
import gzip
import hashlib
import html
import json
from html.parser import HTMLParser
from pathlib import Path
import posixpath
import re
from urllib.parse import unquote, urlsplit

REPOSITORY = 'KomorebiP/Operation-KOMOREBI'
BASE_PATH = '/Operation-KOMOREBI/'
JSON_FILES = {'notation/index.json', 'notation/search.json', 'side-reader-index.json',
              'downloads/selection.json', 'search-index.json'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compressed_json(path):
    return path in JSON_FILES or bool(re.fullmatch(r'notation/(?:data|reader)/[a-z0-9-]+\.json', path))


def asset_name(path):
    if not re.fullmatch(r'[a-zA-Z0-9_./-]+', path) or '..' in path.split('/'):
        raise ValueError('Unsafe delivery asset path: '+path)
    # Directory separators cannot collide with the names produced here.
    if '--' in path:
        raise ValueError('Ambiguous delivery asset name: '+path)
    return path.rsplit('/', 1)[-1] if path.endswith('.zip') else path.replace('/', '--')


def local_target(value, page):
    value = html.unescape(value)
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        if parsed.scheme != 'https' or parsed.netloc.lower() != 'komorebip.github.io':
            return None
        if not parsed.path.startswith(BASE_PATH):
            return None
        return unquote(parsed.path[len(BASE_PATH):])
    if parsed.path.startswith('/'):
        return unquote(parsed.path[len(BASE_PATH):]) if parsed.path.startswith(BASE_PATH) else None
    return posixpath.normpath(posixpath.join(posixpath.dirname(page), unquote(parsed.path)))


class ExportLinks(HTMLParser):
    """Rewrite native links only; data-source URLs retain their logical names."""
    def __init__(self, text, page, records):
        super().__init__(convert_charrefs=False)
        self.page, self.records, self.changes = page, records, []
        self.offsets = [0]+[match.end() for match in re.finditer('\n', text)]
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        target = dict(attrs).get('href')
        if not target:
            return
        record = self.records.get(local_target(target, self.page))
        if not record:
            return
        raw = self.get_starttag_text()
        match = re.search(r'''\bhref\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)''', raw, re.I)
        if not match:
            raise ValueError('Could not locate export link')
        line, column = self.getpos()
        start = self.offsets[line-1]+column
        self.changes.append((start+match.start(), start+match.end(),
                             'href="'+html.escape(record['export_url'], quote=True)+'"'))


def rewrite_links(text, page, records):
    parser = ExportLinks(text, page, records)
    for start, end, value in reversed(parser.changes):
        text = text[:start]+value+text[end:]
    return text


def package(root, artifacts):
    root, artifacts = root.resolve(), artifacts.resolve()
    if artifacts == root or artifacts.is_relative_to(root) or root.is_relative_to(artifacts):
        raise ValueError('Release assets must have a separate output directory')
    if artifacts.exists() and any(artifacts.iterdir()):
        raise ValueError('Use an empty release asset directory')
    revision = json.loads((root/'build-info.json').read_bytes())['collection_revision']
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('Delivery needs a concrete Git revision')
    tag = 'reader-downloads-'+revision
    prefix = 'https://github.com/'+REPOSITORY+'/releases/download/'+tag+'/'
    artifacts.mkdir(parents=True, exist_ok=True)
    before = sum(path.stat().st_size for path in root.rglob('*') if path.is_file())
    paths = {path.relative_to(root).as_posix() for path in root.rglob('*.json')
             if compressed_json(path.relative_to(root).as_posix())}
    bundles = json.loads((root/'downloads/index.json').read_bytes())
    for bundle in bundles:
        path = bundle['url']
        if not re.fullmatch(r'downloads/[a-z0-9-]+\.zip', path):
            raise ValueError('Unexpected reading bundle path')
        raw = (root/path).read_bytes()
        if len(raw) != bundle['archive_bytes'] or sha(raw) != bundle['archive_sha256']:
            raise ValueError('Reading bundle identity changed')
        paths.add(path)
    records = {}
    for path in sorted(paths):
        target = root/path
        if target.is_symlink() or not target.resolve().is_relative_to(root):
            raise ValueError('Unsafe delivery source')
        raw = target.read_bytes()
        name = asset_name(path)
        record = dict(path=path, asset=name, bytes=len(raw), sha256=sha(raw), export_url=prefix+name)
        archive = artifacts/name
        archive.write_bytes(raw)
        if archive.read_bytes() != raw:
            raise ValueError('Release export changed bytes')
        if compressed_json(path):
            packed = gzip.compress(raw, compresslevel=9, mtime=0)
            if gzip.decompress(packed) != raw:
                raise ValueError('Compressed data changed bytes')
            (root/(path+'.gz')).write_bytes(packed)
            record.update(gzip=path+'.gz', gzip_bytes=len(packed), gzip_sha256=sha(packed))
        records[path] = record
    # Update the public download catalogue while preserving archive contents,
    # checksums, file lists and the original local route for compatibility.
    for bundle in bundles:
        bundle['local_url'] = bundle['url']
        bundle['url'] = records[bundle['url']]['export_url']
    (root/'downloads/index.json').write_text(json.dumps(bundles, ensure_ascii=False, separators=(',', ':'))+'\n', encoding='utf-8')
    fallback = root/'assets/vendor/fflate-0.8.3.js'
    manifest = dict(schema=1, revision=revision, repository=REPOSITORY, tag=tag, files=records,
                    fallback_integrity='sha256-'+base64.b64encode(hashlib.sha256(fallback.read_bytes()).digest()).decode())
    (root/'delivery.json').write_text(json.dumps(manifest, separators=(',', ':'))+'\n', encoding='utf-8')
    script_hash = sha((root/'assets/reader-data.js').read_bytes())[:12]
    pages = 0
    for file in sorted(root.rglob('*.html')):
        page = file.relative_to(root).as_posix()
        if page.split('/')[0] in {'assets', 'documents', 'downloads'}:
            continue
        original = file.read_text(encoding='utf-8')
        text = rewrite_links(original, page, records)
        script = (BASE_PATH+'assets/reader-data.js') if page == '404.html' else posixpath.relpath('assets/reader-data.js', posixpath.dirname(page) or '.')
        marker = '<script src="'+script+'?v='+script_hash+'" data-reader-delivery></script>'
        if '</head>' not in text:
            raise ValueError('Missing page head: '+page)
        # Synchronous small loader is installed before any deferred consumers.
        text = text.replace('</head>', marker+'</head>', 1)
        if page == '404.html':
            links = ''.join('<li><a href="'+record['export_url']+'">'+html.escape(path)+'</a></li>'
                            for path, record in records.items())
            text = text.replace('</main>', '<details id="retained-downloads"><summary>Find a download at its new address</summary><ul>'+links+'</ul></details></main>', 1)
        file.write_text(text, encoding='utf-8', newline='\n')
        pages += 1
    for path in paths:
        (root/path).unlink()  # Only the fixed, verified sources inside root.
    verify(root, artifacts)
    after = sum(path.stat().st_size for path in root.rglob('*') if path.is_file())
    report = dict(schema=1, revision=revision, files=len(records), reading_zips=len(bundles),
                  compressed_indexes=sum('gzip' in record for record in records.values()),
                  html_pages=pages, before_bytes=before, published_bytes=after, saved_bytes=before-after,
                  byte_identity_verified=True)
    (root/'delivery-report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    (artifacts/'delivery-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    (artifacts/'SHA256SUMS.txt').write_text(''.join(record['sha256']+'  '+record['asset']+'\n' for record in records.values()), encoding='utf-8')
    (artifacts/'RELEASE.md').write_text('Reader downloads for Operation-KOMOREBI revision `'+revision+'`.\n\n'
        'These are the byte-identical reading ZIPs and raw JSON exports validated before Pages packaging. '
        'The site retains its reading content and serves compressed copies of interactive indexes. '
        'Archive contents, source bytes and SHA-256 identities are preserved.\n', encoding='utf-8')
    return report


def verify(root, artifacts):
    manifest = json.loads((root/'delivery.json').read_bytes())
    for path, record in manifest['files'].items():
        raw = (artifacts/record['asset']).read_bytes()
        if len(raw) != record['bytes'] or sha(raw) != record['sha256']:
            raise ValueError('Export identity mismatch: '+path)
        if 'gzip' in record:
            packed = (root/record['gzip']).read_bytes()
            if len(packed) != record['gzip_bytes'] or sha(packed) != record['gzip_sha256'] or gzip.decompress(packed) != raw:
                raise ValueError('Index identity mismatch: '+path)
    return manifest
