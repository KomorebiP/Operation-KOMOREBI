"""Publish the exact local coupled-function investigation."""
import hashlib


def build(site):
    body = r'''<div class="sf-lab" id="special-functions-lab">
<header class="sf-intro"><p class="sf-kicker">Special Functions / coupled contractions</p>
<h1>One beginning.<br><em>Four scales to explore.</em></h1>
<p>Both functions begin at zero with slope one. Change where they sample each other, then follow the difference from exact coefficients to a bounded approximation.</p>
<p class="sf-local">Exact rational coefficients · Local series bounds · Runs in your browser</p></header>
<noscript><p class="notice">Enable JavaScript to calculate. The <a href="read/monographs-special-functions/coupled-contractions.html">coupled-functions chapter</a> and the equations below are available without it.</p></noscript>
<nav class="sf-jumps" aria-label="In this laboratory"><a href="#sf-workspace">Experiment</a><a href="#sf-recurrence">Inspect the recurrence</a><a href="#sf-coefficients">Exact coefficients</a><a href="#sf-mathematics">Why the bound works</a></nav>
<section class="sf-guidance" aria-labelledby="sf-question"><h2 id="sf-question">Follow a change through the calculation</h2>
<div class="sf-starters"><button type="button" data-sf-preset="default" disabled><strong>Same slope, different curves</strong><span>Compare the first coefficients of the worked pair.</span></button>
<button type="button" data-sf-preset="symmetric" disabled><strong>Make the pair agree</strong><span>Set every scale to 1/2 and inspect the exact series.</span></button>
<button type="button" data-sf-preset="compare" disabled><strong>Change one address</strong><span>Compare q = 1/3 with q = 2/3, keeping the other scales.</span></button></div>
<p id="sf-lesson">Start at degree three: u₁ = qr/3 and v₁ = ab/3. Then inspect degree five to see both components' earlier coefficients contribute.</p></section>
<div class="sf-toolbar"><button type="button" id="sf-share" disabled>Copy experiment link</button><button type="button" id="sf-csv" disabled>Download exact coefficients</button><button type="button" id="sf-reset" disabled>Reset</button></div>
<p id="sf-status" role="status" aria-atomic="true"></p>
<label id="sf-share-fallback" for="sf-share-link" hidden>Experiment link<input type="url" id="sf-share-link" readonly></label>
<div class="sf-workspace" id="sf-workspace"><section class="sf-panel sf-controls" aria-labelledby="sf-controls-title"><h2 id="sf-controls-title">Choose the four scales</h2>
<div class="sf-equations arithmatex">\[U'(z)=1+U(qz)V(rz),\qquad V'(z)=1+U(az)V(bz).\]</div>
<form id="sf-form"><fieldset id="sf-fields" disabled><legend class="sr-only">Exact experiment settings</legend>
<p id="sf-input-help" class="sf-note">Use fractions such as 2/3, with denominator 1–100. Each scale must be strictly between zero and one.</p>
<div class="sf-scale-grid"><label for="sf-q">q · U in the first equation<input id="sf-q" type="text" value="1/3" inputmode="text" maxlength="16" aria-describedby="sf-input-help sf-error" autocomplete="off" spellcheck="false"></label>
<label for="sf-r">r · V in the first equation<input id="sf-r" type="text" value="2/3" inputmode="text" maxlength="16" aria-describedby="sf-input-help sf-error" autocomplete="off" spellcheck="false"></label>
<label for="sf-a">a · U in the second equation<input id="sf-a" type="text" value="1/2" inputmode="text" maxlength="16" aria-describedby="sf-input-help sf-error" autocomplete="off" spellcheck="false"></label>
<label for="sf-b">b · V in the second equation<input id="sf-b" type="text" value="3/4" inputmode="text" maxlength="16" aria-describedby="sf-input-help sf-error" autocomplete="off" spellcheck="false"></label></div>
<div class="sf-scale-grid sf-budget"><label for="sf-count">Coefficients per component<input id="sf-count" type="number" value="12" min="1" max="16" step="1" aria-describedby="sf-count-help sf-error"></label>
<label for="sf-radius">Disk radius R<input id="sf-radius" type="text" value="1" maxlength="16" aria-describedby="sf-radius-help sf-error" autocomplete="off" spellcheck="false"></label></div>
<p id="sf-count-help" class="sf-note">N coefficients retain indices 0 to N − 1, through degree 2N − 1. Choose 1–16.</p>
<p id="sf-radius-help" class="sf-note">Use a rational radius from 0 to 4/3. The picture shows the real interval [−R, R]; the bound applies throughout the complex disk |z| ≤ R.</p>
<details class="sf-comparison" id="sf-comparison"><summary>Compare a second set of scales</summary>
<label class="sf-check" for="sf-compare"><input type="checkbox" id="sf-compare">Show comparison curves</label>
<div class="sf-scale-grid"><label for="sf-cq">Comparison q<input id="sf-cq" type="text" value="1/2" maxlength="16" aria-describedby="sf-input-help sf-error"></label><label for="sf-cr">Comparison r<input id="sf-cr" type="text" value="1/2" maxlength="16" aria-describedby="sf-input-help sf-error"></label><label for="sf-ca">Comparison a<input id="sf-ca" type="text" value="1/2" maxlength="16" aria-describedby="sf-input-help sf-error"></label><label for="sf-cb">Comparison b<input id="sf-cb" type="text" value="1/2" maxlength="16" aria-describedby="sf-input-help sf-error"></label></div>
<button type="button" id="sf-pin">Copy current scales to comparison</button><p class="sf-note">Both pairs use the same coefficient count and disk radius.</p></details>
<button type="submit" class="sf-primary">Update experiment</button></fieldset></form>
<p id="sf-error" class="sf-error" role="alert" hidden></p></section>
<section class="sf-panel sf-picture" aria-labelledby="sf-plot-title"><div class="sf-panel-heading"><p class="sf-kicker">From coefficients to curves</p><h2 id="sf-plot-title">A shared tangent, a different path</h2></div>
<div id="sf-plot" class="sf-plot" role="img" aria-labelledby="sf-plot-title" aria-describedby="sf-plot-description"></div>
<p class="sf-legend"><span class="sf-key sf-u">● U</span><span class="sf-key sf-v">■ V</span><span>Solid: current pair</span><span id="sf-comparison-key" hidden>Dashed: comparison pair</span></p>
<p id="sf-plot-description" class="sf-note">The odd Taylor polynomials are plotted on the selected real interval.</p>
<div class="sf-metrics"><div><span>Highest retained degree</span><strong id="sf-degree">—</strong></div><div><span>Uniform omitted-series bound</span><strong id="sf-bound">—</strong><small id="sf-bound-decimal"></small></div></div>
<p class="sf-note">The tail bound controls the omitted series. Plotted decimal evaluation has additional floating-point roundoff; the graph is not an interval plot.</p>
<details class="sf-detail"><summary>Read five graph samples as exact fractions</summary><div class="sf-table-scroll" tabindex="0" role="region" aria-label="Exact graph sample table"><table><caption>Truncated polynomials at rational addresses</caption><thead><tr><th scope="col">x</th><th scope="col">Current U</th><th scope="col">Current V</th><th scope="col" class="sf-comparison-column">Comparison U</th><th scope="col" class="sf-comparison-column">Comparison V</th></tr></thead><tbody id="sf-samples"></tbody></table></div></details>
<p id="sf-difference" class="sf-note" hidden></p></section></div>
<section class="sf-panel sf-inspector" id="sf-recurrence" aria-labelledby="sf-recurrence-title"><p class="sf-kicker">Inspect the construction</p><h2 id="sf-recurrence-title">Where does this coefficient come from?</h2>
<p>For indices n ≥ 1, the two equations use the same earlier products uᵢvⱼ. Their scale weights differ. Index zero is supplied by the initial slopes u₀ = v₀ = 1. Choose a coefficient from the current pair and inspect every contribution.</p>
<label class="sf-term-label" for="sf-term">Coefficient to inspect<select id="sf-term" disabled><option value="2">Index 2 · degree 5</option></select></label>
<div class="sf-equations arithmatex">\[u_n=\frac{1}{2n+1}\sum_{i+j=n-1}q^{2i+1}r^{2j+1}u_i v_j,\qquad v_n=\frac{1}{2n+1}\sum_{i+j=n-1}a^{2i+1}b^{2j+1}u_i v_j.\]</div>
<p id="sf-term-description"></p>
<div class="sf-table-scroll" tabindex="0" role="region" aria-label="Exact recurrence contributions"><table><caption id="sf-term-caption">Every contribution, including division by 2n + 1</caption><thead><tr><th scope="col">i</th><th scope="col">j</th><th scope="col">Shared uᵢvⱼ</th><th scope="col">Contribution to uₙ</th><th scope="col">Contribution to vₙ</th></tr></thead><tbody id="sf-terms"></tbody><tfoot><tr><th scope="row" colspan="3">Exact sum</th><td id="sf-sum-u"></td><td id="sf-sum-v"></td></tr></tfoot></table></div>
<p class="sf-note">Open a long fraction to read all digits. The coefficient table and CSV retain every exact numerator and denominator.</p></section>
<section class="sf-panel" id="sf-coefficients" aria-labelledby="sf-coefficients-title"><h2 id="sf-coefficients-title">Keep the exact calculation</h2>
<p>These are ordinary Taylor coefficients in U(z) = Σuₙz²ⁿ⁺¹ and V(z) = Σvₙz²ⁿ⁺¹. Every even coefficient is zero. The derivative at the origin of order 2n + 1 is (2n + 1)! times the displayed coefficient.</p>
<div class="sf-table-scroll" tabindex="0" role="region" aria-label="Exact Taylor coefficient table"><table><caption>Retained odd coefficients</caption><thead><tr><th scope="col">Index n</th><th scope="col">Degree</th><th scope="col">Current uₙ</th><th scope="col">Current vₙ</th><th scope="col" class="sf-comparison-column">Comparison uₙ</th><th scope="col" class="sf-comparison-column">Comparison vₙ</th></tr></thead><tbody id="sf-coefficient-rows"></tbody></table></div></section>
<section class="sf-panel" id="sf-mathematics" aria-labelledby="sf-math-title"><h2 id="sf-math-title">A finite picture with a stated error</h2>
<p>For positive scales at most one, induction on the recurrence gives 0 &lt; uₙ, vₙ ≤ 2⁻ⁿ. If N coefficients are retained, the first omitted index is N. With ρ = R²/2 &lt; 1, the geometric tail gives</p>
<div class="sf-equations arithmatex">\[\left|F(z)-\sum_{n=0}^{N-1}c_nz^{2n+1}\right|\le\sum_{n=N}^{\infty}2^{-n}R^{2n+1}=\frac{R\rho^N}{1-\rho},\qquad |z|\le R.\]</div>
<p>Here F is U or V. The chosen radius cap, 4/3, lies below √2. This elementary bound is deliberately shared by all admitted scale sets; it does not estimate the actual error of a particular pair. A coarse bound can be larger than the plotted values. The manuscript develops sharper bounds on larger disks.</p>
<p>The browser evaluates a finite exact rational recurrence using integer fractions. Its plots illustrate finite Taylor polynomials. The general existence, entire growth, and inverse theorems belong to the manuscript and its recorded formal companions; this laboratory adds no Lean coverage.</p>
<details class="sf-detail"><summary>A closed-form check and an investigation to try</summary><p>If all four scales equal 1/2, the pair agrees with √2 sinh(z/√2), so uₙ = vₙ = 1/(2ⁿ(2n + 1)!). Load “Make the pair agree” and check the first four rows. Then copy the current scales to the comparison and change only q. Find the first coefficient that changes, and inspect the term that causes it.</p><p>Now keep the scales fixed and increase the coefficient count. The exact bound decreases geometrically at a fixed positive radius. Increasing the radius changes the bound and the displayed interval; it does not change the coefficients.</p></details>
<nav class="sf-reading" aria-label="Continue with the Special Functions sources"><a href="collection/SPECIAL_FUNCTIONS.html">Five families and reading volumes</a><a href="read/monographs-special-functions/coupled-contractions.html">Coupled-functions chapter</a><a href="read/monographs-special-functions/index.html">Monograph and proof appendices</a><a href="collection/works/monographs-special-functions.html#lean">Formal statements and evidence</a><a href="playground.html#special-functions-coupled">Edit the Python experiment</a></nav>
</section></div>'''
    assets = site.root / 'website/assets'

    def version(name, raw=None):
        data = (assets/name).read_bytes() if raw is None else raw
        return 'assets/'+name+'?v='+hashlib.sha256(data).hexdigest()[:12]

    for name in ('special-functions-lab-core.mjs', 'special-functions-lab.css'):
        site.write('assets/'+name, (assets/name).read_text(encoding='utf-8'))
    script = (assets/'special-functions-lab.js').read_text(encoding='utf-8')
    script = script.replace("'./special-functions-lab-core.mjs'", "'./"+version('special-functions-lab-core.mjs').removeprefix('assets/')+"'")
    site.write('assets/special-functions-lab.js', script)
    body = '<link rel="stylesheet" href="'+version('special-functions-lab.css')+'">'+body
    body += '<script type="module" src="'+version('special-functions-lab.js', script.encode())+'"></script>'
    site.page('special-functions-lab.html', 'Coupled-function laboratory', body)
    site.search.append(dict(title='Coupled-function laboratory: exact coefficients and local tail bounds',
                            group='Collection', kind='Examples', work_ids=['monographs-special-functions'],
                            url='special-functions-lab.html',
                            text='Special Functions coupled contractions rational scales recurrence coefficient contributions Taylor series truncation error disk radius compare functions exact fractions CSV experiment link'))
