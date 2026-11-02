"""Build a portable source bundle and project-aware execution routes."""
import argparse
from collections import Counter
import hashlib
import html
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

from lean_runner import Collection, digest, safe_path

PAGE='lean/run.html'
FALLBACK_ROOT='papers/paper-v/current/source/complete/original_snapshot/formalization/lean'
OMIT_PARTS={'.lake','.git','build','node_modules','__pycache__'}
OMIT_SUFFIXES={'.olean','.ilean','.ir','.o','.a','.so','.dll','.exe','.pdf','.zip','.gz','.tar','.png','.jpg','.jpeg','.webp','.woff','.woff2'}
OUTPUT_PARTS={'verification','evidence','results','logs'}


def re_license(name):
    return name.upper().startswith(('LICENSE','LICENCE','COPYING','COPYRIGHT')) and PurePosixPath(name).suffix.lower() not in OMIT_SUFFIXES


def identity(path):
    return hashlib.sha256(path.encode()).hexdigest()[:16]


def action(site,page,path):
    return '<a href="'+site.rel(PAGE,page)+'?file='+identity(path)+'">Run with dependencies</a>'


def collect(root,revision):
    from lean_reader import selected_paths
    from readable_chapters import BOOKS
    from reader_documents import page_path
    registry=json.loads((root/'manifests/browse-resources.json').read_bytes())
    owned={};selected=[]
    for component in registry['components']:
        if component['id'] not in BOOKS:continue
        receipt=json.loads((root/'manifests/source-imports'/(component['id']+'.json')).read_bytes())
        for entry in receipt['files']:
            path=component['destination']+'/'+entry['path']
            owned[path]={**entry,'work':component['id'],'repository_path':path}
        selected.extend(selected_paths(component,owned))
    inputs={};projects={};sources=[]
    for path,entry in owned.items():
        parts=PurePosixPath(path).parts
        if ((path.endswith('.lean') and not OMIT_PARTS.intersection(parts)) or re_license(PurePosixPath(path).name)):
            inputs[path]=entry
    def add(path):
        if path not in owned:raise ValueError('Missing retained environment input: '+path)
        inputs[path]=owned[path]
    for path in sorted(selected):
        project=None
        for parent in PurePosixPath(path).parents:
            if any(str(parent)+'/'+name in owned for name in ('lakefile.lean','lakefile.toml')):
                project=str(parent);break
        if project and project not in projects:
            files=[]
            for candidate in owned:
                relative=candidate.removeprefix(project+'/')
                if relative==candidate or OMIT_PARTS.intersection(PurePosixPath(relative).parts) or PurePosixPath(relative).suffix.lower() in OMIT_SUFFIXES:continue
                if OUTPUT_PARTS.intersection(PurePosixPath(relative).parts) and not relative.endswith('.lean'):continue
                add(candidate);files.append(candidate)
            for name in ('lean-toolchain','lake-manifest.json'):
                add(project+'/'+name)
                if project+'/'+name not in files:files.append(project+'/'+name)
            projects[project]=dict(files=sorted(files))
        entry=owned[path]
        sources.append(dict(id=identity(path),path=path,work=entry['work'],label=BOOKS[entry['work']]['label'],sha256=entry['sha256'],
                            url=page_path(entry['work'],path),project=project))
    for name in ('lean-toolchain','lake-manifest.json'):add(FALLBACK_ROOT+'/'+name)
    return owned,dict(schema=1,source_revision=revision,sources=sources,inputs={
        p:{k:e[k] for k in ('work','sha256','git_blob_sha1','size','mode')} for p,e in sorted(inputs.items())},projects=projects)


