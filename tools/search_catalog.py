"""Static full-text search with compact postings and per-result previews."""
import collections
import hashlib
import json
from pathlib import Path
import re
import unicodedata

SCHEMA = 2
TERMS_PER_PART = 256
DETAIL_FIELDS = ('text', 'preview', 'preview_parts', 'math_preview')
SYMBOLS = dict(zip('αβγρωηδℓ', ('alpha', 'beta', 'gamma', 'rho', 'omega', 'eta', 'delta', 'ell')))


def normalized(value):
    """Match reader.js: symbol aliases, NFKD, marks removed, letters and numbers."""
    value = re.sub('[αβγρωηδℓ]', lambda m: ' '+SYMBOLS[m[0]]+' ', value)
    value = ''.join(c for c in unicodedata.normalize('NFKD', value)
                    if not unicodedata.category(c).startswith('M')).lower()
    return re.sub(r'[\W_]+', ' ', value).strip()


def packed(value):
    return (json.dumps(value, ensure_ascii=False, separators=(',', ':'))+'\n').encode('utf8')


def base36(value):
    if not value:
        return '0'
    result = ''
    while value:
        value, digit = divmod(value, 36)
        result = '0123456789abcdefghijklmnopqrstuvwxyz'[digit]+result
    return result


def encode_ids(ids):
    previous = 0
    encoded = []
    for identifier in ids:
        encoded.append(base36(identifier-previous))
        previous = identifier
    return '.'.join(encoded)


def decode_ids(value, total):
    result = []
    previous = 0
    for token in value.split('.'):
        if not re.fullmatch('[0-9a-z]+', token):
            raise ValueError('Invalid search posting')
        identifier = previous+int(token, 36)
        if identifier >= total or result and identifier <= previous:
            raise ValueError('Invalid search posting order')
        result.append(identifier)
        previous = identifier
    return result


def render_fields(row):
    # A rich, authored preview already supplies the displayed excerpt.
    return {key: row[key] for key in DETAIL_FIELDS if key in row
            and not (key == 'text' and row.get('preview'))}


def row_signature(metadata, terms, detail):
    return hashlib.sha256(packed([metadata, sorted(terms), detail])).hexdigest()


