"""Publish one receipt-bound proof in an opt-in, externally hosted Lean editor."""
import hashlib
import html
import json
from urllib.parse import quote, urlencode

PAGE = 'lean/playground.html'
WORK = 'paper-xii'
SOURCE = ('papers/paper-xii/current/core/publication/source/lean_guide/'
          'formal_release/lean/PaperXII/LocalIdempotents.lean')
HOST = 'https://live.lean-lang.org/'
PROJECT = 'MathlibDemo'
DECLARATION = 'PaperXII.LocalIdempotents.eq_zero_or_one'
SUFFIX = '\n-- Playground inspection command; the retained source above is unchanged.\n#check '+DECLARATION+'\n'


def action(site, page, *, work=None, source=None):
    if work != WORK and source != SOURCE:
        return ''
    return '<a href="'+site.rel(PAGE, page)+'">Try this proof in Lean</a>'


def editor_url(code):
    return HOST+'#'+urlencode({'project': PROJECT, 'code': code}, quote_via=quote)


def build(reader):
    site = reader.site
    records = [r for r in reader.lean_works.get(WORK, []) if r['repository_path'] == SOURCE]
    if len(records) != 1:
        raise ValueError('Lean playground needs its selected, receipt-bound Paper XII source')
    record = records[0]
    raw = site.read_source(record)
    if hashlib.sha256(raw).hexdigest() != record['sha256']:
        raise ValueError('Lean playground source checksum differs from the reader record')
    text = raw.decode('utf-8-sig')
    code = text+SUFFIX
    url = editor_url(code)
    e = html.escape
    def asset(name):
        digest = hashlib.sha256((site.root/'website/assets'/name).read_bytes()).hexdigest()[:12]
        return site.rel('assets/'+name, PAGE)+'?v='+digest
    def link(path):
        return e(site.rel(path, PAGE), quote=True)
    from lean_reader import highlight_lines
    preview = '\n'.join(highlight_lines(text))
    body = f'''<link rel="stylesheet" href="{asset('lean-reader.css')}">
<link rel="stylesheet" href="{asset('lean-playground.css')}">
<section class="lean-playground" data-lean-playground>
<nav class="breadcrumbs" aria-label="Lean navigation"><a href="{link('lean/index.html')}">Inspect Lean</a><a href="{link('lean/paper-xii/index.html')}">Paper XII sources</a></nav>
<header class="lean-heading"><p class="eyebrow">Paper XII · Interactive proof</p><h1>Try a proof in Lean</h1>
<p class="lean-lede">An idempotent in a commutative local ring is either zero or one. Explore Proposition 3.4, edit its proof, and see what Lean says.</p></header>
<nav class="lean-actions" aria-label="Proof reading routes"><a href="{link('read/paper-xii/index.html')}">Read Paper XII</a><a href="{link(record['url'])}">Inspect original source</a><a download href="{link(record['file_url'])}">Download source</a></nav>
<div class="lean-session-intro"><div><h2>A live editor, alongside the paper</h2>
<p>Load the editor to check the proof automatically. Click a proof step to see its goal; open <strong>All Messages</strong> for diagnostics. The final <code>#check</code> displays the theorem’s type.</p>
<p class="lean-service-note">Powered by <a href="{HOST}" target="_blank" rel="noopener noreferrer">live.lean-lang.org</a>. Loading connects to that service; code you enter is sent there for checking. An internet connection is required.</p></div>
<div class="lean-session-actions"><button type="button" data-lean-open hidden>Load Lean editor</button>
<a data-lean-external href="{e(url, quote=True)}" target="_blank" rel="noopener noreferrer">Open original proof in a new tab <span aria-hidden="true">↗</span></a>
<button type="button" data-lean-close hidden>Close editor</button></div></div>
<p class="lean-session-status" role="status" aria-live="polite" data-lean-status>Original source below. The live editor loads only when you choose it.</p>
<div class="lean-editor-slot" data-lean-slot hidden></div>
<p class="lean-editor-help" data-lean-help hidden>Lean checks as you type. If the editor stays blank or cannot connect, use the new-tab link above. Closing or restoring the editor discards its edits; copy code you want to keep first.</p>
<details class="lean-original" open data-lean-original><summary>Original source · LocalIdempotents.lean</summary><pre class="lean-original-code"><code>{preview}</code></pre></details>
<aside class="lean-experiment"><h2>Make Lean object</h2><p>Inside the editor, replace the first <code>exact h.mul_left_cancel …</code> step with <code>rfl</code>. Lean should report an error. Use <strong>Restore original proof</strong> to start again. A <code>sorry</code> warning means a proof is unfinished.</p></aside>
<details class="lean-session-scope"><summary>Source, Lean version, and scope</summary>
<p>The starting proof is the complete retained <code>LocalIdempotents.lean</code> from Paper XII. The playground adds one <code>#check</code> command after the file; it does not alter the original download.</p>
<p>The editor uses the live service’s <code>{PROJECT}</code> project. Its Lean and Mathlib versions can change and are shown inside the editor. This is a live experiment on the service’s environment, rather than a reproduction of the paper’s pinned project.</p>
<p>This pilot checks one file. It does not replay the full paper, load the collection’s other project modules, or update recorded verification and coverage labels. Results and warnings are shown by Lean inside the editor; this page does not assign a proof-success badge.</p>
<p><a href="{link('lean/playground.json')}">Source checksum and playground record</a> · <a href="{link('collection/works/paper-xii.html')}">Paper XII overview and evidence</a></p></details>
<noscript><p>Use <strong>Open original proof in a new tab</strong> to check it with the live service. The source remains readable here without JavaScript.</p></noscript>
</section><script defer src="{asset('lean-playground.js')}"></script>'''
    site.page(PAGE, 'Try a proof in Lean', body)
    site.write('lean/playground.json', json.dumps(dict(
        schema=1, source_revision=site.revision, work=WORK, repository_path=SOURCE,
        source_url=record['url'], file_url=record['file_url'], sha256=record['sha256'],
        source_bytes=len(raw), appended_code=SUFFIX, editor_host=HOST, project=PROJECT,
        environment='Live service versions; not the paper project lockfile',
        execution='Opt-in remote Lean service', build_runs_lean=False,
        changes_recorded_verification=False), ensure_ascii=False, indent=2)+'\n')
    site.search.append(dict(title='Try a proof in Lean', group='Collection', kind='Lean',
                            work_ids=[WORK], url=PAGE,
                            text='Paper XII Proposition 3.4 local ring idempotent interactive Lean proof playground'))
    return dict(examples=1, execution='opt-in external service', build_runs_lean=False)