def read_inputs(root,catalog,revision):
    paths=list(catalog['inputs']);raws={};missing=[]
    for path in paths:
        target=root/path
        if target.is_file() and digest(target.read_bytes())==catalog['inputs'][path]['sha256']:
            raws[path]=target.read_bytes()
        else:missing.append(path)
    if missing:
        args=['git','-c','gc.auto=0','-c','credential.helper=','-c','credential.interactive=false','cat-file','--batch']
        data=subprocess.check_output(args,cwd=root,input=''.join(catalog['inputs'][p]['git_blob_sha1']+'\n' for p in missing).encode(),
                                     env={**os.environ,'GIT_TERMINAL_PROMPT':'0','GIT_NO_LAZY_FETCH':'1'})
        offset=0
        for path in missing:
            end=data.index(b'\n',offset);header=data[offset:end].split()
            if len(header)!=3 or header[1]!=b'blob':raise ValueError('Git source blob unavailable: '+path)
            size=int(header[2]);offset=end+1;raws[path]=data[offset:offset+size];offset+=size+1
        if offset!=len(data):raise ValueError('Unexpected Git batch output')
    tree={}
    for row in subprocess.check_output(['git','ls-tree','-rz',revision],cwd=root).split(b'\0'):
        if row:
            meta,path=row.split(b'\t',1);mode,kind,sha=meta.decode().split();tree[path.decode()]=(mode,kind,sha)
    for path,entry in catalog['inputs'].items():
        if tree.get(path)!=('100644','blob',entry['git_blob_sha1']) and tree.get(path)!=('100755','blob',entry['git_blob_sha1']):
            raise ValueError('Input differs from the committed receipt: '+path)
        raw=raws[path]
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if digest(raw)!=entry['sha256'] or blob!=entry['git_blob_sha1'] or len(raw)!=entry['size']:
            raise ValueError('Input source identity failed: '+path)
    return raws


