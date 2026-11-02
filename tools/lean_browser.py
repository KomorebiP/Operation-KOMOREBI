"""Publish small receipt-bound workspaces for the local WebAssembly compiler."""
import hashlib
import html
import json
from pathlib import Path
import shutil

PAGE='lean/browser/index.html'
BASE='lean/browser/'
RESIDUAL='papers/paper-x/current/current_continuation/lean/PaperX/Residual.lean'
COMPRESSION='monographs/proof-path-theory/formal/ProofPath/Compression.lean'
RECOVERY='monographs/proof-path-theory/formal/ProofPath/Recovery.lean'
COMPAT_SOURCE='''-- Browser compatibility: Lean 4.33 calls this lemma dif_pos.
-- Checked by Lean alongside Recovery; this is not retained paper source.
universe u
theorem dite_eq_left {α : Sort u} {p : Prop} [Decidable p]
    {t : p → α} {e : ¬ p → α} (h : p) : dite p t e = t h := by
  exact dif_pos h
'''
WORKSPACES=[
    ('paper-x-residual','Paper X · Residual partition','paper-x', [('PaperX.Residual',RESIDUAL)]),
    ('proof-path-compression','Proof Path Theory · Compression','proof-path-theory', [('ProofPath.Compression',COMPRESSION)]),
    ('proof-path-recovery','Proof Path Theory · Recovery with its local import','proof-path-theory', [('ProofPath.Compression',COMPRESSION),('ProofPath.Recovery',RECOVERY)]),
]


def action(site,page,*,source=None,work=None):
    for key,label,owner,files in WORKSPACES:
        if source==files[-1][1] or source is None and work==owner:
            return '<a href="'+site.rel(PAGE,page)+'?example='+key+'">Edit and run in your browser</a>'
    return ''


def verify_runtime(root):
    data=json.loads((root/'SOURCE.json').read_bytes())
    from prepare_lean_wasm import UPSTREAM, LEAN, MATHLIB
    if (data['upstream'],data['lean'],data['mathlib'])!=(UPSTREAM,LEAN,MATHLIB):
        raise ValueError('Unexpected browser compiler build')
    required={'lean-wasm/lean.js','lean-wasm/lean.wasm.gz','lean-wasm/core-layer.json',
              'lean-lib/Lean-layer.json','lean-lib/Std-layer.json','lean-lib/Batteries-layer.json',
              'lean-mathlib/real-analysis-layer.json'}
    if not required <= data['files'].keys():raise ValueError('Incomplete browser compiler download')
    for path,record in data['files'].items():
        from lean_runner import safe_path
        raw=(root/safe_path(path)).read_bytes()
        if len(raw)!=record['size'] or hashlib.sha256(raw).hexdigest()!=record['sha256']:
            raise ValueError('Browser compiler checksum mismatch: '+path)
    return data