def publish(site):
    if not re.fullmatch(r'[A-Za-z0-9._-]+', site.revision):
        raise ValueError('Invalid search revision')
    prefix = 'search/'+site.revision+'/'
    rows = site.search
    groups = sorted({r['group'] for r in rows})
    kinds = sorted({r['kind'] for r in rows})
    works = sorted({w for r in rows for w in r['work_ids']})
    group_ids = {v: i for i, v in enumerate(groups)}
    kind_ids = {v: i for i, v in enumerate(kinds)}
    work_ids = {v: i for i, v in enumerate(works)}
    metadata = []
    postings = collections.defaultdict(list)
    signatures = hashlib.sha256()
    detail_bytes = 0

    def write(path, value):
        raw = packed(value)
        target = site.output/path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        return len(raw)

    for identifier, row in enumerate(rows):
        meta = [row['title'], row['url'], group_ids[row['group']], kind_ids[row['kind']],
                [work_ids[w] for w in row['work_ids']], int(bool(row.get('visual_guide')))]
        metadata.append(meta)
        terms = set(normalized(row['title']+' '+row['text']).split())
        for term in terms:
            postings[term].append(identifier)
        detail = render_fields(row)
        detail_bytes += write(prefix+'entries/'+str(identifier)+'.json', detail)
        signatures.update(row_signature(meta, terms, detail).encode('ascii'))

    metadata_bytes = write(prefix+'metadata.json', dict(groups=groups, kinds=kinds, works=works, rows=metadata))
    terms = sorted(postings)
    lexicon_bytes = write(prefix+'terms.json', terms)
    posting_bytes = 0
    part_sizes = []
    for first in range(0, len(terms), TERMS_PER_PART):
        part = {term: encode_ids(postings[term]) for term in terms[first:first+TERMS_PER_PART]}
        size = write(prefix+'postings/'+str(first//TERMS_PER_PART)+'.json', part)
        posting_bytes += size
        part_sizes.append(size)
    result = dict(entries=len(rows), terms=len(terms), metadata_bytes=metadata_bytes,
                  lexicon_bytes=lexicon_bytes, posting_bytes=posting_bytes,
                  max_posting_part_bytes=max(part_sizes, default=0), detail_bytes=detail_bytes)
    manifest = dict(schema=SCHEMA, source_revision=site.revision, entries=len(rows),
                    metadata=prefix+'metadata.json', lexicon=prefix+'terms.json',
                    postings=prefix+'postings/', details=prefix+'entries/',
                    terms_per_part=TERMS_PER_PART, signatures_sha256=signatures.hexdigest(), sizes=result)
    site.write('search-index.json', packed(manifest).decode('utf8'))
    return result


def metadata_rows(root, manifest=None):
    root = Path(root)
    manifest = manifest if manifest is not None else json.loads((root/'search-index.json').read_bytes())
    # Older static fixtures remain readable by the site checkers.
    if isinstance(manifest, list):
        return manifest
    if manifest.get('schema') != SCHEMA:
        raise ValueError('Unsupported search catalogue')
    data = json.loads((root/manifest['metadata']).read_bytes())
    if len(data['rows']) != manifest['entries']:
        raise ValueError('Search catalogue count mismatch')
    return [dict(id=i, title=r[0], url=r[1], group=data['groups'][r[2]],
                 kind=data['kinds'][r[3]], work_ids=[data['works'][w] for w in r[4]],
                 **({'visual_guide': True} if r[5] else {})) for i, r in enumerate(data['rows'])]


def verify(root, revision):
    root = Path(root)
    manifest = json.loads((root/'search-index.json').read_bytes())
    assert manifest['schema'] == SCHEMA and manifest['source_revision'] == revision
    prefix = 'search/'+revision+'/'
    assert manifest['metadata'] == prefix+'metadata.json'
    assert manifest['lexicon'] == prefix+'terms.json'
    assert manifest['postings'] == prefix+'postings/' and manifest['details'] == prefix+'entries/'
    assert manifest['terms_per_part'] == TERMS_PER_PART
    metadata = json.loads((root/manifest['metadata']).read_bytes())
    terms = json.loads((root/manifest['lexicon']).read_bytes())
    assert terms == sorted(set(terms))
    by_row = [set() for _ in metadata['rows']]
    posting_bytes = 0
    part_sizes = []
    for first in range(0, len(terms), TERMS_PER_PART):
        raw = (root/(manifest['postings']+str(first//TERMS_PER_PART)+'.json')).read_bytes()
        part = json.loads(raw)
        assert set(part) == set(terms[first:first+TERMS_PER_PART])
        posting_bytes += len(raw)
        part_sizes.append(len(raw))
        for term, encoded in part.items():
            for identifier in decode_ids(encoded, manifest['entries']):
                by_row[identifier].add(term)
    signatures = hashlib.sha256()
    detail_bytes = 0
    rows = metadata_rows(root, manifest)
    for i, row in enumerate(rows):
        raw = (root/(manifest['details']+str(i)+'.json')).read_bytes()
        detail = json.loads(raw)
        assert set(detail) <= set(DETAIL_FIELDS)
        assert isinstance(detail.get('preview') or detail.get('text'), str)
        signatures.update(row_signature(metadata['rows'][i], by_row[i], detail).encode('ascii'))
        detail_bytes += len(raw)
    assert signatures.hexdigest() == manifest['signatures_sha256']
    expected = dict(entries=len(rows), terms=len(terms), metadata_bytes=(root/manifest['metadata']).stat().st_size,
                    lexicon_bytes=(root/manifest['lexicon']).stat().st_size, posting_bytes=posting_bytes,
                    max_posting_part_bytes=max(part_sizes, default=0), detail_bytes=detail_bytes)
    assert expected == manifest['sizes']
    # Search should never quietly return to loading the complete source text.
    assert expected['metadata_bytes'] < 4*1024*1024
    assert expected['lexicon_bytes'] < 1024*1024
    assert expected['max_posting_part_bytes'] < 512*1024
    return expected
