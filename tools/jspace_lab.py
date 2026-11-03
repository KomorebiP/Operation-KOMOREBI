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
<p>Explore two saved neural agents. Change their temporary working values, follow a message, or check what survives later.</p></div>
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
<p id="jl-guide-note" class="jlab-guide-note">Choose a target pair and adjust the edit strength. Compare the two agents’ answers, then audit their remembered facts.</p>
<details class="jlab-help"><summary>A quick guide to the terms</summary><dl><div><dt>Working pair</dt><dd>Two temporary values, written as [left, right]. These are what the agents are currently using.</dd></div><div><dt>Donor</dt><dd>A reference state with the working values you want. The edit tries to transfer a small part of that state.</dd></div><div><dt>Facts</dt><dd>Eight stored values tested separately. Changing an answer can also harm recall.</dd></div></dl></details>
<div id="jl-start-panel" class="jlab-start-panel"><p>Start with a prepared example, then explore the controls.</p><button type="button" id="jl-launch" disabled>Start state edit <span aria-hidden="true">→</span></button></div>
<p id="jl-status" role="status" aria-live="polite"></p>
<iframe id="jl-frame" title="J-Space experiment controls and actual neural-model results" data-src="assets/j-space/causal-lab.html?v=APP_VERSION" data-style="WORKBENCH_STYLE" hidden></iframe>
</section>
<noscript><p class="jlab-note">Enable JavaScript to run the agents, or <a href="assets/j-space/causal-lab.html" download="Komorebi_JSpace_Causal_Lab_v1_4.html">download the self-contained lab</a> and open it in a browser with JavaScript enabled.</p></noscript>

<aside class="jlab-context" aria-label="About this experiment"><p><strong>A research experiment.</strong> These are small saved neural models. An edit can work at first and fail later; a successful case is not a J-space certificate. All predictions and failed reference checks come from the original instrument.</p>
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
