# Visual release computation and rendering report

## Contract

The release constructs scientific figures for a fixed twelve-coordinate arithmetic/Fourier/quantum model. Exact computation tests rational shell products, completeness, fixed input energies, a phase-erased Fourier table, relative-phase quarter turns, and lossless lane interleave. The preserved source verifier additionally checks its declared arithmetic range 2 through 64.

The coefficient domains are exact Python integers, Fraction rationals, and the source cyclotomic quotient ring. NumPy diagnostics and Matplotlib coordinates are floating approximations, reported separately. There is no random sampling.

## Result

The final bounded replay completed successfully. Its manifest validates with the project root. It replays **3,003 exact source assertions** and passes **5,374 exact release assertions**. These are execution assertion counts from two identified code paths, rather than a claim of 8,377 different theorems. Twenty figures are supplied in PDF, SVG, and PNG, with individual hashes in the scientific result.

The largest new floating diagnostic residual is **6.764165321960921e-15** for polyphase Fourier assembly, below the declared tolerance **1e-12**. The phase-family probability residual is **6.661338147750939e-16** and its normalization residual is **4.440892098500626e-16**.

## Provenance

- Final manifest: `verification/visual_release_run_v2/manifest.json`
- Scientific result: `verification/visual_release_run_v2/visual_results.json`
- Generator: `checks/make_visuals.py`
- Contract: `checks/visual_contract.json`
- Inputs: generator and preserved `verify_bridge.py` identified by hashes in the manifest
- Bounds: N=12, source q=2..64, 401 phase-curve rendering points, 20 figures
- Caps requested: 120 seconds wall, 100 seconds CPU per process, 2 GiB per-process address space, one core, one cooperative numerical-library thread, 1 MiB combined logs

The initial replay also passed the arithmetic checks. Draft figure inspection found an omitted three-dimensional imaginary-axis label and crowded lane annotations. The final generator places a visible 2D axis label inside the 3D panel and gives the lane values more vertical margin. The superseded first run and its source snapshot remain in `verification/visual_release_run/`. The v2 manifest and asset hashes are authoritative for the final plots.

## Interpretation and limits

The general Ramanujan, Fourier, and projector identities are justified by algebraic derivations in the traditional paper. Finite execution success is implementation evidence for the specified range. The new phase family is independently proof-audited elementary algebra, with exact endpoint/quarter-turn checks and separate floating rendering. It is not an added Lean theorem.

No Lean compilation, quantum hardware, gate synthesis, or complexity advantage is claimed by the visualization replay. Norm loss under projection is explicit, including selected probability 8/25 for the normalized filter input under the Born-rule projective-measurement model.

## Rendering review

All twenty final figures were inspected as contact sheets. The genuine complex-amplitude trajectory and polyphase annotation fixes were also inspected at larger resolution. Figures use an accessible restrained palette, named axes, exact values or explicit normalization, and vector PDF/SVG output. The guide preserves amplitude/probability and frequency/sample basis distinctions.
