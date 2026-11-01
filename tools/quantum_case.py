"""Publish source-bound finite quantum teaching records and verify their bytes."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import zipfile

PROGRAM = 'examples/quantum_phase_measurement.py'
MANUSCRIPT = 'docs/demonstrations/QUANTUM_PHASE_MEASUREMENT.md'
MANUSCRIPT_URL = 'collection/demonstrations/QUANTUM_PHASE_MEASUREMENT.html'
READER = 'read/quantum-phase-measurement.html'
PREFIX = 'downloads/quantum-phase-measurement/'
RECORD = PREFIX+'source-record.json'
FILES = ('measurement-settings.csv', 'partial-dephasing.csv', 'results.json',
         'measurement-comparison.svg', 'amplitude-damping.csv',
         'arithmetic-phase.csv', 'syndrome-recovery.csv')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load_program(root):
    name = 'quantum_phase_measurement_publication'
    spec = importlib.util.spec_from_file_location(name, root/PROGRAM)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def publish(site):
    sources = {p: (site.root/p).read_bytes()
               for p in (PROGRAM, MANUSCRIPT, 'LICENSE.md')}
    target = site.output/PREFIX
    target.mkdir(parents=True, exist_ok=True)
    download = PREFIX+'quantum_phase_measurement.py'
    (site.output/download).write_bytes(sources[PROGRAM])
    tables = []
    for name in FILES:
        path = 'verification/quantum-phase-measurement/'+name
        raw = (site.root/path).read_bytes()
        sources[path] = raw
        (target/name).write_bytes(raw)
        tables.append(dict(url=PREFIX+name, sha256=digest(raw), size=len(raw)))
    archive = PREFIX+'source-and-results.zip'
    with zipfile.ZipFile(site.output/archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for path, raw in sorted(sources.items()):
            info = zipfile.ZipInfo(path, (2026, 11, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, raw)
    record = dict(collection_revision=site.revision, program_source=PROGRAM,
                  program_sha256=digest(sources[PROGRAM]),
                  program_size=len(sources[PROGRAM]), manuscript_source=MANUSCRIPT,
                  manuscript_sha256=digest(sources[MANUSCRIPT]),
                  manuscript_url=MANUSCRIPT_URL, reader_url=READER,
                  download_url=download, tables=tables, archive_url=archive,
                  archive_sha256=digest((site.output/archive).read_bytes()),
                  archive_files=[dict(path=p, sha256=digest(raw))
                                 for p, raw in sorted(sources.items())],
                  scope='Exact finite teaching example; no sampling or Lean replay.')
    site.write(RECORD, json.dumps(record, indent=2)+'\n')
    from reader_documents import source_lines
    body = ('<h1>Quantum phase, measurement, and information loss / exact Python</h1>'
            '<p>Gaussian rational matrix arithmetic, three-setting tomography, '
            'partial dephasing, operation order, coherent records, and packet '
            'refinement, amplitude damping, modulus-12 arithmetic interference, '
            'and three-qubit syndrome recovery. Python 3.10 or later; standard library only.</p>'
            '<p><a class="button" href="../'+MANUSCRIPT_URL+'">Read the worked derivation</a> · '
            '<a download href="../'+download+'">Download Python</a> · '
            '<a href="../'+archive+'">Source and results ZIP</a> · '
            '<a href="../'+RECORD+'">Revision and source identities</a></p>'
            '<p>Exact generated records: '+
            ' · '.join('<a href="../'+t['url']+'">'+t['url'].split('/')[-1]+'</a>'
                       for t in tables)+'</p>'
            '<p>Run <code>python -B quantum_phase_measurement.py</code>. '
            'Add <code>--output quantum-results</code> to reproduce the records.</p>')
    site.page(READER, 'Quantum phase and measurement / exact Python',
              body+source_lines(sources[PROGRAM].decode('utf-8')),
              'https://github.com/KomorebiP/Operation-KOMOREBI/blob/'+site.revision+'/'+PROGRAM)
    site.search.append(dict(title='Quantum phase and measurement / exact Python',
                            group='Collection', kind='Code', work_ids=['paper-vii', 'monographs-quantum-and-circuits'],
                            url=READER, text='quantum phase dephasing coherence density matrix '
                            'tomography Born Kraus purity record CNOT parity packet recovery '
                            'Ramanujan Fourier modulus twelve amplitude damping syndrome bit flip'))
    return record


def verify_site(root: Path, pages: dict) -> int:
    record = json.loads((root/RECORD).read_bytes())
    assert record['reader_url'] in pages and record['manuscript_url'] in pages
    raw = (root/record['download_url']).read_bytes()
    assert len(raw) == record['program_size'] and digest(raw) == record['program_sha256']
    for item in record['tables']:
        content = (root/item['url']).read_bytes()
        assert len(content) == item['size'] and digest(content) == item['sha256']
    archive = root/record['archive_url']
    assert digest(archive.read_bytes()) == record['archive_sha256']
    with zipfile.ZipFile(archive) as bundle:
        assert set(bundle.namelist()) == {x['path'] for x in record['archive_files']}
        for item in record['archive_files']:
            assert digest(bundle.read(item['path'])) == item['sha256']
        assert digest(bundle.read(MANUSCRIPT)) == record['manuscript_sha256']
    from reader_documents import source_lines
    html = (root/READER).read_text(encoding='utf-8')
    assert source_lines(raw.decode('utf-8')) in html and MANUSCRIPT_URL in html
    if (root/'build-info.json').is_file():
        assert record['collection_revision'] == json.loads(
            (root/'build-info.json').read_bytes())['collection_revision']
    return 1
