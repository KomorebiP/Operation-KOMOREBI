"""Publish the exact finite-dimensional recovery laboratory."""
import hashlib


def build(site):
    body = '''<div class="math-lab recovery-lab" id="recovery-lab">
<header class="rl-intro"><p class="lab-kicker">Interactive mathematics / information and recovery</p>
<h1>What did your<br><em>summary forget?</em></h1>
<p>Choose what you measure and what you want to know. Find an exact recovery rule, or two inputs your measurements cannot distinguish. Then repair the summary.</p>
<p class="lab-local">Exact rational arithmetic · 2–4 input coordinates · Runs in your browser</p></header>
<noscript><p class="notice">Enable JavaScript to run the laboratory. <a href="collection/demonstrations/RECOVERY.html">Read the worked recovery calculation</a> without it.</p></noscript>
<nav class="rl-jumps" aria-label="In this laboratory"><a href="#rl-guide">Guided investigation</a><a href="#rl-setup-title">Edit an experiment</a><a href="#rl-motion-title">Explore the pictures</a><a href="#rl-vocabulary">Notation and access help</a></nav>
<details class="rl-guide" id="rl-guide" open><summary>New here? Follow a four-step investigation</summary>
<p>You need addition and the idea that a function gives one answer for each input. Start with this puzzle: (1, 0) and (0, 1) have the same total, but different first coordinates. What could a rule using only that total know?</p>
<div class="rl-lesson-buttons" role="group" aria-label="Load a guided step">
<button type="button" data-rl-lesson="0" disabled>1. Lose information</button><button type="button" data-rl-lesson="1" disabled>2. Recover an answer</button><button type="button" data-rl-lesson="2" disabled>3. Compare questions</button><button type="button" data-rl-lesson="3" disabled>4. Repair the summary</button></div>
<div id="rl-lesson-content" hidden><h2 id="rl-lesson-title" tabindex="-1"></h2><p id="rl-lesson-idea"></p>
<p class="rl-lesson-example" id="rl-lesson-example"></p><p id="rl-lesson-task"></p>
<p class="lab-caption" id="rl-lesson-state"></p>
<fieldset class="rl-prediction"><legend id="rl-prediction-prompt"></legend><div id="rl-prediction-choices"></div></fieldset>
<p id="rl-prediction-feedback" role="status" aria-atomic="true"></p>
<div class="rl-lesson-actions"><button type="button" id="rl-lesson-reload">Reload this step</button><a href="#rl-setup-title">Try it in the workspace ↓</a><button type="button" id="rl-lesson-next">Next guided step →</button></div></div></details>
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
</fieldset><p class="lab-error" id="rl-error" role="status" hidden></p>
<details class="rl-equations"><summary>Read the rows as equations</summary><p id="rl-equation-input"></p><div id="rl-equations"></div>
<p>A row gives the coefficient of each input coordinate. A zero skips that coordinate; a negative coefficient subtracts it. An unchecked measurement supplies no information to the recovery rule.</p></details></section>
<section class="rl-result" aria-labelledby="rl-result-title"><h2 id="rl-result-title">2. Test recovery</h2>
<div class="rl-verdict" id="rl-verdict"><p>Loading the exact calculation…</p></div>
<dl class="rl-metrics"><div><dt>Independent measurements</dt><dd id="rl-rank">—</dd></div><div><dt>Invisible directions</dt><dd id="rl-nullity">—</dd></div><div><dt>Extra measurements needed</dt><dd id="rl-missing">—</dd></div></dl>
<div id="rl-question-tabs" class="rl-question-tabs" role="group" aria-label="Inspect a question"></div>
<div class="rl-certificate" id="rl-certificate"></div>
<div class="rl-worked"><h3 id="rl-worked-title"></h3><div class="rl-formula" id="rl-worked-calculation"></div><p id="rl-worked-text"></p></div>
<div class="rl-repair"><h3>3. Make the summary sufficient</h3>
<p id="rl-repair-note">The rank calculation finds the smallest number of additional linear measurements needed for these questions.</p>
<button type="button" id="rl-repair" disabled>Build a sufficient summary</button>
<button type="button" id="rl-undo" disabled>Undo summary repair</button>
<p class="lab-caption" id="rl-repair-status" role="status"></p></div>
</section></div>
<section class="rl-motion" aria-labelledby="rl-motion-title"><div><p class="lab-kicker">Same information / different inputs</p>
<h2 id="rl-motion-title">Move in an invisible direction.</h2>
<p id="rl-motion-note">An invisible direction w satisfies Rw = 0. Moving from x to x + tw leaves every enabled measurement unchanged.</p></div>
<p class="rl-control-help" id="rl-motion-help">Use the arrow keys on a slider, or the − and + buttons beside t. Home and End move to the ends. At t = 0 the inputs coincide. The pictures update without animation; exact values and descriptions are available below.</p>
<fieldset id="rl-motion-controls" disabled><legend class="sr-only">Explore inputs with the same summary</legend>
<div id="rl-base-inputs" class="rl-base-inputs"></div>
<div class="lab-slider"><label for="rl-offset">Move along the invisible direction · t<output id="rl-offset-value" for="rl-offset" aria-live="off">1</output></label>
<div class="rl-stepper"><button type="button" id="rl-step-back" aria-label="Decrease t by one">−</button><input type="range" id="rl-offset" min="-4" max="4" step="1" value="1" aria-describedby="rl-motion-help rl-motion-note"><button type="button" id="rl-step-forward" aria-label="Increase t by one">+</button></div></div></fieldset>
<div class="rl-geometry">
<figure id="rl-fiber-figure"><h3 id="rl-fiber-title">Which inputs share this summary?</h3><div id="rl-fiber-chart" class="lab-diagram" role="img" aria-labelledby="rl-fiber-title" aria-describedby="rl-fiber-description"></div><figcaption id="rl-fiber-description"></figcaption></figure>
<figure><h3 id="rl-response-title">Does the answer change as you move?</h3><div id="rl-response-chart" class="lab-diagram" role="img" aria-labelledby="rl-response-title" aria-describedby="rl-response-description"></div><figcaption id="rl-response-description"></figcaption>
<p class="lab-caption">Solid line and circles: selected answer at x + tw. Dashed line: its value at the base input x. The vertical marker shows the current t. Graphs round fractions for display.</p></figure></div>
<details class="rl-detail"><summary>Read all nine graph samples as exact values</summary><div class="table-scroll" id="rl-samples"></div><p>A flat graph along one direction alone does not prove recovery. The exact certificate tests every invisible direction. A nonzero slope supplies a collision.</p></details>
<details class="rl-detail"><summary>Compare each input coordinate and measurement</summary>
<div class="rl-motion-charts"><div><h3>Input coordinates change</h3><div id="rl-input-chart" class="lab-diagram" role="img" aria-label="Original and moved input coordinates"></div></div>
<div><h3>Enabled measurements stay fixed</h3><div id="rl-summary-chart" class="lab-diagram" role="img" aria-label="Original and moved measurement values"></div></div></div>
<p class="lab-caption">Filled marks: x. Outlined marks: x + tw. Plots approximate the exact fractions shown below.</p></details>
<div class="table-scroll"><table class="rl-values"><caption>Exact values for the two inputs</caption><thead><tr><th scope="col">Quantity</th><th scope="col">At x</th><th scope="col">At x + tw</th></tr></thead><tbody id="rl-values"></tbody></table></div>
</section>
<details class="rl-detail" id="rl-vocabulary"><summary>Notation, everyday meanings, and access help</summary>
<dl class="rl-vocabulary"><div><dt>Input x</dt><dd>The full list of numbers you started with. A coordinate is one number in that list.</dd></div>
<div><dt>Measurement y = Rx</dt><dd>A weighted sum of input coordinates. Each enabled row of R supplies one number in the summary y.</dd></div>
<div><dt>Question F</dt><dd>A weighted sum you want to know. Each row of F is a separate question; F₁ and F₂ name different answers.</dd></div>
<div><dt>Recovery rule G</dt><dd>A rule that calculates the requested answers using only the summary. For linear recovery, F = GR says the measurement rows combine to give the question rows.</dd></div>
<div><dt>Kernel / invisible direction w</dt><dd>A change to the input that every enabled measurement erases: Rw = 0. A fiber is the whole set of inputs with one fixed summary.</dd></div>
<div><dt>Rank and nullity</dt><dd>Rank counts independent measurements. Nullity counts independent invisible directions. They add up to the number of input coordinates.</dd></div>
<div><dt>Certificate</dt><dd>An exact identity you can check: either weights that reconstruct the question, or two indistinguishable inputs with different answers.</dd></div></dl>
<p>Tab moves between controls. Space toggles a measurement; Enter activates a button. Arrow keys adjust sliders. Select a question button to inspect its certificate. Guided-step buttons replace the experiment and keep focus; “Next guided step” moves focus to the new explanation.</p>
<p>Every graph has a visible description and a table of exact values. The two-coordinate picture shows a full fiber; higher-dimensional experiments use the answer-versus-t graph. Line styles and mark shapes distinguish series as well as color. Wide tables can be focused and scrolled with arrow keys.</p>
<p>Results update as you type. Invalid entries are marked and described; the last valid calculation stays visible until you fix them. <a href="collection/demonstrations/RECOVERY.html">The written worked example</a> is available without JavaScript. See <a href="collection/ACCESSIBILITY.html">accessibility and reading options</a> for the wider collection.</p></details>
<details class="rl-detail"><summary>Inspect the kernel and the row reduction</summary>
<p id="rl-kernel-note"></p><div id="rl-kernel"></div>
<p id="rl-row-note"></p><div class="table-scroll" id="rl-rref"></div>
<details><summary>See the row operations</summary><ol id="rl-operations"></ol></details>
<p>The same row operations give a matrix E with E R_active = R_reduced. The recovery coefficients are formed from E, so their product with the original enabled rows can be checked directly.</p>
<div class="table-scroll" id="rl-transform"></div></details>
<details class="rl-detail"><summary>Go deeper: why do these certificates settle the question?</summary>
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

    guidance = (site.root/'website/assets/recovery-lab-guidance.mjs').read_text(encoding='utf-8')
    guidance = guidance.replace("'./recovery-lab-core.mjs'", "'./"+version('recovery-lab-core.mjs').removeprefix('assets/')+"'")
    site.write('assets/recovery-lab-guidance.mjs', guidance)
    script = (site.root/'website/assets/recovery-lab.js').read_text(encoding='utf-8')
    script = script.replace("'./recovery-lab-core.mjs'", "'./"+version('recovery-lab-core.mjs').removeprefix('assets/')+"'")
    script = script.replace("'./recovery-lab-guidance.mjs'", "'./"+version('recovery-lab-guidance.mjs',guidance.encode()).removeprefix('assets/')+"'")
    site.write('assets/recovery-lab.js', script)
    body = '<link rel="stylesheet" href="'+version('interactive-diagrams.css')+'"><link rel="stylesheet" href="'+version('recovery-lab.css')+'">'+body
    body += '<script type="module" src="'+version('recovery-lab.js',script.encode())+'"></script>'
    site.page('recovery-lab.html', 'Recovery laboratory', body)
    site.search.append(dict(title='Recovery laboratory: exact information loss, factorization, and minimal repair',
                            group='Collection', kind='Examples', work_ids=['paper-iii','realization-boundaries'],
                            url='recovery-lab.html', text='Interactive exact rational matrices recovery information summary kernel nullspace row reduction rank factorization certificate collision witness minimal extra measurements repair multiple questions guided investigation worked examples fiber geometry answer graph notation keyboard access'))
