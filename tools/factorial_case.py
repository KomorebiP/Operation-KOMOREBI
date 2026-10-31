"""Publish and verify the standalone factorial-lane demonstration."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

PROGRAM = 'examples/factorial_lanes.py'
MANUSCRIPT = 'docs/demonstrations/FACTORIAL_LANES.md'
READER = 'read/factorial-lanes.html'
DOWNLOAD = 'downloads/factorial-lanes/factorial_lanes.py'
RECORD = 'downloads/factorial-lanes/source-record.json'


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def publish(site) -> dict:
    program = (site.root/PROGRAM).read_bytes()
    manuscript = (site.root/MANUSCRIPT).read_bytes()
    # Both inputs are site-owned and published at the same immutable revision.
    (site.output/DOWNLOAD).parent.mkdir(parents=True, exist_ok=True)
    (site.output/DOWNLOAD).write_bytes(program)
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
        '<a href="../'+RECORD+'">Source identities</a></p>'
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
    from reader_documents import source_lines
    assert source_lines(raw.decode('utf-8')) in pages[record['reader_url']]
    assert 'FACTORIAL_LANES.html' in pages[record['reader_url']]
    assert record['scope'].startswith('Exact formal identities')
    return 1
