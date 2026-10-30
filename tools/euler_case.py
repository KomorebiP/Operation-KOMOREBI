"""Publish the source-bound extended Euler example without executing its code."""
import hashlib
import json
from pathlib import PurePosixPath
import zipfile

RECORD='manifests/euler-packets-worked-example-2026-10-29.json'
PREFIX='downloads/euler-packets/'
READER='read/euler-packets.html'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked_path(path):
    value=PurePosixPath(path)
    if not value.parts or value.as_posix()!=path or value.is_absolute() or '..' in value.parts or '\\' in path or ':' in path or '\0' in path:
        raise ValueError('Unsafe Euler source path: '+path)
    return path


def publish(site):
    record_path=site.root/RECORD
    record=json.loads(record_path.read_bytes())
    binding=site.assessments['euler-signal-bridge']['worked_example']
    if binding['record']!=RECORD or binding['sha256']!=sha(record_path.read_bytes()):
        raise ValueError('Euler publication differs from its registered assessment')
    contents={}
    for entry in record['files']:
        path=checked_path(entry['path'])
        raw=(site.root/path).read_bytes()
        if sha(raw)!=entry['sha256']:
            raise ValueError('Euler worked source differs from its publication record: '+path)
        if path in contents:
            raise ValueError('Duplicate Euler source: '+path)
        contents[path]=raw
    for run_path in record['accepted_runs']:
        run=json.loads(contents[run_path])
        if run['run']['status']!='completed' or run['run']['exit_status']!=0:
            raise ValueError('Euler computation did not complete: '+run_path)
        for entry in run['input_artifacts']:
            if entry['path'] not in contents or sha(contents[entry['path']])!=entry['sha256'] or entry['sha256_after']!=entry['sha256']:
                raise ValueError('Euler run input differs: '+entry['path'])
        for entry in run['outputs']:
            if entry['path'] not in contents or sha(contents[entry['path']])!=entry['sha256']:
                raise ValueError('Euler run output differs: '+entry['path'])
    downloads={
        'euler_packets.py':'examples/euler_packets.py',
        'results.json':'verification/euler-packets/run-005/results.json',
        'euler-coefficients.csv':'verification/euler-packets/run-005/euler-coefficients.csv',
        'power-polynomials.csv':'verification/euler-packets/run-005/power-polynomials.csv',
        'local-reconstruction.csv':'verification/euler-packets/run-005/local-reconstruction.csv',
        'coefficient-matrices.csv':'verification/euler-packets/run-005/coefficient-matrices.csv',
        'congruence-ladders.csv':'verification/euler-packets/run-005/congruence-ladders.csv',
        'fibonacci-transfer.csv':'verification/euler-packets/run-005/fibonacci-transfer.csv',
        'fibonacci-precision.csv':'verification/euler-packets/run-005/fibonacci-precision.csv',
        'polynomial-calculus.csv':'verification/euler-packets/run-005/polynomial-calculus.csv',
        'library-comparison.json':'verification/euler-packets/cross-check-005/results.json',
    }
    output=site.output/PREFIX
    output.mkdir(parents=True,exist_ok=True)
    published=[]
    for name,source in downloads.items():
        raw=contents[source]
        (output/name).write_bytes(raw)
        published.append(dict(url=PREFIX+name,source=source,sha256=sha(raw),size=len(raw)))
    members={**contents,RECORD:record_path.read_bytes(),'LICENSE.md':(site.root/'LICENSE.md').read_bytes()}
    archive=output/'source-and-checks.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as bundle:
        for path,raw in members.items():
            bundle.writestr(path,raw)
    source=dict(title=record['title'],source_revision=site.revision,
                record=RECORD,record_sha256=sha(record_path.read_bytes()),
                manuscript_url='collection/demonstrations/EULER_PACKETS.html',
                reader_url=READER,downloads=published,
                archive_url=PREFIX+'source-and-checks.zip',archive_sha256=sha(archive.read_bytes()),
                archive_members=[dict(path=path,sha256=sha(raw)) for path,raw in members.items()],
                scope=record['scope'])
    site.write(PREFIX+'source-record.json',json.dumps(source,indent=2)+'\n')
    from reader_documents import source_lines
    body=('<h1>Exact program for the Euler worked example</h1>'
          '<p>Python 3.10 or later and its standard library. Exact integers and fractions.</p>'
          '<p><a class="button" href="../collection/demonstrations/EULER_PACKETS.html">Read the full derivation</a> '
          '<a href="../'+PREFIX+'euler_packets.py" download>Download Python</a> · '
          '<a href="../'+PREFIX+'source-and-checks.zip">Source and results bundle</a> · '
          '<a href="../'+PREFIX+'source-record.json">Source identities</a></p>'
          '<p>Run <code>python -B euler_packets.py</code>. Add <code>--output my-results</code> to save exact tables.</p>')
    body+=source_lines(contents['examples/euler_packets.py'].decode('utf-8'))
    site.page(READER,'Exact program for the Euler worked example',body,
              'https://github.com/KomorebiP/Operation-KOMOREBI/blob/'+site.revision+'/examples/euler_packets.py')
    site.search.append(dict(title='Euler packets, polynomials and residuals / exact program',
        group='Collection',kind='Code',url=READER,work_ids=record['work_ids'],
        text='Euler secant A000364 A211212 quartic packets Schur complement reciprocal polynomials Fibonacci polynomial connection companion defect sequence transfer infinite coefficient matrices Pascal Toeplitz base changes supercongruences congruential addresses CRT odd-prime dyadic local coordinates Bernoulli sharp precision prime residual exact standalone Python'))
    return source


def verify_site(root,pages):
    path=root/(PREFIX+'source-record.json')
    if not path.is_file():
        return 0
    source=json.loads(path.read_bytes())
    assert source['reader_url'] in pages and source['manuscript_url'] in pages
    for entry in source['downloads']:
        raw=(root/checked_path(entry['url'])).read_bytes()
        assert len(raw)==entry['size'] and sha(raw)==entry['sha256']
    archive=root/checked_path(source['archive_url'])
    assert sha(archive.read_bytes())==source['archive_sha256']
    with zipfile.ZipFile(archive) as bundle:
        assert len(bundle.namelist())==len(set(bundle.namelist()))
        assert set(bundle.namelist())=={e['path'] for e in source['archive_members']}
        for entry in source['archive_members']:
            assert sha(bundle.read(checked_path(entry['path'])))==entry['sha256']
        assert sha(bundle.read(source['record']))==source['record_sha256']
        record=json.loads(bundle.read(source['record']))
        assert all(sha(bundle.read(e['path']))==e['sha256'] for e in record['files'])
    return 1
