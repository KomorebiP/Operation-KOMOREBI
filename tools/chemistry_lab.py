"""Publish the source-bound chemistry experiment and its static reading route."""
import hashlib
import html
import json

PAGE='chemistry-lab.html'


def build(site):
    def asset(name,raw=None):
        raw=raw if raw is not None else (site.root/'website/assets'/name).read_bytes()
        return 'assets/'+name+'?v='+hashlib.sha256(raw).hexdigest()[:12]
    raw=(site.root/'website/assets/chemistry/lab-v1.json').read_bytes()
    data=json.loads(raw)
    if data['version']!=1: raise ValueError('Unknown chemistry lab data')
    source=json.loads((site.root/'manifests/chemistry-stage14.json').read_bytes())
    if data['archive_sha256']!=source['sha256']: raise ValueError('Chemistry lab source mismatch')
    site.write('assets/chemistry/lab-v1.json',raw.decode())
    for name in ['chemistry-lab.css','chemistry-lab-core.mjs']:
        site.write('assets/'+name,(site.root/'website/assets'/name).read_text(encoding='utf-8'))
    script=(site.root/'website/assets/chemistry-lab.js').read_text(encoding='utf-8')
    script=script.replace("'./chemistry-lab-core.mjs'","'./"+asset('chemistry-lab-core.mjs').removeprefix('assets/')+"'")
    site.write('assets/chemistry-lab.js',script)
    body='''
<div class="cl-page" id="chemistry-lab" data-source="'''+asset('chemistry/lab-v1.json')+'''" data-sha256="'''+hashlib.sha256(raw).hexdigest()+'''">
<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="index.html">Home</a> / <a href="collection/COMPUTATIONAL_CHEMISTRY.html">Computational chemistry</a></nav>
<header class="cl-hero"><p class="cl-eyebrow">Computational chemistry laboratory</p>
<h1>Three actions.<br><em>One recovered operator.</em></h1>
<p class="cl-lead">Nine states. Twenty-one unknown coefficients. Reveal what each probe tells you, then see how imperfect data change the answer.</p>
<p>A probe supplies a known nine-component vector and receives the full vector H v. The experiment uses the published real, three-orbital family with two alpha electrons and one beta electron.</p>
<nav class="cl-route" aria-label="Chemistry learning route"><a href="#cl-experiment">1. Experiment</a><a href="#cl-worked">2. Worked calculation</a><a href="read/computational-chemistry/three-queries.html">3. Theorem</a><a href="read/computational-chemistry/reproduce.html">4. Replay</a></nav>
</header>
<p id="cl-load-status" role="status">Loading the experiment and checking its fixture identity. The worked calculation below is available now.</p><button id="cl-retry" type="button" hidden>Retry loading the experiment</button>
<noscript><p>The interactive experiment needs JavaScript. Read the worked calculation below, then follow the theorem or download the replay bundle.</p></noscript>
<div id="cl-experiment" hidden>
<section class="cl-toolbar" aria-label="Choose an experiment"><div><label for="cl-example">Example</label><select id="cl-example">'''+''.join('<option value="'+x['id']+'">'+html.escape(x['title'])+'</option>' for x in data['samples'])+'''</select></div><div class="cl-actions"><button type="button" id="cl-reset">Reset example</button><a id="cl-permalink" href="chemistry-lab.html">Link to this experiment</a></div><p id="cl-context"></p></section>
<section class="cl-panel" aria-labelledby="cl-probes-title"><div class="cl-section-heading"><div><p class="cl-eyebrow">01 / Reveal the actions</p><h2 id="cl-probes-title">How much is still hidden?</h2></div><div class="cl-probe-buttons" role="group" aria-label="Number of available probes"><button type="button" data-probes="1" aria-pressed="false">1 probe</button><button type="button" data-probes="2" aria-pressed="true">2 probes</button><button type="button" data-probes="3" aria-pressed="false">3 probes</button></div></div>
<div class="cl-stats"><div><span>Independent constraints</span><strong id="cl-rank"></strong></div><div><span>Hidden directions</span><strong id="cl-nullity"></strong></div><div><span>Operator coefficients</span><strong>21</strong></div></div>
<p class="cl-result" id="cl-probe-result"></p><div class="cl-rank-track" id="cl-rank-track" aria-hidden="true"></div>
<p>The probe demonstration uses exact actions of the decoded estimate. For the H10 example these are educational reference actions; the uncertainty calculation below uses the original binary64 action cache.</p>
<div class="cl-matrices"><figure><figcaption>Reference operator H</figcaption><div id="cl-h-map"></div></figure><figure><figcaption id="cl-alternative-caption">Indistinguishable operator H + ΔH</figcaption><div id="cl-alternative-map"></div></figure></div>
<p id="cl-witness-description"></p><p class="cl-caption">Each square is one matrix entry. The symbols +, −, and · show its sign or zero. Outlined squares mark changed entries; the exact tables retain every value.</p>
<details><summary>Inspect the probes, actions, and exact ambiguity witness</summary><p>Rows are determinant indices 0–8. The three fixed probes have squared norm 3 and are mutually orthogonal. The action table lists one nine-component output per available probe.</p><div id="cl-probe-table"></div><div id="cl-action-table"></div><div id="cl-witness-table"></div></details>
</section>
<section class="cl-panel" aria-labelledby="cl-uncertainty-title"><p class="cl-eyebrow">02 / Account for uncertainty</p><h2 id="cl-uncertainty-title">An answer with its error bound.</h2>
<p>This section always uses all three cached actions. Adjust an assumed error cap or the broadening. These controls do not measure the true error.</p>
<div class="cl-uncertainty-grid"><div class="cl-controls">
<label for="cl-error">Action-error budget ε <output id="cl-error-value" for="cl-error"></output></label><input type="range" id="cl-error" min="0" max="7" step="1" value="2" aria-describedby="cl-error-help"><p id="cl-error-help">Multiply the example’s stored action-error cap. The norm combines all 27 action entries.</p>
<label for="cl-source">Source-error cap δ <output id="cl-source-value" for="cl-source"></output></label><input type="range" id="cl-source" min="0" max="4" step="1" value="1" aria-describedby="cl-source-help"><p id="cl-source-help">A dimensionless bound on the source-vector error. Zero fixes the source exactly.</p>
<label for="cl-eta">Broadening η <output id="cl-eta-value" for="cl-eta"></output></label><input type="range" id="cl-eta" min="0" max="4" step="1" value="4" aria-describedby="cl-eta-help"><p id="cl-eta-help">Positive broadening in Hartree. Smaller values resolve finer energy features and can amplify uncertainty.</p>
<p id="cl-energy"></p><p id="cl-cap-note" class="cl-callout"></p>
</div><figure class="cl-response"><figcaption>Complex resolvent response</figcaption><div id="cl-disk"></div><p id="cl-disk-description"></p></figure></div>
<p id="cl-consistency" class="cl-result"></p><dl class="cl-metrics" id="cl-metrics"></dl>
<div class="cl-callout" id="cl-positivity"></div>
<details><summary>Read the error calculation and units</summary><p>The exact decoder fits the 27 cached values to the 21-parameter family. Let d² be the squared residual. A compatible operator exists in the full linear family precisely when d² ≤ ε².</p><p>When consistent, the operator error is at most r_H = √(20(ε² − d²)). The response disk has radius R_g = ‖b̂‖² r_H / η² + δ(2‖b̂‖ + δ) / η. This is an upper bound, without a claim of optimality.</p><p>With Hamiltonian energies in Hartree, ε, d, and r_H have energy units. The response and its radius have inverse-energy units. The source is dimensionless. The source-resolved density is −Im(g)/π; its interval half-width is R_g/π. It is not the total density of states.</p><div id="cl-bound-table"></div><p>Square roots are enclosed outward by rational multiples of 10⁻³⁰, with exact squares retained exactly. The browser computes the decoder and bounds with BigInt fractions and verifies the saved response solution by substitution. Graphs and short decimal labels are rounded.</p></details>
</section>
<section class="cl-panel" aria-labelledby="cl-certificate-title"><p class="cl-eyebrow">03 / Follow the evidence</p><h2 id="cl-certificate-title">Keep the assumptions with the answer.</h2>
<p id="cl-certificate-summary"></p><div class="cl-actions"><button type="button" id="cl-download">Download this experiment’s certificate</button><a id="cl-original-certificate" href="assets/chemistry/stage14/chemistry_stage14/exact-audit-001/example_certificate.json">Published source certificate</a><a href="assets/chemistry/validation-v1/Stage14_Validated_Replay.zip">Download the validated replay bundle</a></div>
<details><summary>Inspect the exact experiment certificate</summary><p>A browser-generated certificate records this experiment’s assumptions and rational bounds. It is distinct from the published source certificate and is not independent review or proof-assistant verification.</p><pre id="cl-certificate" tabindex="0" role="group" aria-label="Exact experiment certificate; scroll horizontally if needed"></pre></details>
<details><summary>Source identity and verification limits</summary><p id="cl-provenance"></p><p>The fixed model and fixtures are derived from the hash-bound Stage 14 export. Exact browser checks cover the displayed identities and conditional bounds. They do not establish full-H10 physical accuracy, Coulomb realizability, priority, or a runtime advantage.</p><p><a href="assets/chemistry/lab-v1.json">Inspect the lab fixtures</a> · <a href="assets/chemistry/stage14/export.json">Inspect the original export manifest</a> · <a href="read/computational-chemistry/review.html">Read the proof self-review</a></p></details>
</section><p id="cl-announcement" class="cl-sr-only" role="status" aria-live="polite" aria-atomic="true"></p></div>
<section class="cl-panel" id="cl-worked" aria-labelledby="cl-worked-title"><p class="cl-eyebrow">Worked calculation / Available without JavaScript</p><h2 id="cl-worked-title">Why does the third action matter?</h2>
<ol class="cl-worked-steps"><li><strong>Specify the family.</strong> The operator is a real symmetric 9-by-9 matrix in a particular 21-dimensional integral-symmetry family. The energy shift is included.</li><li><strong>Choose the fixed probes.</strong> The three columns are v₁ = (−1,0,0,−1,0,0,1,0,0), v₂ = (0,1,0,0,0,−1,0,1,0), and v₃ = (0,0,1,0,1,0,0,0,1).</li><li><strong>Ask for complete actions.</strong> Each answer H vⱼ has nine components. Two actions give at most 18 scalar constraints, so some nonzero family perturbation ΔH remains invisible. The lab displays an exact such perturbation for the selected prefix of probes.</li><li><strong>Add the third action.</strong> The fixed 27-by-21 action map has rank 21. An exact rational left inverse recovers every operator coefficient for consistent noiseless data. The written theorem also proves the lower bound for deterministic adaptive probes.</li></ol>
<h3>A numerical error calculation you can check by hand</h3><p>Suppose the cache residual is zero, the action-error cap is ε = 1/4096 Hartree, the source is normalized, its error cap is δ = 1/8192, and η = 1 Hartree. Then r_H = √20/4096 &lt; 0.001092 Hartree, and R_g = √20/4096 + (1/8192)(2 + 1/8192) &lt; 0.001337 per Hartree. The “Exact rational example” opens with these settings.</p>
<p>If d &gt; ε, the cache is inconsistent with the assumed family and cap, so no response enclosure is reported. If ε = d, the compatible set is a singleton. Positivity of one estimate, feasibility of the positive subclass, and positivity of every compatible operator are separate questions.</p>
<p class="cl-callout">Three action queries are three complete classical matrix-vector products. The count does not describe three scalar measurements or three quantum experiments. The H10 example certifies arithmetic in a declared reduced model; its numerical radius does not bound frozen-core or finite-basis approximation error.</p>
<nav class="cl-route" aria-label="Continue studying chemistry"><a href="collection/COMPUTATIONAL_CHEMISTRY.html">Research overview</a><a href="read/computational-chemistry/notation.html">Notation and units</a><a href="read/computational-chemistry/normal-form.html">Normal-form derivation</a><a href="read/computational-chemistry/three-queries.html">Theorem and error bounds</a><a href="read/computational-chemistry/model-error.html">Physical model-error obligations</a><a href="read/computational-chemistry/reproduce.html">Replay instructions</a></nav>
</section><details class="cl-panel"><summary>Keyboard, graphs, and reading help</summary><p>Tab moves between controls. Enter or Space activates buttons. Arrow keys adjust the three sliders. Each graph has a visible text description and exact values in the expandable tables. Tables and certificate blocks can be focused and scrolled with arrow keys. Controls preserve focus when results change. The experiment link retains the example, probe count, and slider positions.</p><p>Without JavaScript, the worked calculation, theorem, and replay links remain available. The laboratory does not upload data or require an account. See <a href="collection/ACCESSIBILITY.html">accessibility and reporting problems</a>.</p></details></div>
'''
    body='<link rel="stylesheet" href="'+asset('chemistry-lab.css')+'">'+body+'<script type="module" src="'+asset('chemistry-lab.js',script.encode())+'"></script>'
    site.page(PAGE,'Computational chemistry laboratory: three-query recovery',body,'https://github.com/KomorebiP/Operation-KOMOREBI/blob/'+site.revision+'/tools/chemistry_lab.py')
    site.search.append(dict(title='Computational chemistry laboratory: three-query recovery',group='Collection',kind='Examples',work_ids=[],url=PAGE,text='Interactive Hamiltonian recovery nine states three probes 21 parameters exact rational ambiguity witness noise response disk broadening consistency positivity certificate H10 reduced model worked calculation replay'))
    return dict(examples=len(data['samples']),fixture_bytes=len(raw),new_physical_accuracy_claim=False)
