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
<label class="lab-share-fallback" id="sl-link-fallback" for="sl-link" hidden><span id="sl-link-label">Experiment link</span><input type="url" id="sl-link" readonly></label>
<p class="lab-error" id="sl-error" role="status" hidden></p>
<details class="sl-data sl-starters" id="sl-starters"><summary>Start with a comparison experiment</summary>
<p class="lab-caption" id="sl-starter-note">Each starter opens a reference experiment and adds two named runs to your notebook. Existing saved runs are kept.</p>
<div class="sl-starter-grid">
<article><h2>Sharp edges</h2><p>Compare Haar and cosine reconstructions of steps and a spike, keeping eight coefficients in each.</p><button type="button" data-sl-starter="edges" disabled>Compare sharp edges</button></article>
<article><h2>A cosine-like tone</h2><p>Keep one component in each representation. The generated reference is rounded to whole numbers.</p><button type="button" data-sl-starter="tone" disabled>Compare a tone</button></article>
<article><h2>Does more detail help?</h2><p>Compare six and 32 Haar coefficients from the same noisy observations. Inspect their errors against the known reference.</p><button type="button" data-sl-starter="noise" disabled>Compare detail in noise</button></article>
<article><h2>Magnitude or energy?</h2><p>Compare two Haar ranking rules on a 16-sample benchmark, retaining one coefficient under each rule.</p><button type="button" data-sl-starter="ranking" disabled>Compare ranking rules</button></article>
</div></details>
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
<h2 id="sl-reconstruction-title"><span id="sl-main-title">Signal reconstruction</span> <span id="sl-active-name">· Haar wavelets</span></h2>
<div class="sl-legend sl-signal-legend"><span class="sl-reference">Clean reference</span><span class="sl-observed">Observed with noise</span><span class="sl-reconstruction">Selected reconstruction</span></div>
<div class="sl-edit-toolbar"><button type="button" id="sl-draw" data-sl-action aria-pressed="false" disabled>Draw reference</button>
<button type="button" id="sl-undo" disabled>Undo edit</button><button type="button" id="sl-redo" disabled>Redo edit</button></div>
<p class="lab-caption" id="sl-draw-help" hidden>Drag across the plot to draw whole-number reference samples from −64 to 64. Crossed addresses are filled between pointer positions. Finish drawing to see the noisy reconstruction. Escape cancels a stroke and leaves drawing mode.</p>
SIGNAL_PLOT
<fieldset class="sl-inspector" id="sl-sample-inspector" disabled><legend class="sr-only">Inspect a sample</legend>ADDRESS
<p class="sl-readout" id="sl-sample-status" role="status"></p></fieldset>
<details class="sl-exact-edit"><summary>Edit the selected sample precisely</summary><fieldset id="sl-edit-controls" disabled><legend class="sr-only">Set a reference sample</legend>
<label class="lab-label" for="sl-edit-value">Reference value · whole number from −64 to 64<input type="number" id="sl-edit-value" min="-64" max="64" step="1" value="0" required></label>
<button type="button" id="sl-set-sample">Set selected sample</button></fieldset></details>
<p class="sl-readout" id="sl-edit-status" role="status"></p>
</section></div>
<div class="sl-actions"><button type="button" id="sl-copy" data-sl-action disabled>Copy experiment link</button>
<button type="button" id="sl-save-run" data-sl-action disabled>Save run to notebook</button>
<label class="lab-label" for="sl-export-kind">Export
<select id="sl-export-kind" disabled><option value="signal">Signal CSV</option><option value="curves">Error curves CSV</option><option value="experiment">Experiment JSON</option></select></label>
<button type="button" id="sl-export" data-sl-action disabled>Download</button>
<button type="button" id="sl-reset" data-sl-action disabled>Reset lab</button></div>
<details class="sl-data sl-notebook" id="sl-notebook"><summary>Experiment notebook <span id="sl-notebook-count">0 / 12 saved runs</span></summary>
<p class="lab-caption">Save competing setups, rename their rows, and restore them later. Runs are saved in this browser. Download notebook JSON to keep or exchange the collection; importing appends runs and recomputes their results. Reset lab keeps the notebook.</p>
<p class="lab-caption" id="sl-notebook-status" role="status"></p>
<div class="sl-notebook-actions"><button type="button" id="sl-notebook-export" disabled>Download notebook JSON</button>
<button type="button" id="sl-notebook-csv" disabled>Download results CSV</button>
<label class="lab-label" for="sl-notebook-file">Import notebook JSON · up to 64 KiB<input type="file" id="sl-notebook-file" accept=".json,application/json" disabled></label></div>
<p id="sl-notebook-empty" class="lab-caption">Save the current run, change its budget or representation, then save another run to compare.</p>
<div class="table-scroll" id="sl-notebook-table-wrap" hidden><table class="sl-notebook-table"><caption>Saved runs · squared errors recomputed from their settings</caption>
<thead><tr><th scope="col">Run name</th><th scope="col">Setup</th><th scope="col">Retained</th><th scope="col">Error to reference · Σ(x̂ − x)²</th><th scope="col">Discarded energy · Σ(y − x̂)²</th><th scope="col">Actions</th></tr></thead>
<tbody id="sl-notebook-rows"></tbody></table></div>
<div id="sl-notebook-comparison" hidden><h2>Compare saved reconstructions</h2>
<div class="sl-shared-preview" id="sl-shared-preview" hidden><p id="sl-shared-note" role="status">Shared comparison preview. Your notebook is unchanged.</p>
<div class="sl-pair-actions"><button type="button" id="sl-shared-save">Save both runs to notebook</button><button type="button" id="sl-shared-close">Close shared preview</button></div></div>
<div class="sl-pair-controls"><label class="lab-label" for="sl-compare-a">Run A<select id="sl-compare-a"></select></label>
<label class="lab-label" for="sl-compare-b">Run B<select id="sl-compare-b"></select></label></div>
<p class="sl-readout" id="sl-pair-summary" role="status"></p>
<div id="sl-pair-plot" hidden>
<fieldset class="sl-pair-inspector" id="sl-pair-inspector" disabled><legend class="sr-only">Inspect the saved comparison</legend>
<label class="lab-label" for="sl-pair-view">Plot view<select id="sl-pair-view"><option value="overlay">Reconstructions</option><option value="error">Signed error to reference</option><option value="difference">Difference · B − A</option></select></label>
<p class="lab-caption" id="sl-pair-view-note">Click the plot or use the sample slider to inspect both runs.</p>
<div class="sl-legend"><span class="sl-reference" id="sl-pair-reference-label">Clean reference</span><span class="sl-cosine" id="sl-pair-a-label">Run A</span><span class="sl-samples" id="sl-pair-b-label">Run B</span><span class="sl-difference" id="sl-pair-difference-label" hidden>Difference · B − A</span></div>
PAIR_PLOT PAIR_ADDRESS
<p class="sl-readout" id="sl-pair-gap" role="status"></p>
<div class="sl-pair-actions"><button type="button" id="sl-pair-largest">Inspect largest difference</button><button type="button" id="sl-pair-csv">Download comparison CSV</button><button type="button" id="sl-pair-copy">Copy comparison link</button></div>
<p class="sl-readout" id="sl-pair-share-status" role="status"></p>
</fieldset>
<dl class="sl-pair-readouts" aria-label="Selected sample values"><div><dt>Sample address</dt><dd><output id="sl-pair-sample">—</output></dd></div>
<div><dt>Reference</dt><dd><output id="sl-pair-reference">—</output></dd></div><div><dt>Observed</dt><dd><output id="sl-pair-observed">—</output></dd></div>
<div><dt>Reconstruction A</dt><dd><output id="sl-pair-a">—</output></dd></div><div><dt>Reconstruction B</dt><dd><output id="sl-pair-b">—</output></dd></div>
<div><dt>A − reference</dt><dd><output id="sl-pair-error-a">—</output></dd></div><div><dt>B − reference</dt><dd><output id="sl-pair-error-b">—</output></dd></div>
<div><dt>Difference · B − A</dt><dd><output id="sl-pair-difference">—</output></dd></div></dl>
<details id="sl-pair-table-details" class="sl-pair-table"><summary>Inspect every comparison sample</summary><div class="table-scroll"><table><caption>Signed errors use reconstruction minus reference; differences use B minus A.</caption>
<thead><tr><th scope="col">Address</th><th scope="col">Reference</th><th scope="col">Observed</th><th scope="col">Run A</th><th scope="col">Run B</th><th scope="col">A − reference</th><th scope="col">B − reference</th><th scope="col">B − A</th></tr></thead><tbody id="sl-pair-table"></tbody></table></div></details>
</div></div>
</details>
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
<p class="lab-caption" id="sl-best-note"></p>
<details class="sl-targets" id="sl-target-details"><summary>Find a budget for a quality target</summary>
<fieldset id="sl-target-controls" disabled><legend class="sr-only">Find the smallest qualifying coefficient budgets</legend>
<div class="sl-target-form"><label class="lab-label" for="sl-target-metric">Quality measure<select id="sl-target-metric"><option value="energy">Observed energy retained</option><option value="reference">RMS error to known reference</option></select></label>
<label class="lab-label" for="sl-target-value"><span id="sl-target-label">Target energy retained · %</span><input type="number" id="sl-target-value" min="0" max="100" step="any" value="95" required></label></div>
<p class="lab-caption" id="sl-target-note"></p><p class="lab-error" id="sl-target-error" role="status" hidden></p>
<div class="table-scroll"><table class="sl-target-table"><caption>Smallest qualifying budget in each representation</caption><thead><tr><th scope="col">Basis</th><th scope="col">Kept</th><th scope="col" id="sl-target-result-label">Energy retained</th><th scope="col">Apply</th></tr></thead><tbody id="sl-target-rows"></tbody></table></div>
<button type="button" id="sl-target-save" disabled>Save qualifying runs to notebook</button>
<p class="lab-caption" id="sl-target-capacity" role="status"></p>
<p class="lab-caption">RMS means √(squared error / sample count). Reference-error targets use the known clean signal and are experimental comparisons. Every coefficient budget is checked; a target may be unreachable. Numerical comparisons allow 10⁻¹⁰ × max(1, the relevant signal energy) in squared-error units. A zero-energy observation meets energy-retention targets with zero coefficients.</p>
</fieldset></details></section>
<section aria-labelledby="sl-coefficients-title"><h2 id="sl-coefficients-title">Which components survive?</h2>
<p class="lab-caption">Weighted coefficient energy. Solid bars are kept; outlined bars are omitted. Tap a bar to inspect it.</p>
COEFFICIENT_PLOT
<fieldset class="sl-inspector" id="sl-coefficient-inspector" disabled><legend class="sr-only">Inspect a coefficient</legend>COEFFICIENT
<p class="sl-readout" id="sl-coefficient-status" role="status"></p></fieldset>
<h3>Selected contribution, if retained</h3>BASIS_PLOT
</section></div>
<details class="sl-data" id="sl-import"><summary>Import your own signal</summary>
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
        'PAIR_PLOT': diagram('sl-pair-chart', 'Two saved reconstructions of the same observed signal'),
        'PAIR_ADDRESS': slider('sl-pair-address', 'Inspect comparison sample', 32, 0, 63),
        'COMPARISON_ROWS': rows,
    }
    # Replace longer placeholders before their shorter prefixes.
    for key in sorted(replacements, key=len, reverse=True):
        body = body.replace(key, replacements[key])
    def asset(name):
        return 'assets/'+name+'?v='+hashlib.sha256((site.root/'website/assets'/name).read_bytes()).hexdigest()[:12]
    def version_model(script):
        return script.replace("'./signal-lab-core.mjs'", "'./signal-lab-core.mjs?v="+hashlib.sha256((site.root/'website/assets/signal-lab-core.mjs').read_bytes()).hexdigest()[:12]+"'")
    workspace = version_model((site.root/'website/assets/signal-lab-workspace.mjs').read_text(encoding='utf-8'))
    site.write('assets/signal-lab-workspace.mjs', workspace)
    script = version_model((site.root/'website/assets/signal-lab.js').read_text(encoding='utf-8'))
    script = script.replace("'./signal-lab-workspace.mjs'", "'./signal-lab-workspace.mjs?v="+hashlib.sha256(workspace.encode()).hexdigest()[:12]+"'")
    site.write('assets/signal-lab.js', script)
    body = '<link rel="stylesheet" href="'+asset('interactive-diagrams.css')+'"><link rel="stylesheet" href="'+asset('signal-lab.css')+'">'+body
    body += '<script type="module" src="assets/signal-lab.js?v='+hashlib.sha256(script.encode()).hexdigest()[:12]+'"></script>'
    site.page('signal-lab.html', 'Signal laboratory', body)
    site.search.append(dict(title='Signal laboratory: compare Haar, cosine and sample representations',group='Collection',kind='Examples',
                            work_ids=['paper-ii','paper-v','information-realization'],url='signal-lab.html',
                            text='Interactive signal laboratory quality target minimum budget retained energy RMS threshold starter experiments draw edit undo reference notebook compare saved runs signed residual errors differences inspection wavelets DCT cosine compression denoising coefficient budget weighted energy error curves seeded noise CSV JSON import export'))
