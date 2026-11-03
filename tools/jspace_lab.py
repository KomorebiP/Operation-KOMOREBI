"""Publish the preserved, self-contained J-Space lab with a reader-site entry."""
import hashlib
import json


COMPONENT = 'experiments-jspace-causal-lab'
SOURCE = 'experiments/jspace-causal-lab/Komorebi_JSpace_Causal_Lab_v1_4.html'
APP_URL = 'assets/j-space/causal-lab.html'
RECORD_URL = 'assets/j-space/source.json'
APP_SHA256 = '29e6c50cb376136c36c682703962d4e2276cd40570f6ce4abb92ac1810821370'
APP_SIZE = 4424170


def source_record():
    return dict(schema=1, component=COMPONENT, source=SOURCE, url=APP_URL,
                sha256=APP_SHA256, size=APP_SIZE, edition='1.4',
                scope='Unchanged saved browser instrument. No new training or J-space certification.')


def verify(root):
    """Check the one frozen HTML asset before exempting it from site chrome QA."""
    raw = (root/APP_URL).read_bytes()
    if len(raw) != APP_SIZE or hashlib.sha256(raw).hexdigest() != APP_SHA256:
        raise ValueError('J-Space browser instrument differs from the preserved edition')
    if json.loads((root/RECORD_URL).read_bytes()) != source_record():
        raise ValueError('J-Space source record differs from the preserved edition')
    return source_record()