def bundle(root,revision,destination):
    owned,catalog=collect(root,revision);raws=read_inputs(root,catalog,revision)
    for project,data in catalog['projects'].items():
        data['toolchain']=raws[project+'/lean-toolchain'].decode('utf-8-sig').strip()
    lock=json.loads(raws[FALLBACK_ROOT+'/lake-manifest.json'])
    mathlib=next(p['rev'] for p in lock['packages'] if p['name']=='mathlib')
    catalog['fallback']=dict(toolchain=raws[FALLBACK_ROOT+'/lean-toolchain'].decode().strip(),
                             mathlib=mathlib,lock=lock,basis=FALLBACK_ROOT,
                             scope='New execution overlay, not a recovered original project.')
    collection=Collection(catalog,lambda path:raws[path]);routes=[]
    for source in catalog['sources']:
        try:
            plan=collection.plan(source['path'])
            source.update(mode=plan['mode'],toolchain=plan['toolchain'],issues=plan['issues'],
                          input_files=len(plan['files']))
        except ValueError as error:
            source.update(mode='needs-setup',toolchain=None,issues=[str(error)],input_files=0)
        routes.append({k:v for k,v in source.items() if k!='project'} | {'project':source['project']})
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    readme='''Komorebi Lean source runner

Install Python 3.11+, Git, and Elan from https://lean-lang.org/install/.
Unzip this bundle, open a terminal in its folder, and run:

  python run_lean.py --list
  python run_lean.py --source "PATH_FROM_THE_LIST" --output ../my-lean-run

Use a new output directory for each run. First runs download the pinned Lean
toolchain and Mathlib cache and can take several minutes and gigabytes of disk.
The runner executes native Lean, including the source's commands. Use it on
source you intend to run. Nothing executes just by viewing the website.

RUN_INPUTS.json records every staged source/configuration hash. RESULT.json and
per-step logs distinguish setup failures, timeouts, compiler failures, warnings,
and a clean compiler exit. A sorry warning is not a finished proof. No axiom or
whole-paper audit is performed and collection coverage labels do not change.

Retained projects keep their own toolchain and lockfile. Files without a Lake
project use a labelled reconstructed workspace: local imports are resolved to
the closest source edition inside the same work, distinct ties are rejected, and the
exact source bytes are copied into module paths. The overlay's pinned Lean and
Mathlib environment comes from the retained Paper V setup. It is an experiment
in that environment, not a claim to have recovered the original setup.

The bundle includes the retained Lean sources for the 16 reading editions plus
source/configuration inputs for their Lake projects. Compiled objects, package
caches, historical result logs and binary publication archives are omitted. Source/license paths and
checksums are listed in CATALOG.json. Keep this bundle with a run's records.
'''
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        def put(path,raw,executable=False):
            safe_path(path);info=zipfile.ZipInfo(path,date_time=(2020,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o100755 if executable else 0o100644)<<16;archive.writestr(info,raw)
        put('run_lean.py',(root/'tools/lean_runner.py').read_bytes())
        put('CATALOG.json',(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n').encode())
        put('README.txt',readme.encode())
        put('LICENSE.md',(root/'LICENSE.md').read_bytes())
        for path,raw in raws.items():put('inputs/'+path,raw,owned[path]['mode']=='100755')
    return catalog,dict(schema=1,source_revision=revision,bundle_sha256=digest(destination.read_bytes()),
                        bundle_bytes=destination.stat().st_size,source_files=len(catalog['inputs']),
                        files=routes,modes=dict(Counter(s['mode'] for s in routes)),
                        needs_setup=sum(bool(s['issues']) for s in routes),build_runs_lean=False)


def build(reader):
    site=reader.site;catalog,record=bundle(site.root,site.revision,site.output/'downloads/komorebi-lean-runner.zip')
    site.write('lean/run.json',json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    e=html.escape
    def asset(name):return site.rel('assets/'+name,PAGE)+'?v='+digest((site.root/'website/assets'/name).read_bytes())[:12]
    options=''.join('<option value="'+e(s['id'])+'">'+e(s['label']+' · '+s['path'].split('/')[-1])+'</option>' for s in record['files'])
    size=round(record['bundle_bytes']/1048576,1)
    body=f'''<link rel="stylesheet" href="{asset('lean-reader.css')}"><link rel="stylesheet" href="{asset('lean-execution.css')}">
<section class="lean-execution" data-lean-execution data-catalog="run.json">
<nav class="breadcrumbs" aria-label="Lean navigation"><a href="index.html">Inspect Lean</a><a href="playground.html">Interactive pilot</a></nav>
<header class="lean-heading"><p class="eyebrow">The complete reading collection</p><h1>Run Lean with its dependencies</h1>
<p class="lean-lede">Choose any of the {len(record['files']):,} displayed source files. Prepare its imports, use a pinned Lean environment, and keep the actual compiler output.</p></header>
<div class="lean-run-picker"><label for="lean-run-search">Find a source file</label><input id="lean-run-search" type="search" placeholder="Work, file name, or path" autocomplete="off">
<label for="lean-run-file">Selected source</label><select id="lean-run-file">{options}</select><p role="status" data-lean-run-count></p></div>
<section class="lean-run-selection" data-lean-run-selection hidden><p class="eyebrow" data-run-work></p><h2 data-run-name></h2><code class="lean-run-path" data-run-path></code>
<p data-run-mode></p><p data-run-pin></p><p data-run-issues hidden></p><nav class="lean-actions" aria-label="Selected proof routes"><a data-run-inspect>Inspect source</a><a data-run-workflow href="https://github.com/KomorebiP/Operation-KOMOREBI/actions/workflows/lean-source-run.yml">Run on GitHub</a></nav>
<label for="lean-run-command">Run command after unzipping the bundle</label><textarea id="lean-run-command" rows="3" readonly spellcheck="false"></textarea>
<p class="lean-run-help">Use a fresh output folder. The runner downloads the pinned toolchain and dependencies on its first run, then records diagnostics and source hashes.</p></section>
<section class="lean-run-start"><h2>Run on your computer</h2><p><a class="button" download href="../downloads/komorebi-lean-runner.zip">Download Lean runner · {size} MB</a></p>
<ol><li>Install Python 3.11+, Git, and <a href="https://lean-lang.org/install/">Elan, Lean’s toolchain manager</a>.</li><li>Unzip the bundle and open a terminal in its folder.</li><li>Choose a source above and run its command. Open <code>RESULT.json</code> and the logs in the new output folder.</li></ol>
<p>Nothing runs when you browse this page. The downloaded runner executes native Lean on your computer. First runs can take several minutes and gigabytes of disk.</p></section>
<section class="lean-run-explain"><h2>Two environments, stated explicitly</h2><p><strong>Retained project:</strong> use the original Lake configuration, Lean pin, lockfile, and local source modules.</p><p><strong>Reconstructed workspace:</strong> keep the source bytes unchanged, collect its local imports, and use a fixed Lean/Mathlib environment. This is a new experiment rather than a replay of an absent project configuration. Ambiguous or missing imports stop preparation.</p>
<p><strong>GitHub runs:</strong> repository maintainers can use the manual <a href="https://github.com/KomorebiP/Operation-KOMOREBI/actions/workflows/lean-source-run.yml">Lean source runner workflow</a>. Paste the selected repository path into its <strong>source</strong> input. The job checks that file and saves its result and logs as an artifact.</p>
<p>Compiler errors, warnings, missing imports, and timeouts remain visible. A clean compiler exit does not audit axioms or establish that the entire paper is formalized. Existing coverage labels stay attached to their recorded evidence.</p>
<p>For interactive checking of custom modules inside this site, the runner can also export a project for a dedicated Lean web server. <a href="../collection/LEAN_EXECUTION.html#path-to-interactive-checking-inside-the-site">Backend setup and export instructions</a>.</p>
<p><a href="run.json">Environment catalogue and bundle checksum</a> · <a href="../downloads/komorebi-lean-runner.zip" download>Complete runner bundle</a></p></section>
<noscript><p>The bundle works without site JavaScript. Run <code>python run_lean.py --list</code> to list source paths, then follow its README. The source inspector and GitHub workflow links also work directly.</p></noscript></section><script defer src="{asset('lean-execution.js')}"></script>'''
    site.page(PAGE,'Run Lean with dependencies',body)
    site.search.append(dict(title='Run Lean with dependencies',group='Collection',kind='Lean',work_ids=sorted({s['work'] for s in record['files']}),url=PAGE,text='native Lean project runner all source files pinned toolchain Mathlib local imports'))
    return {k:record[k] for k in ('modes','needs_setup','source_files','bundle_bytes','build_runs_lean')}


def verify(root,documents):
    record=json.loads((root/'lean/run.json').read_bytes());bundle_path=root/'downloads/komorebi-lean-runner.zip'
    assert digest(bundle_path.read_bytes())==record['bundle_sha256']
    selected={f['path'] for work in json.loads((root/'lean/index.json').read_bytes())['works'] for f in work['files']}
    sources={r['repository_path']:r for r in documents['files'] if r['repository_path'] in selected}
    assert set(sources)==selected
    assert {s['path'] for s in record['files']}==selected
    assert len(record['files'])==len(sources) and len({s['id'] for s in record['files']})==len(sources)
    with zipfile.ZipFile(bundle_path) as archive:
        catalog=json.loads(archive.read('CATALOG.json'))
        assert record['source_revision']==catalog['source_revision']
        assert len(catalog['inputs'])==record['source_files']
        for path,entry in catalog['inputs'].items():assert digest(archive.read('inputs/'+safe_path(path)))==entry['sha256'],path
        for source in record['files']:
            original=sources[source['path']]
            assert source['sha256']==original['sha256'] and source['id']==identity(source['path'])
            assert digest(archive.read('inputs/'+source['path']))==original['sha256']
    assert record['build_runs_lean'] is False
    return dict(files=len(sources),inputs=record['source_files'],bundle_identity='PASS',build_runs_lean=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--revision',default='HEAD')
    args=parser.parse_args();revision=subprocess.check_output(['git','rev-parse',args.revision],cwd=args.root,text=True).strip()
    _,record=bundle(args.root,revision,args.output);print(json.dumps({k:record[k] for k in ('modes','needs_setup','source_files','bundle_bytes')}))


if __name__=='__main__':main()
