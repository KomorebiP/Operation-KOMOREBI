"""Publish control-driven versions of the three finite teaching demonstrations."""
import hashlib


def slider(identifier, label, value, low, high):
    return (f'<div class="lab-slider"><label for="{identifier}">{label}'
            f'<output for="{identifier}" id="{identifier}-value">{value}</output></label>'
            f'<input type="range" id="{identifier}" min="{low}" max="{high}" '
            f'step="1" value="{value}"></div>')


def diagram(identifier, label):
    return (f'<div class="lab-diagram" id="{identifier}" role="img" aria-label="{label}">'
            '<p>The diagram appears when JavaScript is available. The worked calculation is linked below.</p></div>')


def sources(name, page, description):
    title = {'packets': 'packet reconstruction', 'refinement': 'signal refinement', 'recovery': 'recovery'}[name]
    return (f'<div class="lab-sources"><p>{description}</p><a href="collection/demonstrations/{page}.html">'
            f'Read the {title} explanation <span aria-hidden="true">↗</span></a>'
            f'<a href="playground.html#{name}">Open the Python example</a></div>')


def build(site):
    matrix = ''.join(f'<input type="number" id="matrix-{i}" aria-label="Matrix row {i//2+1}, column {i%2+1}" '
                     f'min="-9" max="9" step="1" value="{i+1}" required>' for i in range(4))
    blocks = ''.join(f'<label for="block-{i}"><input type="checkbox" id="block-{i}" checked>'
                     f'<span>Row {i//2+1}, column {i%2+1}<output id="block-{i}-value">'
                     f'{[2, 6, 6, 12][i]}</output></span></label>' for i in range(4))
    body = '''<div class="math-lab" id="math-lab">
<header class="lab-intro"><p class="lab-kicker">Interactive mathematics</p>
<h1>Change the parts.<br><em>See what survives.</em></h1>
<p>Rebuild an operation. Refine a signal. Find what a summary loses.<br class="lab-wide-break"> Three small experiments, with the calculation always in view.</p>
<span class="lab-local">Whole-number inputs · Instant results · No installation</span></header>
<nav class="lab-tabs" aria-label="Choose an experiment">
<a id="tab-packets" href="#packets"><span>01</span> Reconstruct</a>
<a id="tab-refinement" href="#refinement"><span>02</span> Refine</a>
<a id="tab-recovery" href="#recovery"><span>03</span> Recover</a></nav>
<noscript><p class="notice">Enable JavaScript for the controls and diagrams, or follow the worked explanations below.</p></noscript>
<section class="lab-panel" id="packets" aria-labelledby="packets-title">
<div class="lab-panel-heading"><div><p class="lab-kicker">01 / Operator packets</p>
<h2 id="packets-title">The whole operation, in four pieces.</h2>
<p>Each block carries one input coordinate to one output coordinate. Keep all four to rebuild the matrix operation.</p></div>
<button type="button" data-reset="packets" disabled>Reset experiment</button></div>
<div class="lab-workspace"><fieldset class="lab-controls" id="packet-controls" disabled>
<legend>Change the inputs</legend><p class="lab-control-note">Try changing a coordinate, then remove a block.</p>
<div class="lab-matrix-row"><div><span class="lab-label" id="matrix-label">Matrix T</span>
<div class="lab-matrix" role="group" aria-labelledby="matrix-label">MATRIX</div></div>
<p>Rows are outputs.<br>Columns are inputs.<br>Whole numbers −9 to 9.</p></div>
<p class="lab-error" id="matrix-error" role="status" hidden></p>
VECTOR_SLIDERS
<fieldset class="lab-blocks"><legend>Keep these blocks</legend>BLOCKS</fieldset>
<button class="lab-secondary" type="button" id="packet-remove">Remove bottom-right block</button>
</fieldset><div class="lab-visual">PACKET_DIAGRAM
<div class="lab-metrics"><div><span>Direct result · Tx</span><output id="packet-direct">(8, 18)</output></div>
<div><span>From kept blocks</span><output id="packet-rebuilt">(8, 18)</output></div>
<div class="lab-residual"><span>Residual · direct − rebuilt</span><output id="packet-residual">(0, 0)</output></div></div>
<p class="lab-verdict" id="packet-status" role="status">All four blocks retained. The operation is reconstructed.</p>
<p class="lab-caption">Read each connection as T[row, column] × x[column]. Dashed connections mark omitted blocks.</p>
</div></div>
<details class="lab-reason"><summary>Why does reconstruction work?</summary>
<p>The coordinate projectors P₁ and P₂ add to the identity. Consequently, the sum of all four blocks PⱼTPᵢ is (P₁ + P₂)T(P₁ + P₂) = T for every vector. Omitting a block changes the retained operator whenever that block is nonzero; a particular input may still give the same output.</p></details>
PACKET_SOURCES</section>
<section class="lab-panel" id="refinement" aria-labelledby="refinement-title">
<div class="lab-panel-heading"><div><p class="lab-kicker">02 / Signal refinement</p>
<h2 id="refinement-title">More parts. The same signal.</h2>
<p>Separate eight samples by their original addresses. Finer packets preserve every value; discarding a packet can leave a residual.</p></div>
<button type="button" data-reset="refinement" disabled>Reset experiment</button></div>
<div class="lab-workspace"><fieldset class="lab-controls" id="signal-controls" disabled>
<legend>Shape the signal</legend><label class="lab-label" for="signal-preset">Start with a shape</label>
<select id="signal-preset"><option value="ramp">Rising sequence</option><option value="alternating">Alternating signs</option><option value="pulse">Single pulse</option><option value="custom" disabled>Custom signal</option></select>
<div class="lab-samples">SIGNAL_SLIDERS</div>
<label class="lab-label" for="signal-count">Number of packets</label>
<select id="signal-count" aria-describedby="signal-level-help"><option value="2">2 · even and odd addresses</option><option value="4" selected>4 · remainders modulo four</option><option value="8">8 · one sample per packet</option></select>
<p class="lab-control-note" id="signal-level-help">Changing resolution restores all packets.</p>
<button class="lab-secondary" type="button" id="signal-drop">Discard packet 2</button>
</fieldset><div class="lab-visual">SIGNAL_DIAGRAM
<fieldset class="lab-packets" id="signal-packets" disabled><legend>Keep these address packets</legend></fieldset>
<div class="lab-metrics lab-metrics-two"><div><span>Retained samples</span><output id="signal-retained">8 / 8</output></div>
<div class="lab-residual"><span>Squared residual norm · Σrᵢ²</span><output id="signal-energy">0</output></div></div>
<p class="lab-verdict" id="signal-status" role="status">All packets retained. Every sample is recovered.</p>
<details class="lab-data"><summary>Inspect the values and original addresses</summary>
<div class="table-scroll"><table><caption>Original, reconstructed and residual values</caption>
<thead><tr><th scope="col">Address</th><th scope="col">Original</th><th scope="col">Rebuilt</th><th scope="col">Residual</th></tr></thead><tbody id="signal-table"></tbody></table></div></details>
</div></div>
<details class="lab-reason"><summary>What changes when the packets get finer?</summary>
<p>Addresses start at zero. With four packets, packet r holds addresses congruent to r modulo four. The even packet splits into packets 0 and 2; the odd packet splits into packets 1 and 3. With eight packets, each of those splits again. Returning each sample to its address reconstructs the signal. Here, a discarded sample is replaced by zero, and the residual is original minus rebuilt.</p></details>
SIGNAL_SOURCES</section>
<section class="lab-panel" id="recovery" aria-labelledby="recovery-title">
<div class="lab-panel-heading"><div><p class="lab-kicker">03 / Information and recovery</p>
<h2 id="recovery-title">One summary. Two possible inputs.</h2>
<p>The summary keeps only x₁ + x₂. Move along the line to see which questions still have a unique answer.</p></div>
<button type="button" data-reset="recovery" disabled>Reset experiment</button></div>
<div class="lab-workspace"><fieldset class="lab-controls" id="recovery-controls" disabled>
<legend>Choose the question</legend><label class="lab-label" for="recovery-question">What should the summary recover?</label>
<select id="recovery-question"><option value="first">The first coordinate · x₁</option><option value="sum">Twice the sum · 2x₁ + 2x₂</option><option value="difference">The difference · x₁ − x₂</option><option value="custom" disabled>Custom linear question</option></select>
<p class="lab-control-note">For a custom question F(x) = ax₁ + bx₂, change a and b below.</p>
RECOVERY_SLIDERS
</fieldset><div class="lab-visual">RECOVERY_DIAGRAM
<div class="lab-collision"><div><span>Input u</span><output id="recovery-u">(1, 0)</output><span id="recovery-u-answer">F(u) = 1</span></div>
<div class="lab-shared"><span>Same summary</span><output id="recovery-summary">1</output><span>x₁ + x₂</span></div>
<div><span>Input v</span><output id="recovery-v">(0, 1)</output><span id="recovery-v-answer">F(v) = 0</span></div></div>
<p class="lab-verdict" id="recovery-status" role="status">Same summary, different answers. The first coordinate cannot be recovered from the sum alone.</p>
<p class="lab-caption" id="recovery-rule">The summary erases the direction (1, −1), but the requested answer changes along it.</p>
</div></div>
<details class="lab-reason"><summary>When is recovery possible?</summary>
<p>For R(x) = x₁ + x₂ and F(x) = ax₁ + bx₂ on the real plane, exact recovery from R for every input is possible exactly when a = b. Then F(x) = aR(x) and the recovery rule is G(s) = as. Otherwise, u and v above have equal sums but answers differing by a − b. No function of the sum alone can give both answers, even if that function is nonlinear.</p></details>
RECOVERY_SOURCES</section>
<p class="lab-footnote">These bounded integer experiments illustrate finite constructions over the real numbers. The linked explanations give the arguments, sources, and recorded proof coverage.</p>
</div>'''
    replacements = {
        'MATRIX': matrix, 'BLOCKS': blocks,
        'VECTOR_SLIDERS': slider('vector-0', 'Input coordinate x₁', 2, -5, 5) + slider('vector-1', 'Input coordinate x₂', 3, -5, 5),
        'SIGNAL_SLIDERS': ''.join(slider(f'sample-{i}', f'Sample {i}', i+1, -8, 8) for i in range(8)),
        'RECOVERY_SLIDERS': (slider('summary', 'Summary s = x₁ + x₂', 1, -4, 4)
                             + slider('position', 'Move along the same summary · x₁', 1, -4, 4)
                             + slider('coefficient-a', 'Coefficient a', 1, -3, 3)
                             + slider('coefficient-b', 'Coefficient b', 0, -3, 3)),
        'PACKET_DIAGRAM': diagram('packet-diagram', 'Four connections from input coordinates to output coordinates'),
        'SIGNAL_DIAGRAM': diagram('signal-diagram', 'Original signal, reconstruction and residual, by address'),
        'RECOVERY_DIAGRAM': diagram('recovery-diagram', 'Two inputs on the line x one plus x two equals the same summary'),
        'PACKET_SOURCES': sources('packets', 'PACKETS', 'Continue to the hand calculation, operator identity, and Paper I source links.'),
        'SIGNAL_SOURCES': sources('refinement', 'REFINEMENT', 'Continue to the address calculation and Paper II refinement sources.'),
        'RECOVERY_SOURCES': sources('recovery', 'RECOVERY', 'Continue to the collision argument, Paper III, and Realization Boundaries.'),
    }
    for key, value in replacements.items():
        body = body.replace(key, value)
    def asset(name):
        version = hashlib.sha256((site.root/'website/assets'/name).read_bytes()).hexdigest()[:12]
        return 'assets/'+name+'?v='+version
    body = '<link rel="stylesheet" href="'+asset('interactive-diagrams.css')+'">'+body
    body += '<script type="module" src="'+asset('interactive-diagrams.js')+'"></script>'
    site.page('interactive.html', 'Interactive mathematics', body)
    for name, title, works in [
        ('packets', 'Reconstruct an operator', ['paper-i']),
        ('refinement', 'Refine a signal', ['paper-ii', 'paper-v']),
        ('recovery', 'Recover information from a summary', ['paper-iii', 'realization-boundaries']),
    ]:
        site.search.append(dict(title='Interactive diagram: '+title, group='Collection', kind='Examples',
                                work_ids=works, url='interactive.html#'+name,
                                text='Interactive mathematics diagrams sliders matrix blocks packets reconstruction signal refinement residual information loss summary recovery '+title))
