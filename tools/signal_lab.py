"""Publish the larger signal and representation laboratory."""
import hashlib
from interactive_diagrams import slider, diagram


def build(site):
    body = '''<div class="math-lab signal-workbench" id="signal-lab">
<header class="sl-intro"><p class="lab-kicker">Signals / compression / noise</p>
<h1>Signal laboratory</h1>
<p>Compare Haar, cosine, and sample representations under one coefficient budget. Explore compression and controlled noise.</p></header>
<noscript><p class="notice">Enable JavaScript to run this laboratory. The <a href="collection/demonstrations/HAAR_LAB.html">worked Haar calculation</a> is available without it.</p></noscript>
<p class="lab-caption" id="sl-status" role="status"></p>
<label class="lab-share-fallback" id="sl-link-fallback" for="sl-link" hidden>Experiment link<input type="url" id="sl-link" readonly></label>
<p class="lab-error" id="sl-error" role="status" hidden></p>
<div class="sl-primary-grid"><details class="sl-setup" id="sl-setup" open><summary>Experiment controls<span id="sl-controls-summary">64 samples · 12 kept · noise ±4</span></summary>
<fieldset class="sl-controls" id="sl-controls" disabled><legend>Build the experiment</legend>
<div class="sl-form-grid"><label class="lab-label" for="sl-shape">Reference signal
<select id="sl-shape"><option value="steps">Steps and a spike</option><option value="wave">Cosine wave</option><option value="chirp">Chirp</option><option value="spikes">Sparse impulses</option><option value="triangle">Triangle</option><option value="mixed">Mixed structure</option><option value="custom" disabled>Imported samples</option></select></label>
<label class="lab-label" for="sl-size">Samples
<select id="sl-size"><option>16</option><option>32</option><option selected>64</option><option>128</option><option>256</option></select></label>
<label class="lab-label" for="sl-policy">Retain coefficients by
<select id="sl-policy"><option value="energy">Largest weighted energy</option><option value="magnitude">Largest raw magnitude</option><option value="prefix">Coarse / low-frequency prefix</option></select></label></div>
<div class="sl-slider-grid">BUDGET NOISE</div>
<div class="sl-seed-row"><button type="button" id="sl-new-noise">New noise realization</button>
<p class="lab-control-note" id="sl-seed-note">Seed 17 · bounded integer noise.</p></div>
<details class="sl-generator"><summary>Waveform parameters and seed</summary>
<label class="lab-label" for="sl-seed">Noise seed<input type="number" id="sl-seed" min="0" max="4294967295" step="1" value="17" required></label>
<div class="sl-slider-grid">AMPLITUDE CYCLES</div>
<p class="lab-control-note" id="sl-shape-note">Preset samples are rounded to whole numbers. Imported data supplies its own sample count.</p></details>
</fieldset></details>
<section class="sl-main-plot" aria-labelledby="sl-reconstruction-title">
<h2 id="sl-reconstruction-title">Signal reconstruction <span id="sl-active-name">· Haar wavelets</span></h2>
<div class="sl-legend"><span class="sl-reference">Clean reference</span><span class="sl-observed">Observed with noise</span><span class="sl-reconstruction">Selected reconstruction</span></div>
SIGNAL_PLOT
<fieldset class="sl-inspector" id="sl-sample-inspector" disabled><legend class="sr-only">Inspect a sample</legend>ADDRESS
<p class="sl-readout" id="sl-sample-status" role="status"></p></fieldset>
</section></div>
<div class="sl-actions"><button type="button" id="sl-copy" data-sl-action disabled>Copy experiment link</button>
<label class="lab-label" for="sl-export-kind">Export
<select id="sl-export-kind" disabled><option value="signal">Signal CSV</option><option value="curves">Error curves CSV</option><option value="experiment">Experiment JSON</option></select></label>
<button type="button" id="sl-export" data-sl-action disabled>Download</button>
<button type="button" id="sl-reset" data-sl-action disabled>Reset lab</button></div>
<section aria-labelledby="sl-comparison-title"><h2 id="sl-comparison-title">Same budget. Three representations.</h2>
<p class="lab-caption" id="sl-policy-note"></p>
<div class="table-scroll"><table class="sl-comparison"><caption id="sl-budget-summary">12 of 64 coefficients retained in each representation</caption>
<thead><tr><th scope="col">Representation</th><th scope="col">Error to reference · Σ(x̂ − x)²</th><th scope="col">Discarded energy · Σ(y − x̂)²</th></tr></thead>
<tbody>COMPARISON_ROWS</tbody></table></div>
<p class="lab-caption">Select a representation to inspect its reconstruction and coefficients. The original noise energy is <output id="sl-noise-energy">—</output>.</p></section>
<div class="sl-analysis-grid"><section aria-labelledby="sl-frontier-title"><h2 id="sl-frontier-title">When does adding detail help?</h2>
<p class="lab-caption">Reference error for every coefficient budget. Click the graph or move the budget slider.</p>
<div class="sl-legend"><span class="sl-haar">Haar wavelets</span><span class="sl-cosine">Cosine modes</span><span class="sl-samples">Sample coordinates</span></div>
FRONTIER_PLOT
<button type="button" id="sl-best" data-sl-action disabled>Use minimum for selected representation</button>
<p class="lab-caption" id="sl-best-note"></p></section>
<section aria-labelledby="sl-coefficients-title"><h2 id="sl-coefficients-title">Which components survive?</h2>
<p class="lab-caption">Weighted coefficient energy. Solid bars are kept; outlined bars are omitted. Tap a bar to inspect it.</p>
COEFFICIENT_PLOT
<fieldset class="sl-inspector" id="sl-coefficient-inspector" disabled><legend class="sr-only">Inspect a coefficient</legend>COEFFICIENT
<p class="sl-readout" id="sl-coefficient-status" role="status"></p></fieldset>
<h3>Selected contribution, if retained</h3>BASIS_PLOT
</section></div>
<details class="sl-data"><summary>Import your own signal</summary>
<p id="sl-import-help">Use 16, 32, 64, 128, or 256 whole-number reference samples from −64 to 64. Paste values, or import a numeric CSV with a reference, value, or sample column. A saved experiment JSON restores the complete setup.</p>
<p class="lab-caption">Imported samples become the known reference. The noise control adds simulated noise afterward; this experiment does not estimate an unknown real-world clean signal.</p>
<fieldset class="sl-import-controls" id="sl-import-controls" disabled>
<legend class="sr-only">Import signal data</legend><label class="lab-label" for="sl-file">CSV, text, or saved experiment JSON · up to 64 KiB</label>
<input type="file" id="sl-file" accept=".csv,.txt,.json,text/csv,text/plain,application/json" aria-describedby="sl-import-help">
<label class="lab-label" for="sl-paste">Paste reference samples</label>
<textarea id="sl-paste" rows="4" aria-describedby="sl-import-help" placeholder="2, 2, 2, 2, 6, 6, 6, 6, -4, -4, 12, -4, 4, 4, 4, 4"></textarea>
<button type="button" id="sl-apply">Use these samples</button></fieldset></details>
<details class="sl-data" id="sl-table-details"><summary>Inspect every sample</summary>
<div class="table-scroll"><table><caption>Selected reconstruction at every address</caption><thead><tr><th scope="col">Address</th><th scope="col">Reference</th><th scope="col">Observed</th><th scope="col">Reconstructed</th><th scope="col">Discarded residual</th></tr></thead><tbody id="sl-sample-table"></tbody></table></div></details>
<details class="sl-data"><summary>Conventions and how to interpret the comparison</summary>
<p>The reference x is known. Observations y = x + noise use a fixed seeded integer sequence. The reconstruction x̂ uses the selected coefficients of y. The two errors compare x̂ with x and with y respectively; they answer different questions.</p>
<p>Haar analysis uses pair averages and half-differences. Its global mean has weight N and a level-j detail has weight 2ʲ. Cosine analysis uses the orthonormal DCT-II, with a separately normalized constant mode. Sample coordinates use the identity basis. Each representation has exactly N coefficients.</p>
<p>For an orthogonal basis, omitting a coefficient loses its weighted squared magnitude. Keeping the largest weighted energies therefore minimizes squared error to the observed samples at a fixed budget, in exact arithmetic. Largest raw magnitude is a different rule for the averaging-normalized Haar coefficients. Prefix order means coarse-to-fine Haar details, low-to-high cosine modes, or the earliest sample addresses.</p>
<p>The minimum button uses the known reference curve, choosing its smallest budget within 10⁻¹⁰ times max(1, reference energy) of the minimum. It is an experimental reference comparison, not a rule for choosing a budget when the clean signal is unknown. Cosine calculations use floating-point arithmetic; plotted and displayed values are numerical approximations.</p>
<p><a href="interactive.html">Guided interactive diagrams</a> · <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.dct.html">DCT normalization convention</a> · <a href="collection/demonstrations/HAAR_LAB.html">Worked Haar calculation</a> · <a href="read/wavelet-polyphase.html">Wavelet and polyphase walkthrough</a></p></details>
</div>'''
    rows = ''.join('<tr><th scope="row"><button type="button" data-sl-basis="'+key+'" aria-pressed="'+('true' if key == 'haar' else 'false')+'" disabled>'+label+'</button></th>'
                   '<td><output id="sl-'+key+'-reference">—</output></td><td><output id="sl-'+key+'-observed">—</output></td></tr>'
                   for key, label in [('haar', 'Haar wavelets'), ('cosine', 'Cosine modes'), ('samples', 'Sample coordinates')])
    replacements = {
        'BUDGET': slider('sl-budget', 'Retained coefficients', 12, 0, 64),
        'NOISE': slider('sl-noise', 'Noise amplitude · ±', 4, 0, 16),
        'AMPLITUDE': slider('sl-amplitude', 'Waveform amplitude', 16, 1, 24),
        'CYCLES': slider('sl-cycles', 'Frequency parameter', 3, 1, 16),
        'ADDRESS': slider('sl-address', 'Inspect sample address', 32, 0, 63),
        'COEFFICIENT': slider('sl-coefficient', 'Inspect coefficient index', 1, 0, 63),
        'SIGNAL_PLOT': diagram('sl-signal-chart', 'Reference, noisy observations and selected signal reconstruction'),
        'FRONTIER_PLOT': diagram('sl-frontier-chart', 'Reference reconstruction errors for all coefficient budgets and all three representations'),
        'COEFFICIENT_PLOT': diagram('sl-coefficient-chart', 'Weighted coefficient energy and retained selection'),
        'BASIS_PLOT': diagram('sl-basis-chart', 'Selected coefficient contribution at every sample address'),
        'COMPARISON_ROWS': rows,
    }
    # Replace longer placeholders before their shorter prefixes.
    for key in sorted(replacements, key=len, reverse=True):
        body = body.replace(key, replacements[key])
    def asset(name):
        return 'assets/'+name+'?v='+hashlib.sha256((site.root/'website/assets'/name).read_bytes()).hexdigest()[:12]
    script = (site.root/'website/assets/signal-lab.js').read_text(encoding='utf-8')
    script = script.replace("'./signal-lab-core.mjs'", "'./signal-lab-core.mjs?v="+hashlib.sha256((site.root/'website/assets/signal-lab-core.mjs').read_bytes()).hexdigest()[:12]+"'")
    site.write('assets/signal-lab.js', script)
    body = '<link rel="stylesheet" href="'+asset('interactive-diagrams.css')+'"><link rel="stylesheet" href="'+asset('signal-lab.css')+'">'+body
    body += '<script type="module" src="assets/signal-lab.js?v='+hashlib.sha256(script.encode()).hexdigest()[:12]+'"></script>'
    site.page('signal-lab.html', 'Signal laboratory', body)
    site.search.append(dict(title='Signal laboratory: compare Haar, cosine and sample representations',group='Collection',kind='Examples',
                            work_ids=['paper-ii','paper-v','information-realization'],url='signal-lab.html',
                            text='Interactive signal laboratory wavelets DCT cosine compression denoising coefficient budget weighted energy error curves seeded noise CSV JSON import export'))
