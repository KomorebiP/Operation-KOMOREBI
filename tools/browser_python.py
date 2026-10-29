"""Build a browser playground from unchanged teaching and library sources."""
import ast
import hashlib
import html
import io
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

EXAMPLES = {
    'packets': ('Reconstruct an operator', 'PACKETS', ['paper-i']),
    'refinement': ('Refine a signal', 'REFINEMENT', ['paper-ii', 'paper-v']),
    'recovery': ('Test recovery from a summary', 'RECOVERY', ['paper-iii', 'realization-boundaries']),
    'library': ('Use Komorebi Math', None, ['paper-i', 'paper-ii']),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def teaching_source(text, name):
    helpers = {'packets': ['require', 'multiply', 'apply', 'add_matrices', 'add_vectors'],
               'refinement': ['require', 'add_vectors'],
               'recovery': ['require', 'multiply', 'apply']}
    nodes = {n.name: n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)}
    return '# Edit this example, then press Run. Reset restores the published version.\n\n' + '\n\n\n'.join(
        ast.get_source_segment(text, nodes[n]) for n in helpers[name]+[name]) + '\n\n\nprint('+name+'())\n'


def library_bundle(root, revision):
    """Only include files whose bytes match the pinned Git tree."""
    listing = subprocess.check_output(['git', '-C', str(root), 'ls-tree', '-rz', revision,
                                      '--', 'src/komorebi_math', 'LICENSE.md', 'examples/first_run.py'])
    files = []
    output = io.BytesIO()
    example = None
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for row in listing.split(b'\0'):
            if not row:
                continue
            meta, raw_path = row.split(b'\t', 1)
            mode, kind, expected = meta.decode().split()
            path = raw_path.decode()
            if mode not in {'100644', '100755'} or kind != 'blob':
                raise ValueError('Unexpected library entry: '+path)
            raw = (root/path).read_bytes()
            blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            if blob != expected:
                raise ValueError('Library differs from pinned source: '+path)
            if path == 'examples/first_run.py':
                example = raw
                continue
            name = path.removeprefix('src/')
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, raw)
            files.append(dict(path=path, archive_path=name, git_blob_sha1=blob, sha256=sha(raw)))
    if not example or not files:
        raise ValueError('Missing pinned library or introductory example')
    return output.getvalue(), files, example


