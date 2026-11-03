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
<div><p class="jlab-kicker">Interactive research</p><h1>J-Space lab</h1>
<p class="jlab-purpose">Can a small internal edit change an answer while preserving remembered facts?</p>
<p>Two small neural agents receive eight 0/1 facts, then work with a temporary pair of values. Edit part of their internal states, then test the answers, messages and recall.</p></div>
<div class="jlab-meta"><span class="jlab-local">Runs on your device · No installation</span>
<a href="assets/j-space/causal-lab.html" target="_blank" rel="noopener">Open the full research lab <span aria-hidden="true">↗</span></a>
<a href="assets/j-space/causal-lab.html" download="Komorebi_JSpace_Causal_Lab_v1_4.html">Download offline · 4.4 MB <span aria-hidden="true">↓</span></a></div>
</header>

<div class="jlab-picker" role="group" aria-label="Choose an experiment">
<button type="button" data-jl-guide="edit" aria-pressed="true" aria-controls="jl-workspace" disabled><span class="jlab-number" aria-hidden="true">01</span><span><strong>State edit</strong><small>Change a value. Compare the answers.</small></span></button>
<button type="button" data-jl-guide="relay" aria-pressed="false" aria-controls="jl-workspace" disabled><span class="jlab-number" aria-hidden="true">02</span><span><strong>Message trace</strong><small>Follow the change to the other agent.</small></span></button>
<button type="button" data-jl-guide="persistence" aria-pressed="false" aria-controls="jl-workspace" disabled><span class="jlab-number" aria-hidden="true">03</span><span><strong>Persistence</strong><small>Keep computing. Check what survives.</small></span></button>
</div>
<p class="jlab-switch-note">Changing experiments loads a fresh example. Use the export controls to keep a run.</p>

<section class="jlab-workspace" id="jl-workspace" aria-labelledby="jl-workspace-title">
<div class="jlab-workspace-head"><div><p class="jlab-kicker" id="jl-step-label">01 / State edit</p><h2 id="jl-workspace-title" tabindex="-1">Can an edit change the answer?</h2></div><button type="button" id="jl-reset" class="jlab-secondary" hidden disabled>Reset example</button></div>
<p id="jl-guide-note" class="jlab-guide-note">Change a small part of the agents’ internal states. Test whether the answers change while the remembered facts stay retrievable.</p>
<details class="jlab-help"><summary>New here? Understand the experiment</summary><dl><div><dt>Agent</dt><dd>A saved neural network with its own internal state. The two agents exchange short numerical messages.</dd></div><div><dt>Working pair</dt><dd>Two temporary 0/1 values, written as [left, right]. Later operations can flip or swap them.</dd></div><div><dt>Remembered facts</dt><dd>Eight 0/1 values supplied at the start. Recall is tested separately from the current working answer.</dd></div><div><dt>Target reference (donor)</dt><dd>A comparison execution with the working pair you want. The default J edit transfers only a projection of its state.</dd></div><div><dt>Candidate J-space</dt><dd>Three selected directions inside each agent’s 64-number state. The experiment tests what editing those directions does.</dd></div><div><dt>Reference check</dt><dd>The original and whole-target runs check whether the models can do the task. Their failures must be considered when judging the edit.</dd></div></dl></details>
<div id="jl-start-panel" class="jlab-start-panel"><div><strong>Begin with the prepared example.</strong><p>Then use the three steps to change a setting, read the result and check what survived.</p></div><button type="button" id="jl-launch" disabled>Start state edit <span aria-hidden="true">→</span></button></div>
<p id="jl-status" role="status" aria-live="polite"></p>
<div class="jlab-steps" role="group" aria-label="Navigate this experiment"><button type="button" id="jl-return" hidden disabled>Return to message trace with these settings <span aria-hidden="true">→</span></button><button type="button" data-jl-jump="0" disabled>1 · Choose edit</button><button type="button" data-jl-jump="1" disabled>2 · Compare answers</button><button type="button" data-jl-jump="2" disabled>3 · Check facts</button></div>
<iframe id="jl-frame" title="J-Space experiment controls and actual neural-model results" data-src="assets/j-space/causal-lab.html?v=APP_VERSION" data-style="WORKBENCH_STYLE" hidden></iframe>
</section>
<noscript><p class="jlab-note">Enable JavaScript to run the agents, or <a href="assets/j-space/causal-lab.html" download="Komorebi_JSpace_Causal_Lab_v1_4.html">download the self-contained lab</a> and open it in a browser with JavaScript enabled.</p></noscript>

<aside class="jlab-context" aria-label="About this experiment"><p><strong>How far does a result go?</strong> A changed answer shows an effect in this case. It does not establish a naturally writable J-space or show that the edit works on other states, models or long sequences. Keep the failed cases and reference errors alongside the successes.</p>
<div class="jlab-resources"><a href="collection/works/experiments-jspace-causal-lab.html">Methods and source files <span aria-hidden="true">↗</span></a><a href="https://github.com/KomorebiP/Operation-KOMOREBI/blob/REVISION/experiments/jspace-causal-lab/REPORT.md">Laboratory report <span aria-hidden="true">↗</span></a><a href="interactive.html">More interactive mathematics <span aria-hidden="true">→</span></a></div></aside>
</div>'''
    body = body.replace('APP_VERSION', APP_SHA256[:12]).replace('REVISION', site.revision).replace('WORKBENCH_STYLE', asset('jspace-workbench.css'))
    body = '<link rel="stylesheet" href="'+asset('jspace-lab.css')+'">'+body
    body += '<script defer src="'+asset('jspace-workbench.js')+'"></script>'
    body += '<script defer src="'+asset('jspace-lab.js')+'"></script>'
    site.page('j-lab.html', 'J-Space laboratory', body)
    site.search.append(dict(title='J-Space laboratory: state edits, messages and persistence',
                            group='Collection', kind='Examples', work_ids=[COMPONENT], url='j-lab.html',
                            text='Interactive J-Space causal lab neural agents frozen models state edit candidate workspace message relay mediation packet replay persistence memory factual retrieval private labels offline JSON experimental evidence'))
    return verify(site.output)
