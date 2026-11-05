"""Static link previews, canonical URLs and a sitemap for the reader site."""
from functools import lru_cache
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import quote
import xml.etree.ElementTree as ET

BASE_URL = 'https://komorebip.github.io/Operation-KOMOREBI/'
CARD_RECORD = 'assets/brand/sharing-card.json'
NOINDEX = {'404.html', 'search.html', 'side-by-side.html', 'reading-list.html', 'lean/run.html'}
MAX_DESCRIPTION = 165
DESCRIPTIONS = {
    'index.html': 'Explore mathematical papers, visual guides, recorded proofs, and executable examples in the Komorebi collection.',
    'collection/START_HERE.html': 'Start with a worked calculation, choose a reading route, and learn how to interpret the collection’s claims and evidence.',
    'collection/OPERATOR_AUDIT.html': 'A worked operator reference covering maps, algebra, packets, transfer, recovery, and stability, with definitions, examples, exercises, and a practical checklist.',
    'read/index.html': 'Read the Komorebi papers and books online, with formatted mathematics, chapter navigation, visual guides, and links to source files.',
    'read/start.html': 'Choose a visual introduction, a full study route, or a path through the proof and evidence for papers and books with complete online editions.',
    'read/visual-guides.html': 'Explore the collection’s visual guides, with worked diagrams and links to the corresponding mathematical manuscripts.',
    'works.html': 'Browse the Komorebi collection by work, subject, completion stage, and recorded evidence, then follow the reading and source links.',
    'playground.html': 'Run and edit mathematical Python examples in your browser. Inspect the output and follow links to the written calculations and recorded scope.',
    'collection/demonstrations/EULER_PACKETS.html': 'Follow Euler numbers through reciprocal series, polynomial coordinates, prime-adic bounds, and residual repair, with exact checks and source links.',
    'collection/demonstrations/WAVELET_POLYPHASE.html': 'Follow a signal through Haar decomposition, polyphase filter transport, reconstruction, and omitted-interaction errors, with exact worked checks.',
    'collection/examples/02_SEEDS.html': 'Work through finite seed-generation examples, compare operator actions, and follow the links to the mathematical sources and recorded evidence.',
    'collection/works/paper-xi.html': 'Study finite arithmetic packets and restricted comparison constructions, with the general arithmetic realization problem kept separate and open.',
    'collection/works/paper-xii.html': 'Read support descent, finite Hecke packets, and conditional completion criteria, with arithmetic hypotheses and formal coverage stated separately.',
}


def canonical_url(path):
    if (not path or path.startswith('/') or '\\' in path or any(c in path for c in '?#:\0')
            or any(p in {'', '.', '..'} for p in path.split('/')) or not path.endswith('.html')):
        raise ValueError('Invalid reader page: '+path)
    target = path[:-len('index.html')] if path.split('/')[-1] == 'index.html' else path
    return BASE_URL + quote(target, safe='/')


def indexable(path):
    return path not in NOINDEX


def compact(text):
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) <= MAX_DESCRIPTION:
        return text
    return text[:MAX_DESCRIPTION-1].rsplit(' ', 1)[0].rstrip(' ,;:')+'…'


class Paragraphs(HTMLParser):
    """Keep prose; navigation, controls, code and raw equations are not summaries."""
    ignored = {'nav', 'aside', 'details', 'pre', 'code', 'button', 'form', 'script', 'style'}
    void = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, body):
        super().__init__()
        self.stack = []
        self.excluded = False
        self.current = None
        self.prose = 0
        self.blocked = False
        self.paragraphs = []
        self.feed(body)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        old = self.excluded
        if self.current is not None and (tag in {'code','pre'} or 'arithmatex' in attrs.get('class','').split()):
            self.blocked = True
        self.excluded = old or tag in self.ignored or 'arithmatex' in attrs.get('class', '').split()
        if tag not in self.void:
            self.stack.append((tag, old))
        else:
            self.excluded = old
        if tag == 'p' and not self.excluded:
            self.current = []
            self.prose = 0
            self.blocked = False

    def handle_data(self, text):
        if self.current is not None and not self.excluded:
            self.current.append(text)
            if not any(tag == 'a' for tag, _ in self.stack):
                self.prose += len(text.strip())

    def handle_endtag(self, tag):
        if tag == 'p' and self.current is not None:
            text = re.sub(r'\s+', ' ', ''.join(self.current)).strip()
            if not self.blocked and len(text) >= 60 and self.prose >= 40 and len(text.split()) >= 7:
                self.paragraphs.append(text)
            self.current = None
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                self.excluded = self.stack[i][1]
                del self.stack[i:]
                break


def description(path, title, body):
    if path in DESCRIPTIONS:
        return DESCRIPTIONS[path]
    start = body.find('<article id="chapter-text"')
    paragraphs = Paragraphs(body[start:] if start >= 0 else body).paragraphs
    return compact(paragraphs[0] if paragraphs else
                   title+'. Read this page and its source links in the Komorebi collection.')