def build(reader,runtime):
    site=reader.site
    records={r['repository_path']:r for files in reader.lean_works.values() for r in files}
    examples=[]
    for key,title,work,files in WORKSPACES:
        sources=[]
        for module,path in files:
            r=records[path];raw=site.read_source(r)
            if hashlib.sha256(raw).hexdigest()!=r['sha256']:raise ValueError('Browser proof source identity changed')
            sources.append(dict(module=module,path=path,sha256=r['sha256'],
                                inspect=site.rel(r['url'],PAGE),download=site.rel(r['file_url'],PAGE),
                                text=raw.decode('utf-8-sig').replace('\r\n','\n')))
        example=dict(id=key,title=title,work=work,files=sources)
        if key=='proof-path-recovery':
            example['compatibility']=dict(source=COMPAT_SOURCE,sha256=hashlib.sha256(COMPAT_SOURCE.encode()).hexdigest())
        examples.append(example)
    runtime_record=verify_runtime(runtime)
    engine=site.output/BASE/'engine'
    shutil.copytree(runtime,engine,dirs_exist_ok=True)
    shutil.copyfile(site.root/'website/assets/lean-browser-sw.js',site.output/BASE/'sw.js')
    data=dict(schema=1,revision=site.revision,examples=examples,lean=runtime_record['lean'],
              mathlib=runtime_record['mathlib'],download_bytes=runtime_record['bytes'],
              execution='local WebAssembly',changes_recorded_verification=False)
    site.write(BASE+'examples.json',json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    site.write(BASE+'compatibility.lean',COMPAT_SOURCE)
    def asset(name):
        digest=hashlib.sha256((site.root/'website/assets'/name).read_bytes()).hexdigest()[:12]
        return site.rel('assets/'+name,PAGE)+'?v='+digest
    opts=''.join('<option value="'+e['id']+'">'+html.escape(e['title'])+'</option>' for e in examples)
    body=f'''<link rel="stylesheet" href="{asset('lean-browser.css')}">
<section class="lean-local" data-lean-local>
<nav class="breadcrumbs" aria-label="Lean navigation"><a href="{site.rel('lean/index.html',PAGE)}">Inspect Lean</a></nav>
<header class="lean-heading"><p class="eyebrow">The papers · A local proof workspace</p><h1>Edit a proof. Ask Lean.</h1>
<p class="lean-lede">Explore a published proof, change a step, and check it on your own device. The compiler runs inside this browser.</p></header>
<div class="lean-local-intro"><p><strong>Free, with no account.</strong> Proof text stays in this tab. The site downloads compiler files; it does not send your edits to a proof service.</p>
<p class="lean-local-meta">First use downloads a substantial library. Loading can take a minute or more and needs a computer with enough memory. Later checks reuse the loaded compiler; downloaded files are cached when your browser allows it.</p></div>
<p data-local-direct hidden>This compiler needs its own browser page. <a data-local-direct-link target="_blank" rel="noopener">Open the workspace in a new tab</a>.</p>
<div class="lean-local-selectors"><div><label for="local-lean-workspace">Published workspace</label><select id="local-lean-workspace" data-local-example>{opts}</select></div><div><label for="local-lean-file">File to edit</label><select id="local-lean-file" data-local-file></select></div></div>
<nav class="lean-actions" aria-label="Original proof routes"><a data-local-inspect>Inspect original source</a><a data-local-download download>Download original</a></nav>
<p class="lean-local-meta" data-local-source></p>
<details data-local-compat hidden><summary>Browser version compatibility lemma included</summary><p>Lean checks this extra lemma alongside the proof. It supplies a name used by the paper that the older browser compiler lacks. The original source below is unchanged.</p><pre data-local-compat-code></pre><p><a href="compatibility.lean" download>Download the compatibility lemma</a></p></details>
<div class="lean-local-editor"><label for="local-lean-code">Lean source</label><textarea id="local-lean-code" data-local-code spellcheck="false" autocapitalize="off" autocomplete="off" wrap="off"></textarea></div>
<div class="lean-local-toolbar"><button type="button" data-local-run disabled>Load Lean and run</button><button type="button" data-local-stop disabled>Stop</button><button type="button" data-local-restore disabled>Restore workspace</button><button type="button" data-local-break disabled>Try a false proof</button><button type="button" data-local-save disabled>Save edited file</button></div>
<p class="lean-local-status" data-local-status role="status" aria-live="polite">Loading the published workspace…</p>
<section class="lean-local-results" aria-label="Lean results"><h2>Lean’s response</h2><pre data-local-output>No checks yet.</pre></section>
<details><summary>Download and compiler activity</summary><pre data-local-log></pre></details>
<details><summary>Versions, source and limits</summary>
<p>This pilot uses Lean 4.33.0, compiler revision <code>{runtime_record['lean'][:12]}</code>, and selected Mathlib modules from <code>{runtime_record['mathlib'][:12]}</code>. The papers’ retained projects may use different versions. Results here are browser experiments and do not change the collection’s recorded verification.</p>
<p>Choose from three prepared workspaces. You can edit any file in a workspace. Required project files are compiled first, then the dependent file. Imports outside the packaged libraries produce an error. Compiler crashes and interrupted checks produce no successful result.</p>
<p>For local imports, a generated wrapper names and exports the module into the compiler’s temporary filesystem. Original downloads remain byte for byte identical to the retained sources. A clean result means Lean completed checking these files with no reported warnings; it is not an audit of axioms or an entire paper.</p>
<p>Compiler download cache: about {runtime_record['bytes']/1048576:.0f} MiB across all available libraries. Proofs using only Std need less. Edits live in this tab; save a copy before leaving.</p>
<p><a href="examples.json">Source checksums</a> · <a href="engine/SOURCE.json">Compiler download record</a> · <a href="{site.rel('assets/lean-wasm/NOTICE.txt',PAGE)}">Open source credits</a></p>
<button type="button" data-local-clear>Clear downloaded compiler cache</button></details>
<noscript><p>JavaScript is needed to run Lean. Original sources remain available through <a href="{site.rel('lean/index.html',PAGE)}">Inspect Lean</a>.</p></noscript>
</section><script type="module" src="{asset('lean-browser.js')}"></script>'''
    site.page(PAGE,'Edit and run Lean in your browser',body)
    site.search.append(dict(title='Edit and run Lean in your browser',group='Collection',kind='Lean',
                            work_ids=['paper-x','proof-path-theory'],url=PAGE,
                            text='Free local browser WebAssembly Lean compiler edit check proofs residual compression recovery'))
    return dict(workspaces=len(examples),execution='local WebAssembly',compiler_bytes=runtime_record['bytes'],build_runs_lean=False)


def verify(root,documents):
    data=json.loads((root/BASE/'examples.json').read_bytes())
    records={r['repository_path']:r for r in documents['files']}
    assert data['execution']=='local WebAssembly' and data['changes_recorded_verification'] is False
    assert len(data['examples'])==len(WORKSPACES)
    for example,expected in zip(data['examples'],WORKSPACES):
        assert example['id']==expected[0]
        assert [(f['module'],f['path']) for f in example['files']]==expected[3]
        if example['id']=='proof-path-recovery':
            assert example['compatibility']['source']==COMPAT_SOURCE
            assert example['compatibility']['sha256']==hashlib.sha256(COMPAT_SOURCE.encode()).hexdigest()
            assert (root/BASE/'compatibility.lean').read_text(encoding='utf-8')==COMPAT_SOURCE
        else:assert 'compatibility' not in example
        for file in example['files']:
            r=records[file['path']];raw=(root/r['file_url']).read_bytes()
            assert file['sha256']==r['sha256']==hashlib.sha256(raw).hexdigest()
            assert file['text']==raw.decode('utf-8-sig').replace('\r\n','\n')
    verify_runtime(root/BASE/'engine')
    return dict(workspaces=len(WORKSPACES),source_identity='PASS',execution='local WebAssembly')