def build(site, runtime_root):
    from fetch_python_runtime import verify
    runtime = verify(runtime_root)
    shutil.copytree(runtime_root, site.output/'assets/python')
    site.write('assets/python/SOURCE.json', json.dumps(runtime, indent=2)+'\n')
    archive, files, first_run = library_bundle(site.roots['math'], site.revisions['math'])
    (site.output/'downloads/komorebi-math-browser.zip').write_bytes(archive)
    (site.output/'downloads/komorebi-first-run.py').write_bytes(first_run)
    teaching = (site.root/'examples/komorebi_demonstrations.py').read_text(encoding='utf-8')
    record = dict(collection_revision=site.revision, library_revision=site.revisions['math'],
                  library_url='downloads/komorebi-math-browser.zip', library_sha256=sha(archive),
                  library_files=files, runtime_version=runtime['version'], examples={})
    body = '''<h1>Python playground</h1><p class="lede">Run a small calculation, change the code and compare the result with its written explanation.</p>
<p>Python starts when you press Run. The first run downloads about 13 MB of runtime files. The library example also loads NumPy and Komorebi Math. Calculations run in your browser. Your edits are kept only on this page until you leave or reset it.</p>
<nav class="document-routes" aria-label="Choose a Python example">'''
    body += ''.join('<a href="#'+key+'">'+html.escape(value[0])+'</a>' for key, value in EXAMPLES.items())+'</nav>'
    body += '''<noscript><p>Enable JavaScript to run Python here. The explanations, source and downloads below remain available.</p></noscript>
<p id="python-help">Use the example links above to choose a starting point. The editor is a plain text field. Tab moves to the next control. Run uses a fresh Python namespace. Stop ends the runtime. Reset also restores the selected code. Fixed expected values may need updating when you change an input.</p>
<div id="python-playground" data-worker="assets/python-worker.js" data-manifest="downloads/python-playground.json">
<p id="python-status" role="status" aria-live="polite">Choose an example, then press Run.</p>'''
    for name, (title, doc, works) in EXAMPLES.items():
        source = first_run.decode('utf-8') if name == 'library' else teaching_source(teaching, name)
        download = 'downloads/python-'+name+'.py'
        site.write(download, source)
        expected = ('Numerical reconstruction: [2.0, 3.0]\nExact coordinate change: (7/2, 3)\nExact inverse: (2, 3)\nPASS: first examples\n'
                    if name == 'library' else None)
        if doc:
            import re
            document = (site.root/('docs/demonstrations/'+doc+'.md')).read_text(encoding='utf-8')
            expected = re.search(r'<!-- expected-output -->\s*```text\n(.*?)\n```', document, re.S)[1]+'\n'
        record['examples'][name] = dict(url=download, sha256=sha(source.encode()), expected_output=expected)
        body += '<section class="python-example" id="'+name+'"><h2>'+title+'</h2>'
        if doc:
            body += '<p><a href="collection/demonstrations/'+doc+'.html">Hand calculation, expected output and source connections</a></p>'
        else:
            body += '<p>This uses the published Komorebi Math library for packet reconstruction and exact rational coordinate changes. These two operations are the tested browser scope. Optional backends and the rest of the library have not been qualified here.</p><p><a href="collection/FIRST_RUN.html">Installation and expected output</a> · <a href="math/index.html">Komorebi Math guide</a></p>'
        body += '<nav class="document-routes" aria-label="'+title+' sources">'
        for work in works:
            label = work.replace('paper-', 'Paper ').replace('realization-boundaries', 'Realization Boundaries').replace('iii', 'III').replace('ii', 'II')
            if work == 'paper-i': label = 'Paper I'
            if work == 'paper-v': label = 'Paper V'
            base = 'collection/works/'+work+'.html'
            body += '<a href="'+base+'">'+label+'</a><a href="'+base+'#written-proofs">'+label+' proofs</a><a href="'+base+'#lean">'+label+' Lean coverage</a><a href="'+base+'#code">'+label+' code</a>'
            if work.startswith('paper-'): body += '<a href="claims.html#'+work+'">'+label+' claims</a>'
        body += '</nav><label for="code-'+name+'">Python code: '+title+'</label><textarea id="code-'+name+'" class="python-code" spellcheck="false" autocapitalize="off" autocomplete="off" aria-describedby="python-help" rows="14">'+html.escape(source)+'</textarea>'
        body += '<div class="python-actions"><button type="button" data-run="'+name+'">Run '+({'packets':'packet reconstruction','refinement':'signal refinement','recovery':'recovery check','library':'Komorebi Math'}[name])+'</button><button type="button" data-reset="'+name+'">Reset code</button><a download href="'+download+'">Download original code</a></div></section>'
        site.search.append(dict(title='Run Python: '+title,group='Collection',kind='Code',work_ids=works,url='playground.html#'+name,text='Python browser playground editable runnable example NumPy Komorebi Math '+title))
    body += '''<div class="python-results"><h2 id="python-output-title">Output</h2><button type="button" id="python-stop" disabled>Stop Python</button>
<pre id="python-output" role="region" aria-labelledby="python-output-title" tabindex="0">Run an example to see its output here.</pre>
<h3 id="python-error-title">Errors</h3><pre id="python-error" role="region" aria-labelledby="python-error-title" tabindex="0">None.</pre></div></div>
<aside class="notice"><h2>What a run tells you</h2><p>A matching result checks this example and its assertions. It does not establish a general theorem or run Lean. Edited code is labelled separately from the published example.</p><p><a href="collection/DEMONSTRATIONS.html">Demonstration scope</a> · <a href="collection/HAND_WORKED_EXAMPLES.html">More worked examples</a> · <a href="read/demonstrations.html">Complete teaching program</a></p></aside>
<details><summary>Runtime, library revision and source records</summary><p>Pyodide '''+runtime['version']+', Python '+runtime['python']+', NumPy '+runtime['packages']['numpy']+'''. These files are served by this site.</p><p><a href="downloads/python-playground.json">Example checksums and pinned library file list</a> · <a href="assets/python/SOURCE.json">Runtime sources and checksums</a> · <a href="assets/python/LICENSE">Runtime licenses</a> · <a download href="downloads/komorebi-math-browser.zip">Pinned library source ZIP with license</a></p></details>
<script type="module" src="assets/python-playground.js?v=PYTHON_JS_HASH"></script>'''
    body = body.replace('PYTHON_JS_HASH', sha((site.root/'website/assets/python-playground.js').read_bytes())[:12])
    body = body.replace('data-worker="assets/python-worker.js"', 'data-worker="assets/python-worker.js?v='+sha((site.root/'website/assets/python-worker.js').read_bytes())[:12]+'"')
    site.write('downloads/python-playground.json', json.dumps(record, indent=2)+'\n')
    site.page('playground.html', 'Python playground', body)
