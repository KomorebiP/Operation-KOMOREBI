"""Publish the exact finite-dimensional recovery laboratory."""
import hashlib


def build(site):
    body = '''<div class="math-lab recovery-lab" id="recovery-lab">
<header class="rl-intro"><p class="lab-kicker">Interactive mathematics / information and recovery</p>
<h1>What did your<br><em>summary forget?</em></h1>
<p>Choose what you measure and what you want to know. Find an exact recovery rule, or two inputs your measurements cannot distinguish. Then repair the summary.</p>
<p class="lab-local">Exact rational arithmetic · 2–4 input coordinates · Runs in your browser</p></header>
<noscript><p class="notice">Enable JavaScript to run the laboratory. <a href="collection/demonstrations/RECOVERY.html">Read the worked recovery calculation</a> without it.</p></noscript>
<section class="rl-starters" aria-labelledby="rl-starters-title"><h2 id="rl-starters-title">Start with a question</h2>
<div id="rl-presets" class="rl-preset-grid">
<button type="button" data-rl-preset="sum" disabled>A sum loses a coordinate</button>
<button type="button" data-rl-preset="sufficient" disabled>Recover without knowing x</button>
<button type="button" data-rl-preset="partial" disabled>Two questions, one obstruction</button>
<button type="button" data-rl-preset="redundant" disabled>More rows, no more information</button>
<button type="button" data-rl-preset="fractions" disabled>An exact fractional rule</button>
<button type="button" data-rl-preset="invertible" disabled>Recover the whole input</button></div></section>
<div class="rl-toolbar"><button type="button" id="rl-share" disabled>Copy experiment link</button>
<button type="button" id="rl-export" disabled>Download calculation JSON</button>
<button type="button" id="rl-reset" disabled>Reset experiment</button></div>
<p class="lab-caption" id="rl-status" role="status"></p>
<label id="rl-share-fallback" class="lab-share-fallback" for="rl-share-link" hidden>Experiment link<input type="url" id="rl-share-link" readonly></label>
<div class="rl-workspace"><section class="rl-setup" aria-labelledby="rl-setup-title"><h2 id="rl-setup-title">1. Define the information</h2>
<fieldset id="rl-controls" disabled><legend class="sr-only">Measurements and questions</legend>
<label class="lab-label" for="rl-dimension">Input coordinates<select id="rl-dimension"><option value="2" selected>2 coordinates</option><option value="3">3 coordinates</option><option value="4">4 coordinates</option></select></label>
<p class="lab-control-note" id="rl-entry-help">Enter whole numbers from −99 to 99, or fractions such as −2/3 with denominator 1–99. Rows act on column vectors over the real numbers.</p>
<h3>What can you measure? <span>y = Rx</span></h3>
<p class="lab-control-note">Each checked row supplies one measurement. Uncheck a row to see what information disappears.</p>
<div class="table-scroll rl-input-table" id="rl-r-matrix"></div>
<button type="button" class="lab-secondary" id="rl-add-measurement">Add a measurement</button>
<h3>What do you want to know? <span>F(x)</span></h3>
<p class="lab-control-note">Each row is a linear question. Recovery must work for every input x.</p>
<div class="table-scroll rl-input-table" id="rl-f-matrix"></div>
<button type="button" class="lab-secondary" id="rl-add-question">Add a question</button>
</fieldset><p class="lab-error" id="rl-error" role="status" hidden></p></section>
<section class="rl-result" aria-labelledby="rl-result-title"><h2 id="rl-result-title">2. Test recovery</h2>
<div class="rl-verdict" id="rl-verdict" role="status"><p>Loading the exact calculation…</p></div>
<dl class="rl-metrics"><div><dt>Independent measurements</dt><dd id="rl-rank">—</dd></div><div><dt>Invisible directions</dt><dd id="rl-nullity">—</dd></div><div><dt>Extra measurements needed</dt><dd id="rl-missing">—</dd></div></dl>
<div id="rl-question-tabs" class="rl-question-tabs" role="group" aria-label="Inspect a question"></div>
<div class="rl-certificate" id="rl-certificate" aria-live="polite"></div>
<div class="rl-repair"><h3>3. Make the summary sufficient</h3>
<p id="rl-repair-note">The rank calculation finds the smallest number of additional linear measurements needed for these questions.</p>
<button type="button" id="rl-repair" disabled>Build a sufficient summary</button>
<button type="button" id="rl-undo" disabled>Undo summary repair</button>
<p class="lab-caption" id="rl-repair-status" role="status"></p></div>
</section></div>
<section class="rl-motion" aria-labelledby="rl-motion-title"><div><p class="lab-kicker">Same information / different inputs</p>
<h2 id="rl-motion-title">Move in an invisible direction.</h2>
<p id="rl-motion-note">An invisible direction w satisfies Rw = 0. Moving from x to x + tw leaves every enabled measurement unchanged.</p></div>
<fieldset id="rl-motion-controls" disabled><legend class="sr-only">Explore inputs with the same summary</legend>
<div id="rl-base-inputs" class="rl-base-inputs"></div>
<div class="lab-slider"><label for="rl-offset">Move along the invisible direction · t<output id="rl-offset-value" for="rl-offset">1</output></label>
<input type="range" id="rl-offset" min="-4" max="4" step="1" value="1"></div></fieldset>
<div class="rl-motion-charts"><div><h3>Input coordinates change</h3><div id="rl-input-chart" class="lab-diagram" role="img" aria-label="Original and moved input coordinates"></div></div>
<div><h3>Enabled measurements stay fixed</h3><div id="rl-summary-chart" class="lab-diagram" role="img" aria-label="Original and moved measurement values"></div></div></div>
<p class="lab-caption">Filled marks: x. Outlined marks: x + tw. Plots approximate the exact fractions shown below.</p>
<div class="table-scroll"><table class="rl-values"><caption>Exact values for the two inputs</caption><thead><tr><th scope="col">Quantity</th><th scope="col">At x</th><th scope="col">At x + tw</th></tr></thead><tbody id="rl-values"></tbody></table></div>
</section>
<details class="rl-detail"><summary>Inspect the kernel and the row reduction</summary>
<p id="rl-kernel-note"></p><div id="rl-kernel"></div>
<p id="rl-row-note"></p><div class="table-scroll" id="rl-rref"></div>
<details><summary>See the row operations</summary><ol id="rl-operations"></ol></details>
<p>The same row operations give a matrix E with E R_active = R_reduced. The recovery coefficients are formed from E, so their product with the original enabled rows can be checked directly.</p>
<div class="table-scroll" id="rl-transform"></div></details>
<details class="rl-detail"><summary>Why do these certificates settle the question?</summary>
<p>Let R: ℝⁿ → ℝᵐ be the enabled measurements, and let F: ℝⁿ → ℝᵏ be the requested linear answers. Exact recovery from R for every input is possible if and only if ker R ⊆ ker F. Equivalently, every row of F lies in the row space of R, so a matrix G satisfies F = GR.</p>
<p>If F = GR, the rule y ↦ Gy recovers F(x) from y = Rx. If a vector w has Rw = 0 but Fw ≠ 0, then x and x + w have identical measurements and different answers. This rules out every recovery function of those measurements, including nonlinear functions.</p>
<p>To see the converse directly, take a basis of ker R and extend it to a basis of ℝⁿ. When F vanishes on ker R, assign G(Rv) = Fv on the images of the added basis vectors. These images form a basis of im R. Extend G linearly to ℝᵐ. Then GR = F.</p>
<p>The minimum number of extra scalar linear measurements is rank([R; F]) − rank(R), where [R; F] means stacking the rows. Each added row increases rank by at most one. Adding a basis of the missing question directions attains this bound. “Build a sufficient summary” keeps an independent subset of the enabled rows and adds the required question rows; redundant and disabled rows are removed.</p>
<p>These statements concern unrestricted real inputs and exact linear measurements. The displayed matrices have rational entries and are reduced using exact integer fractions. The laboratory does not model noisy measurements, restricted input sets, or approximate recovery. Its calculations add no Lean coverage to the manuscripts.</p></details>
<nav class="rl-reading" aria-label="Continue the recovery investigation"><a href="interactive.html#recovery">Introductory recovery diagram</a><a href="collection/demonstrations/RECOVERY.html">Worked collision argument</a><a href="collection/examples/10_KERNELS.html">Kernels and fibers</a><a href="collection/examples/25_REPAIR_MENUS.html">Repair directions</a><a href="collection/works/paper-iii.html">Paper III</a><a href="collection/works/realization-boundaries.html">Realization Boundaries</a></nav>
</div>'''

    def version(name, raw=None):
        if raw is None:
            raw = (site.root/'website/assets'/name).read_bytes()
        return 'assets/'+name+'?v='+hashlib.sha256(raw).hexdigest()[:12]

    script = (site.root/'website/assets/recovery-lab.js').read_text(encoding='utf-8')
    script = script.replace("'./recovery-lab-core.mjs'", "'./"+version('recovery-lab-core.mjs').removeprefix('assets/')+"'")
    site.write('assets/recovery-lab.js', script)
    body = '<link rel="stylesheet" href="'+version('interactive-diagrams.css')+'"><link rel="stylesheet" href="'+version('recovery-lab.css')+'">'+body
    body += '<script type="module" src="'+version('recovery-lab.js',script.encode())+'"></script>'
    site.page('recovery-lab.html', 'Recovery laboratory', body)
    site.search.append(dict(title='Recovery laboratory: exact information loss, factorization, and minimal repair',
                            group='Collection', kind='Examples', work_ids=['paper-iii','realization-boundaries'],
                            url='recovery-lab.html', text='Interactive exact rational matrices recovery information summary kernel nullspace row reduction rank factorization certificate collision witness minimal extra measurements repair multiple questions'))