def build(site):
    receipt = json.loads((site.root/('manifests/source-imports/'+COMPONENT+'.json')).read_bytes())
    entry = next(item for item in receipt['files'] if item['path'] == SOURCE.rsplit('/', 1)[1])
    if entry['sha256'] != APP_SHA256 or entry['size'] != APP_SIZE:
        raise ValueError('Review the J-Space edition before changing its published identity')
    raw = site.read_source({**entry, 'repository_path': SOURCE})
    target = site.output/APP_URL
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    site.write(RECORD_URL, json.dumps(source_record(), indent=2)+'\n')

    def asset(name):
        return 'assets/'+name+'?v='+hashlib.sha256((site.root/'website/assets'/name).read_bytes()).hexdigest()[:12]

    body = '''<div class="jlab" id="j-lab">
<header class="jlab-intro">
<div><p class="jlab-kicker">Neural agents / working states / causal tests</p>
<h1>J-Space laboratory</h1>
<p class="jlab-lead">Change a working state.<br><em>Follow what survives.</em></p>
<p>Run two saved neural agents in your browser. Edit a candidate working state, trace its messages, and test whether remembered facts and later answers survive.</p>
<div class="jlab-actions"><button type="button" id="jl-launch" disabled>Open the interactive lab <span aria-hidden="true">→</span></button>
<a href="assets/j-space/causal-lab.html" target="_blank" rel="noopener">Open in a full tab <span aria-hidden="true">↗</span></a></div>
<p class="jlab-local">Frozen models · Local inference · No installation</p></div>
<figure class="jlab-model" aria-labelledby="jl-model-caption">
<div class="jlab-model-top"><span>Two agents. One experiment.</span><span class="jlab-live">Saved weights</span></div>
<svg viewBox="0 0 440 190" role="img" aria-labelledby="jl-diagram-title jl-diagram-desc">
<title id="jl-diagram-title">Messages between two neural agents</title>
<desc id="jl-diagram-desc">Each agent has a 64-coordinate hidden state. Eight-component messages pass in both directions. Readouts test temporary content, remembered facts and private labels.</desc>
<defs><marker id="jl-arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="currentColor"/></marker></defs>
<g class="jlab-node"><rect x="18" y="35" width="132" height="115" rx="6"/><rect x="290" y="35" width="132" height="115" rx="6"/></g>
<g class="jlab-wire" marker-end="url(#jl-arrow)"><path d="M154 70H282"/><path d="M286 120H158"/></g>
<g class="jlab-svg-label"><text x="84" y="73">Agent 1</text><text x="356" y="73">Agent 2</text></g>
<g class="jlab-svg-small"><text x="84" y="99">64 coordinates</text><text x="356" y="99">64 coordinates</text><text x="220" y="53">8-component</text><text x="220" y="97">messages</text><text x="220" y="146">Read → compare → continue</text></g>
</svg><figcaption id="jl-model-caption">Observe the actual model outputs. An edit can work at first and fail after the next exchange.</figcaption>
</figure></header>

<section class="jlab-start" aria-labelledby="jl-start-title"><div class="jlab-section-title"><h2 id="jl-start-title">Choose a question to explore</h2><p>Each starting point loads a guided case.</p></div>
<div class="jlab-guides">
<article><p class="jlab-kicker">State → answer</p><h3>Can an edit change the answer?</h3><p>Move a candidate J-space state. Compare the edited answer with the original and whole-donor references.</p><button type="button" data-jl-guide="edit" disabled>Explore a state edit <span aria-hidden="true">→</span></button></article>
<article><p class="jlab-kicker">Agent → agent</p><h3>Does the message carry the change?</h3><p>Edit one agent, follow the outgoing packet, and compare message restoration with packet-only replay.</p><button type="button" data-jl-guide="relay" disabled>Trace a message <span aria-hidden="true">→</span></button></article>
<article><p class="jlab-kicker">Now → later</p><h3>Will the change last?</h3><p>Continue the calculation after editing. Reload remembered facts and inspect where the branches agree or fail.</p><button type="button" data-jl-guide="persistence" disabled>Test persistence <span aria-hidden="true">→</span></button></article>
</div></section>

<section class="jlab-workspace" id="jl-workspace" aria-labelledby="jl-workspace-title" hidden>
<div class="jlab-section-title"><h2 id="jl-workspace-title" tabindex="-1">Interactive workbench</h2><a href="assets/j-space/causal-lab.html" target="_blank" rel="noopener">Use the full tab <span aria-hidden="true">↗</span></a></div>
<p id="jl-guide-note" class="jlab-guide-note"></p>
<p id="jl-status" role="status" aria-live="polite"></p>
<iframe id="jl-frame" title="Interactive J-Space causal lab with saved neural models" data-src="assets/j-space/causal-lab.html?v=APP_VERSION" hidden></iframe>
<p class="jlab-frame-note">The workbench has its own scroll area. Export JSON inside the lab to keep a trace. Guided starting points reset the example; reopening the current lab keeps your changes.</p>
</section>
<noscript><p class="jlab-note">Enable JavaScript to run the agents. You can also <a href="assets/j-space/causal-lab.html" download="Komorebi_JSpace_Causal_Lab_v1_4.html">download the self-contained lab</a> and open it in a browser with JavaScript enabled. Read the <a href="collection/works/experiments-jspace-causal-lab.html">experiment overview</a> for its methods and limits.</p></noscript>

<section class="jlab-context" aria-labelledby="jl-context-title"><div><p class="jlab-kicker">Interpreting a run</p><h2 id="jl-context-title">A research instrument.<br>Failures stay visible.</h2>
<p>This is the preserved causal lab 1.4: two small trained neural lineages, saved weights, candidate state directions, and explicit reference branches. A successful edit in one case is experimental evidence, not a J-space certificate.</p>
<p>Compare the reference branches, inspect individual checkpoints, and keep the failed cases alongside the successes. Read the laboratory report for its recorded tests and remaining questions.</p></div>
<div class="jlab-resources"><h3>Keep exploring</h3>
<a href="collection/works/experiments-jspace-causal-lab.html">Methods, source files and evidence <span aria-hidden="true">↗</span></a>
<a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/REVISION/experiments/jspace-causal-lab/REPORT.md">Read the laboratory report <span aria-hidden="true">↗</span></a>
<a href="assets/j-space/causal-lab.html" download="Komorebi_JSpace_Causal_Lab_v1_4.html">Download the offline lab · 4.4 MB <span aria-hidden="true">↓</span></a>
<a href="interactive.html">Explore interactive mathematics <span aria-hidden="true">→</span></a>
<p>The model runs on your device after the lab loads. The offline file includes its weights and interface.</p></div></section>
</div>'''
    body = body.replace('APP_VERSION', APP_SHA256[:12]).replace('REVISION', site.revision)
    body = '<link rel="stylesheet" href="'+asset('jspace-lab.css')+'">'+body
    body += '<script defer src="'+asset('jspace-lab.js')+'"></script>'
    site.page('j-lab.html', 'J-Space laboratory', body)
    site.search.append(dict(title='J-Space laboratory: state edits, messages and persistence',
                            group='Collection', kind='Examples', work_ids=[COMPONENT], url='j-lab.html',
                            text='Interactive J-Space causal lab neural agents frozen models state edit candidate workspace message relay mediation packet replay persistence memory factual retrieval private labels offline JSON experimental evidence'))
    return verify(site.output)
