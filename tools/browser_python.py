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
from playground_presets import PRESETS

EXAMPLES = {
    'packets': ('Reconstruct an operator', 'PACKETS', ['paper-i']),
    'refinement': ('Refine a signal', 'REFINEMENT', ['paper-ii', 'paper-v']),
    'recovery': ('Test recovery from a summary', 'RECOVERY', ['paper-iii', 'realization-boundaries']),
    'library': ('Use Komorebi Math', None, ['paper-i', 'paper-ii']),
}
EXAMPLES = {**{name: (spec['title'], None, spec.get('works', []))
              for name, spec in PRESETS.items() if spec.get('works')},
            **EXAMPLES,
            **{name: (spec['title'], None, [])
               for name, spec in PRESETS.items() if not spec.get('works')}}


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
    helper = (site.root/'website/python/komorebi_browser.py').read_bytes()
    (site.output/'downloads/komorebi_browser.py').parent.mkdir(parents=True, exist_ok=True)
    (site.output/'downloads/komorebi_browser.py').write_bytes(helper)
    archive, files, first_run = library_bundle(site.roots['math'], site.revisions['math'])
    (site.output/'downloads/komorebi-math-browser.zip').write_bytes(archive)
    (site.output/'downloads/komorebi-first-run.py').write_bytes(first_run)
    teaching = (site.root/'examples/komorebi_demonstrations.py').read_text(encoding='utf-8')
    record = dict(collection_revision=site.revision, library_revision=site.revisions['math'],
                  library_url='downloads/komorebi-math-browser.zip', library_sha256=sha(archive),
                  library_files=files, runtime_version=runtime['version'], packages=runtime['packages'],
                  plotly_js=runtime['plotly_js'], helper_url='downloads/komorebi_browser.py',
                  helper_sha256=sha(helper), examples={})
    body = '''<h1>Python playground</h1><p class="lede">Explore Komorebi's sequences, factorial normalizations and worked calculations. Change the inputs, inspect the graphs and follow the links to the written mathematics.</p>
<p>Python starts when you press Run. The first run downloads about 13 MB of runtime files. The library example also loads NumPy and Komorebi Math. Calculations run in your browser. Use Save draft to keep edited code in this browser, or download it as a Python file. Unsaved code and selected data may be lost when you leave or reload the page.</p>
<div id="python-picker" class="python-picker" hidden><label for="python-preset">Preload an example</label><select id="python-preset" aria-describedby="python-preset-help">
RESEARCH_OPTIONS<optgroup label="Worked examples"><option value="packets">Reconstruct an operator</option><option value="refinement">Refine a signal</option><option value="recovery">Test recovery from a summary</option></optgroup>
<optgroup label="Library preset"><option value="library">Komorebi Math with NumPy</option></optgroup>EXTRA_OPTIONS</select><p id="python-preset-help">Choose a preset to load its code, source links and expected output. Switching presets keeps your edits on this page. Python and any required libraries load when you press Run.</p></div>
<nav id="python-example-links" class="document-routes" aria-label="Choose a Python example">'''
    groups = dict.fromkeys(spec['group'] for spec in PRESETS.values())
    options = ''.join('<optgroup label="'+group+'">'+''.join('<option value="'+name+'">'+html.escape(spec['title'])+'</option>' for name, spec in PRESETS.items() if spec['group']==group)+'</optgroup>' for group in groups)
    research = '<optgroup label="Komorebi sequence research">'+''.join('<option value="'+name+'">'+html.escape(spec['title'])+'</option>' for name, spec in PRESETS.items() if spec.get('works'))+'</optgroup>'
    body = body.replace('RESEARCH_OPTIONS', research).replace('EXTRA_OPTIONS', options.replace(research, ''))
    body += ''.join('<a href="#'+key+'">'+html.escape(value[0])+'</a>' for key, value in EXAMPLES.items())+'</nav>'
    body += '''<noscript><p>Enable JavaScript to run Python here. The explanations, source and downloads below remain available.</p></noscript>
<p id="python-help">The editor is a plain text field. Tab moves to the next control. Run uses a fresh Python namespace. Stop ends the runtime. Reset restores the selected preset. Fixed expected values may need updating when you change an input.</p>
<div id="python-playground" data-worker="assets/python-worker.js" data-manifest="downloads/python-playground.json" data-results="assets/python-results.js?v=RESULTS_HASH" data-plotly="assets/python/plotly-4.1.1.min.js">
<details class="python-files"><summary>Upload data or open saved Python code</summary>
<label for="python-data-files">CSV or JSON data files</label><input id="python-data-files" type="file" accept=".csv,.json" multiple aria-describedby="python-upload-help">
<p id="python-upload-help">Up to 5 UTF-8 files, 2 MB each and 4 MB in total. The page reads them locally. It does not upload them to a server. Python receives their text in the <code>uploaded_files</code> dictionary. Try the Plot CSV or JSON data preset.</p><p id="python-upload-status" role="status">No data files selected.</p><button type="button" id="python-clear-files">Clear data files</button>
<p><a download href="downloads/sample-data.csv">Sample CSV</a> · <a download href="downloads/sample-data.json">Sample JSON</a></p>
<label for="python-code-file">Open a Python file in the selected editor</label><input id="python-code-file" type="file" accept=".py" aria-describedby="python-code-file-help"><p id="python-code-file-help">This replaces the selected editor's text. It does not run the code. Maximum 256 KB.</p></details>
<p id="python-status" role="status" aria-live="polite">Choose an example, then press Run.</p>'''
    for name, (title, doc, works) in EXAMPLES.items():
        source = PRESETS[name]['code'] if name in PRESETS else first_run.decode('utf-8') if name == 'library' else teaching_source(teaching, name)
        download = 'downloads/python-'+name+'.py'
        site.write(download, source)
        expected = ('Numerical reconstruction: [2.0, 3.0]\nExact coordinate change: (7/2, 3)\nExact inverse: (2, 3)\nPASS: first examples\n'
                    if name == 'library' else PRESETS[name]['expected'] if name in PRESETS else None)
        if doc:
            import re
            document = (site.root/('docs/demonstrations/'+doc+'.md')).read_text(encoding='utf-8')
            expected = re.search(r'<!-- expected-output -->\s*```text\n(.*?)\n```', document, re.S)[1]+'\n'
        record['examples'][name] = dict(url=download, sha256=sha(source.encode()), expected_output=expected, packages=PRESETS[name]['packages'] if name in PRESETS else ['numpy'] if name=='library' else [])
        body += '<section class="python-example" id="'+name+'"><h2>'+title+'</h2>'
        if doc:
            body += '<p><a href="collection/demonstrations/'+doc+'.html">Hand calculation, expected output and source connections</a></p>'
        elif name in PRESETS:
            body += '<p>'+html.escape(PRESETS[name]['description'])+'</p>'
            if PRESETS[name].get('guide'):
                body += '<p><a href="collection/demonstrations/SEQUENCE_SHAPES.html#'+PRESETS[name]['guide']+'">Definitions, exact values and how to read this plot</a> · <a href="math/sequences_oeis.html">Komorebi Math sequence API</a></p>'
            body += '<p><a href="#python-features-help">Plotting, data and saving guide</a></p>'
        else:
            body += '<p>This uses the published Komorebi Math library for packet reconstruction and exact rational coordinate changes. These two operations are tested here. The sequence research presets separately test reciprocal coefficients and Fubini row sums in their documented finite ranges. Optional backends and other operations remain outside that scope.</p><p><a href="collection/FIRST_RUN.html">Installation and expected output</a> · <a href="math/index.html">Komorebi Math guide</a></p>'
        body += '<nav class="document-routes" aria-label="'+title+' sources">' if works else ''
        for work in works:
            label = work.replace('paper-', 'Paper ').replace('realization-boundaries', 'Realization Boundaries').replace('iii', 'III').replace('ii', 'II')
            if work == 'paper-i': label = 'Paper I'
            if work == 'paper-v': label = 'Paper V'
            if work == 'paper-iv': label = 'Paper IV'
            if work == 'monographs-special-functions': label = 'Special Functions'
            base = 'collection/works/'+work+'.html'
            body += '<a href="'+base+'">'+label+'</a><a href="'+base+'#written-proofs">'+label+' proofs</a><a href="'+base+'#lean">'+label+' Lean coverage</a><a href="'+base+'#code">'+label+' code</a>'
            if work.startswith('paper-'): body += '<a href="claims.html#'+work+'">'+label+' claims</a>'
        body += ('</nav>' if works else '')+'<label for="code-'+name+'">Python code: '+title+'</label><textarea id="code-'+name+'" class="python-code" spellcheck="false" autocapitalize="off" autocomplete="off" aria-describedby="python-help" rows="14">'+html.escape(source)+'</textarea>'
        body += '<div class="python-actions"><button type="button" data-run="'+name+'">Run '+({'packets':'packet reconstruction','refinement':'signal refinement','recovery':'recovery check','library':'Komorebi Math','plot-2d':'2D plot','surface-3d':'3D surface','curve-3d':'3D curve','matplotlib':'Matplotlib','symbolic':'SymPy','scientific':'SciPy','data':'data plot'}.get(name,PRESETS.get(name, {}).get('run_label',title)))+'</button><button type="button" data-reset="'+name+'">Reset code</button><a download href="'+download+'">Download original code</a><a href="#python-output-title">Jump to results</a><button type="button" data-download-code="'+name+'">Download edited code</button></div><div class="python-actions"><button type="button" data-save="'+name+'">Save draft</button><button type="button" data-restore="'+name+'">Restore draft</button><button type="button" data-forget="'+name+'">Delete saved draft</button></div>'
        body += '<details class="python-expected"><summary>Expected output for the published preset</summary><pre>'+html.escape(expected)+'</pre><p>This is the original example\'s output. Your edits may change it.</p></details></section>'
        site.search.append(dict(title='Run Python: '+title,group='Collection',kind='Code',work_ids=works,url='playground.html#'+name,text='Python browser playground editable runnable example NumPy Komorebi Math '+title))
    body += '''<div class="python-results"><h2 id="python-output-title">Output</h2><button type="button" id="python-stop" disabled>Stop Python</button>
<div class="python-actions"><button type="button" id="python-download-output" disabled>Download output</button><button type="button" id="python-download-report" disabled>Download run report</button><a href="#python-picker">Choose another preset</a></div><div id="python-figures" aria-label="Figures and exported files"></div><pre id="python-output" role="region" aria-labelledby="python-output-title" tabindex="0">Run an example to see its output here.</pre>
<h3 id="python-error-title">Errors</h3><pre id="python-error" role="region" aria-labelledby="python-error-title" tabindex="0">None.</pre></div></div>
<details id="python-features-help"><summary>Plotting, data and saving guide</summary>
<p>Matplotlib figures appear as downloadable PNGs. Use <code>plt.show()</code> or <code>show_matplotlib(fig, description="...")</code>. Interactive plots use <code>from komorebi_browser import show_plot</code> and Plotly-style trace dictionaries. Supported traces are scatter, bar, heatmap, surface and scatter3d. The playground supplies this helper. It is separate from the Komorebi Math package.</p>
<p>Use <code>show_plot(data, layout, description="...")</code> to label a figure and its axes. Interactive plots have series checkboxes, an Enlarge plot button, zoom controls, image and data downloads, and a table of the first 100 samples. 3D views also have keyboard buttons for front, top and default views. The sequence family and factorial weights presets start with 2D views of the same data. If WebGL is unavailable, use those views, the table or the data downloads.</p>
<p>NumPy, Matplotlib, SymPy and SciPy load when selected presets or direct imports need them. Optional Komorebi backends remain outside the tested browser scope. Each run has a two minute limit, up to 50,000 samples per interactive figure, a 2 MB limit per figure or export, and an 8 MB combined figure and export limit.</p>
<p>Use <code>export_file("result.csv", text)</code> for CSV, JSON or text downloads. Saved drafts remain in this browser until you delete them. Restore draft is explicit. Download edited code saves the current editor as a .py file. The run report records the executed code, output, package versions, source revision and input-file checksums. It omits uploaded file contents. Downloaded plotting scripts can be reopened in this playground. The <a download href="downloads/komorebi_browser.py">browser helper source</a> documents the display functions.</p></details>
<aside class="notice"><h2>What a run tells you</h2><p>A matching result checks this example and its assertions. It does not establish a general theorem or run Lean. Edited code is labelled separately from the published example.</p><p><a href="collection/DEMONSTRATIONS.html">Demonstration scope</a> · <a href="collection/HAND_WORKED_EXAMPLES.html">More worked examples</a> · <a href="read/demonstrations.html">Complete teaching program</a></p></aside>
<details><summary>Runtime, library revision and source records</summary><p>Pyodide '''+runtime['version']+', Python '+runtime['python']+', NumPy '+runtime['packages']['numpy']+'''. Matplotlib, SymPy and SciPy are available on demand. Interactive plotting uses Plotly.js '''+runtime['plotly_js']+'''. These files are served by this site.</p><p><a href="downloads/python-playground.json">Example checksums and pinned library file list</a> · <a href="assets/python/SOURCE.json">Runtime sources and checksums</a> · <a href="assets/python/LICENSE">Runtime licenses</a> · <a href="assets/python/PLOTLY-LICENSE">Plotly license</a> · <a download href="downloads/komorebi-math-browser.zip">Pinned library source ZIP with license</a></p></details>
<script type="module" src="assets/python-playground.js?v=PYTHON_JS_HASH"></script>'''
    site.write('downloads/sample-data.csv', 'x,y\n0,1\n1,3\n2,5\n3,7\n')
    site.write('downloads/sample-data.json', json.dumps([{'x':i,'y':2*i+1} for i in range(4)],indent=2)+'\n')
    body = body.replace('RESULTS_HASH', sha((site.root/'website/assets/python-results.js').read_bytes())[:12])
    body = body.replace('PYTHON_JS_HASH', sha((site.root/'website/assets/python-playground.js').read_bytes())[:12])
    body = body.replace('data-worker="assets/python-worker.js"', 'data-worker="assets/python-worker.js?v='+sha((site.root/'website/assets/python-worker.js').read_bytes())[:12]+'"')
    site.write('downloads/python-playground.json', json.dumps(record, indent=2)+'\n')
    site.page('playground.html', 'Python playground', body)