def verify(root, documents):
    from html.parser import HTMLParser
    class Links(HTMLParser):
        def __init__(self):
            super().__init__(); self.urls=[]; self.frames=[]
        def handle_starttag(self, tag, attrs):
            attrs=dict(attrs)
            if tag == 'a' and 'data-lean-external' in attrs: self.urls.append(attrs['href'])
            if tag == 'iframe': self.frames.append(attrs)
    data=json.loads((root/'lean/playground.json').read_bytes())
    record=next(r for r in documents['files'] if r['repository_path'] == SOURCE)
    raw=(root/record['file_url']).read_bytes()
    assert data['repository_path'] == SOURCE and data['work'] == WORK
    assert data['source_url'] == record['url'] and data['file_url'] == record['file_url']
    assert data['source_revision'] == documents.get('source_revision', data['source_revision'])
    assert data['sha256'] == record['sha256'] == hashlib.sha256(raw).hexdigest()
    assert data['source_bytes'] == len(raw) and data['appended_code'] == SUFFIX
    assert data['editor_host'] == HOST and data['project'] == PROJECT
    assert data['build_runs_lean'] is False and data['changes_recorded_verification'] is False
    parser=Links(); parser.feed((root/PAGE).read_text(encoding='utf-8'))
    assert parser.urls == [editor_url(raw.decode('utf-8-sig')+SUFFIX)]
    assert not parser.frames, 'External editor must remain opt-in'
    return dict(examples=1, source_identity='PASS', build_runs_lean=False)
