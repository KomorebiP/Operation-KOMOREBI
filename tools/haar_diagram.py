"""The multilevel Haar experiment's maintained teaching interface."""

DEFAULT_SIGNAL = [2,2,2,2,6,6,6,6,-4,-4,12,-4,4,4,4,4]


def panel(slider, diagram):
    samples = ''.join(
        f'<label for="haar-sample-{i}"><span>{i}</span><input type="number" '
        f'id="haar-sample-{i}" aria-label="Haar signal sample {i}" min="-16" max="16" '
        f'step="1" value="{value}" required></label>'
        for i, value in enumerate(DEFAULT_SIGNAL))
    return '''<section class="lab-panel" id="haar" aria-labelledby="haar-title">
<div class="lab-panel-heading"><div><p class="lab-kicker">04 / Multilevel Haar decomposition</p>
<h2 id="haar-title">Keep the structure. Choose the detail.</h2>
<p>Analyze a 16-sample signal through four levels of averages and differences. Select its coefficients, then reconstruct the signal and account for the loss.</p></div>
<button type="button" data-reset="haar" disabled>Reset experiment</button></div>
<div class="lab-workspace haar-workspace"><fieldset class="lab-controls" id="haar-controls" disabled>
<legend>Choose a signal</legend><label class="lab-label" for="haar-preset">Start with an example</label>
<select id="haar-preset"><option value="step">Steps and a spike</option><option value="ramp">Rising ramp</option><option value="alternating">Alternating signs</option><option value="pulse">Single impulse</option><option value="triangle">Triangle</option><option value="custom" disabled>Custom signal</option></select>
<p class="lab-control-note">Edit any sample below. Addresses run from 0 to 15; values are whole numbers from −16 to 16.</p>
<div class="haar-samples">''' + samples + '''</div>
<p class="lab-error" id="haar-error" role="status" hidden></p>
<fieldset class="haar-choices"><legend>Try a selection</legend>
<button type="button" data-haar-selection="all" aria-pressed="true">All coefficients</button>
<button type="button" data-haar-selection="coarse" aria-pressed="false">Coarse structure</button>
<button type="button" data-haar-selection="no-fine" aria-pressed="false">Drop finest details</button>
<button type="button" data-haar-selection="mean" aria-pressed="false">Mean only</button></fieldset>
''' + slider('haar-cutoff', 'Magnitude cutoff', 0, 0, 16, step=.25) + '''
<p class="lab-control-note" id="haar-cutoff-help">Moving the cutoff selects details with |coefficient| ≥ cutoff. You can then override that selection using the coefficient checkboxes. The global mean is always kept.</p>
<p class="haar-selection-note" id="haar-selection-note">Selection: all coefficients.</p>
</fieldset><div class="lab-visual haar-visual">
<div class="haar-legend"><span class="haar-original">Original</span><span class="haar-rebuilt">Reconstructed</span><span class="haar-residual">Residual</span></div>
''' + diagram('haar-diagram', 'Original and reconstructed 16-sample signal, with residual below') + '''
<fieldset class="haar-inspector" id="haar-inspector" disabled><legend>Inspect the signal</legend>
<label class="lab-label" for="haar-inspect">Coefficient support and contribution</label>
<select id="haar-inspect" aria-describedby="haar-inspect-help"><option value="none">Whole signal</option></select>
<p class="lab-control-note" id="haar-inspect-help">Choose a coefficient to highlight its support. Its contribution is added on the first half and subtracted on the second.</p>
<p class="haar-inspect-detail" id="haar-inspect-detail" role="status"></p>
''' + slider('haar-address', 'Inspect address', 10, 0, 15) + '''
<p class="haar-sample-detail" id="haar-sample-detail" role="status"></p></fieldset>
<div class="lab-metrics lab-metrics-two"><div><span>Retained coefficients</span><output id="haar-retained">16 / 16</output></div>
<div class="lab-residual"><span>Squared reconstruction error · Σrᵢ²</span><output id="haar-error-energy">0</output></div></div>
<p class="lab-verdict" id="haar-status" role="status">All 16 coefficients retained. Every sample is recovered exactly.</p>
<fieldset class="haar-coefficients" id="haar-coefficients" disabled><legend>Keep the coefficients</legend>
<p class="lab-control-note">A detail changes the two halves of its support in opposite directions. Toggle a coefficient to see its contribution.</p>
<div class="haar-mean"><span>Global mean · always kept</span><output id="haar-mean">3</output></div>
<div id="haar-levels"></div></fieldset>
<details class="lab-data"><summary>Inspect samples, intermediate averages, and the energy balance</summary>
<p class="haar-energy-caption">Original energy = reconstructed energy + residual energy</p>
<p class="haar-energy-equation"><output id="haar-original-energy">416</output> = <output id="haar-rebuilt-energy">416</output> + <output id="haar-residual-energy">0</output></p>
<p class="lab-caption">The averaging normalization needs weights: the mean has weight 16 and a level-j detail has weight 2ʲ. Unweighted coefficient squares do not equal signal energy.</p>
<div class="table-scroll"><table><caption>Four analysis levels, from fine to coarse</caption><thead><tr><th scope="col">Level</th><th scope="col">Averages</th><th scope="col">Details</th></tr></thead><tbody id="haar-analysis-table"></tbody></table></div>
<div class="table-scroll"><table><caption>Sample values at each original address</caption><thead><tr><th scope="col">Address</th><th scope="col">Original</th><th scope="col">Reconstructed</th><th scope="col">Residual</th></tr></thead><tbody id="haar-sample-table"></tbody></table></div>
</details></div></div>
<details class="lab-reason"><summary>How do four levels reconstruct the signal?</summary>
<p>For each pair (u, v), store its average a = (u + v)/2 and detail d = (u − v)/2. Repeat on the averages until one global mean remains. This gives 1 mean and 1 + 2 + 4 + 8 details. Invert one level with u = a + d and v = a − d, then repeat toward the samples. An unchecked detail is replaced by zero. The synthesis vectors are mutually orthogonal; accounting for their weights gives the displayed energy balance.</p>
<p>All arithmetic here uses bounded integers and fractions with power-of-two denominators. The displayed coefficients and reconstruction errors are exact.</p></details>
<div class="lab-sources"><p>Build on the Haar-pair worked example, then follow its Paper V and Information Realization source links.</p>
<a href="collection/demonstrations/HAAR_LAB.html">Read the multilevel calculation <span aria-hidden="true">↗</span></a>
<a href="collection/examples/14_HAAR_PAIRS.html">Start with the four-sample example</a></div>
</section>'''
