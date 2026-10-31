"""Publish and verify the standalone factorial-lane demonstration."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

PROGRAM = 'examples/factorial_lanes.py'
MANUSCRIPT = 'docs/demonstrations/FACTORIAL_LANES.md'
READER = 'read/factorial-lanes.html'
PREFIX = 'downloads/factorial-lanes/'
DOWNLOAD = PREFIX+'factorial_lanes.py'
RECORD = PREFIX+'source-record.json'
ARCHIVE = PREFIX+'source-and-results.zip'
TABLES = ('lane-products.csv', 'coefficients.csv', 'results.json')


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def publish(site) -> dict:
    program = (site.root/PROGRAM).read_bytes()
    manuscript = (site.root/MANUSCRIPT).read_bytes()
    contents = {PROGRAM: program, MANUSCRIPT: manuscript}
    (site.output/DOWNLOAD).parent.mkdir(parents=True, exist_ok=True)
    (site.output/DOWNLOAD).write_bytes(program)
    exports = []
    for name in TABLES:
        source = 'verification/factorial-lanes/'+name
        raw = (site.root/source).read_bytes()
        contents[source] = raw
        url = PREFIX+name
        (site.output/url).write_bytes(raw)
        exports.append(dict(source=source, url=url, sha256=sha(raw), size=len(raw)))
    contents['LICENSE.md'] = (site.root/'LICENSE.md').read_bytes()
    with zipfile.ZipFile(site.output/ARCHIVE, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for path, raw in contents.items():
            bundle.writestr(path, raw)

    record = dict(
        title='Factorial lanes: exact worked derivation',
        collection_revision=site.revision,
        program_source=PROGRAM,
        program_sha256=sha(program),
        program_size=len(program),
        manuscript_source=MANUSCRIPT,
        manuscript_sha256=sha(manuscript),
        reader_url=READER,
        manuscript_url='collection/demonstrations/FACTORIAL_LANES.html',
        download_url=DOWNLOAD,
        tables=exports,
        archive_url=ARCHIVE,
        archive_sha256=sha((site.output/ARCHIVE).read_bytes()),
        archive_files=[dict(source=source, sha256=sha(raw)) for source,raw in contents.items()],
        scope='Exact formal identities and 225 finite arithmetic checks; '
              'not a Lean replay or a general conjecture certificate.'
    )
    site.write(RECORD, json.dumps(record, indent=2)+'\n')

    from reader_documents import source_lines
    body = (
        '<h1>Factorial lanes / exact Python program</h1>'
        '<p>Ten step-factorial lanes, hypergeometric coordinates, '
        'factorial normalization, reciprocal inversion, five-adic checks '
        'and counterexamples. Python 3.10 or later, standard library only.</p>'
        '<p><a class="button" href="../collection/demonstrations/FACTORIAL_LANES.html">'
        'Read the complete hand derivation</a> '
        '<a download href="../'+DOWNLOAD+'">Download Python</a> · '
        '<a href="../'+ARCHIVE+'">Source and exact results ZIP</a> · '
        '<a href="../'+RECORD+'">Source identities</a></p>'
        '<p>Checked data: '
        + ' · '.join('<a href="../'+item['url']+'">'+item['url'].split('/')[-1]+'</a>'
                   for item in exports) + '</p>'
        '<p>Run <code>python -B factorial_lanes.py</code>. '
        'Add <code>--output factorial-results</code> to write exact CSV and JSON tables.</p>'
    )
    site.page(READER, 'Factorial lanes / exact Python program',
              body+source_lines(program.decode('utf-8')),
              'https://github.com/KomorebiP/Operation-KOMOREBI/blob/'
              +site.revision+'/'+PROGRAM)
    site.search.append(dict(
        title='Factorial lanes / exact Python checker',
        group='Collection', kind='Code', work_ids=['paper-iv', 'monographs-special-functions'],
        url=READER,
        text='factorial lanes hypergeometric Pochhammer residue packets '
             'ten lanes prime adic five-adic valuations normalized coefficients '
             'reciprocal transfer binomial convolution differences source program'))
    return record


def verify_site(root: Path, pages: dict) -> int:
    record = json.loads((root/RECORD).read_bytes())
    assert record['reader_url'] in pages
    assert record['manuscript_url'] in pages
    raw = (root/record['download_url']).read_bytes()
    assert len(raw) == record['program_size']
    assert sha(raw) == record['program_sha256']
    for item in record['tables']:
        exported = (root/item['url']).read_bytes()
        assert len(exported) == item['size'] and sha(exported) == item['sha256']
    archive = root/record['archive_url']
    assert sha(archive.read_bytes()) == record['archive_sha256']
    with zipfile.ZipFile(archive) as bundle:
        assert set(bundle.namelist()) == {item['source'] for item in record['archive_files']}
        for item in record['archive_files']:
            assert sha(bundle.read(item['source'])) == item['sha256']
    from reader_documents import source_lines
    reader_html = (root/record['reader_url']).read_text(encoding='utf-8')
    assert source_lines(raw.decode('utf-8')) in reader_html
    assert 'FACTORIAL_LANES.html' in reader_html
    assert record['scope'].startswith('Exact formal identities')
    return 1