@lru_cache(maxsize=1)
def card(root=None):
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    return json.loads((root/'website'/CARD_RECORD).read_bytes())


def head_metadata(path, title, body, root=None):
    url = canonical_url(path)
    summary = description(path, title, body)
    image = card(root)
    image_url = BASE_URL+image['image']+'?v='+image['sha256'][:12]
    e = lambda value: html.escape(str(value), quote=True)
    tags = ['<meta name="description" content="'+e(summary)+'">']
    if path != '404.html':
        tags.append('<link rel="canonical" href="'+e(url)+'">')
    if not indexable(path):
        tags.append('<meta name="robots" content="noindex,follow">')
    properties = {
        'og:site_name': 'Komorebi', 'og:type': 'website', 'og:title': title+' · Komorebi',
        'og:description': summary, 'og:url': url, 'og:image': image_url,
        'og:image:type': 'image/jpeg', 'og:image:width': image['width'],
        'og:image:height': image['height'], 'og:image:alt': image['alt'],
    }
    tags += ['<meta property="'+key+'" content="'+e(value)+'">' for key, value in properties.items()]
    # Card consumers use the Open Graph title, description and image above.
    tags += ['<meta name="twitter:card" content="summary_large_image">',
             '<meta name="twitter:image:alt" content="'+e(image['alt'])+'">']
    return '\n'.join(tags)


def jpeg_dimensions(raw):
    assert raw[:2] == b'\xff\xd8', 'Sharing image must be a JPEG'
    at = 2
    while at+4 <= len(raw):
        assert raw[at] == 255, 'Malformed sharing JPEG'
        while raw[at] == 255:
            at += 1
        marker = raw[at]
        at += 1
        size = int.from_bytes(raw[at:at+2], 'big')
        assert size >= 2 and at+size <= len(raw), 'Malformed sharing JPEG segment'
        if marker in {0xc0, 0xc1, 0xc2}:
            return int.from_bytes(raw[at+5:at+7], 'big'), int.from_bytes(raw[at+3:at+5], 'big')
        assert marker != 0xda, 'Sharing JPEG has no dimensions'
        at += size
    raise AssertionError('Sharing JPEG has no dimensions')


def verify_card(root):
    record = json.loads((root/CARD_RECORD).read_bytes())
    for key in ('image', 'source'):
        path = record[key]
        assert path.startswith('assets/brand/') and '..' not in path.split('/') and '\\' not in path
        raw = (root/path).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == record['sha256' if key == 'image' else 'source_sha256']
    raw = (root/record['image']).read_bytes()
    assert jpeg_dimensions(raw) == (record['width'], record['height']) == (1200, 630)
    assert len(raw) < 250_000
    assert record['alt'] and len(record['alt']) <= 420
    return record


def publish(site):
    record = verify_card(site.output)
    paths = sorted(path for path in site.discovery_pages if indexable(path))
    urls = sorted({canonical_url(path) for path in paths})
    assert len(urls) == len(paths) and len(urls) <= 50_000
    document = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for url in urls:
        ET.SubElement(ET.SubElement(document, 'url'), 'loc').text = url
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'+ET.tostring(document, encoding='unicode')+'\n'
    assert len(xml.encode('utf8')) < 50_000_000
    site.write('sitemap.xml', xml)
    return dict(pages=len(site.discovery_pages), sitemap_urls=len(urls),
                preview_image=record['image'], preview_sha256=record['sha256'])


def verify(root, pages):
    record = verify_card(root)
    image_url = BASE_URL+record['image']+'?v='+record['sha256'][:12]
    for path, page in pages.items():
        assert page.canonicals == ([] if path == '404.html' else [canonical_url(path)]), (path, 'Canonical URL')
        assert len(page.metadata) == len(dict(page.metadata)), (path, 'Duplicate metadata')
        meta = dict(page.metadata)
        assert 1 <= len(meta['description']) <= MAX_DESCRIPTION, (path, 'Description')
        assert meta['og:description'] == meta['description']
        assert meta['og:title'] == ''.join(page.head_title)
        assert meta['og:url'] == canonical_url(path)
        assert meta['og:site_name'] == 'Komorebi' and meta['og:type'] == 'website'
        assert meta['og:image'] == image_url and meta['og:image:type'] == 'image/jpeg'
        assert (meta['og:image:width'], meta['og:image:height']) == ('1200', '630')
        assert meta['og:image:alt'] == meta['twitter:image:alt'] == record['alt']
        assert meta['twitter:card'] == 'summary_large_image'
        assert meta.get('robots') == (None if indexable(path) else 'noindex,follow'), (path, 'Indexing policy')
    document = ET.fromstring((root/'sitemap.xml').read_bytes())
    ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    assert document.tag == ns+'urlset'
    urls = [node.findtext(ns+'loc') for node in document]
    assert urls == sorted({canonical_url(p) for p in pages if indexable(p)})
    assert all([child.tag for child in node] == [ns+'loc'] for node in document), 'Do not invent modification dates'
    return dict(pages=len(pages), sitemap_urls=len(urls),
                preview_image=record['image'], preview_sha256=record['sha256'])
