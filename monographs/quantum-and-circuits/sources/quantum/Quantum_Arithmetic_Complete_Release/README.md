# Quantum–Arithmetic Bridge: Projectors, Fourier Packets, and Unitary Realization

Komorebi P. · Final publication set · 6 October 2026

This release completes the finite arithmetic-to-signal-to-complex-state bridge with three companions: the traditional paper, the visual guide, and the Lean guide. The three PDFs are in output/. Editable TeX and Markdown, exact data, scientific figures, checked Lean source, archived proof receipts, and current review records accompany them.

## Read the set

- Traditional paper: full self-contained proofs of QA01–QA20, general finite Fourier and Ramanujan identities, rational divisor projectors, polyphase formulas, and the complete twelve-dimensional example.
- Visual guide: 25 concepts and 20 mathematical figures, covering phase addition, exact filtering, complete order packets, normalized states, alternative measurements, the continuous phase family, and polyphase assembly.
- Lean guide: the exact formal contracts, source excerpts, declaration concordance, all 96 named theorems, toolchain pins, trust assumptions, controls, revision reconciliation, and replay status.

The fixed example selects modes 1, 5, 7, and 11 modulo twelve. Its integer signal is

    (4, 0, 2, 0, -2, 0, -4, 0, -2, 0, 2, 0).

The rational projector is P(n,m) = c12(n−m)/12 and equals F D F†. Its rank is four. The test input splits orthogonally into energies 150 = 48 + 102. The normalized signed and unsigned states have the same sample-basis histogram but opposite selected probabilities after Fourier analysis. A relative-phase family has selected probability sin²(θ/2). Complete sample-basis dephasing gives selected probability 1/3. The last two extensions have prose proofs; they are not additional inherited Lean declarations.

## Evidence and freshness

The authoritative later checkpoint has five active modules with 22 + 17 + 30 + 17 + 10 = 96 named theorem declarations. These include supporting lemmas, rather than 96 new discoveries. The earlier 59-theorem checkpoint is retained as an overlapping predecessor.

The archived September 21 receipt records fresh source compilation with warnings treated as errors, axiom inspection, and Lean-kernel replay of all five modules. This edition independently checks all 96 declaration locations and all 16 recorded source/log hashes. The current exact Python replay passes 3,003 source assertions and 5,374 additional release assertions. Floating diagnostics use a declared tolerance of 1e−12 and are reported separately.

Fresh Lean compilation and kernel replay did not run in this edition. The exact runtime was located, but three download attempts failed with HTTP 502 before any runtime bytes arrived. The current status is NOT_RUN. Archived proof evidence is preserved unchanged and is not represented as a new compiler pass.

The first document build attempted LuaLaTeX, whose font-loading dependency was absent. The completed PDFs use XeLaTeX with Latin Modern and DejaVu Sans Mono. Overlapping draft preview renders produced truncated image reads; the final pipeline serializes rendering and publishes completed staged page sets. Draft figure labels, a visual page spillover, and Lean excerpt page breaks were corrected before final release. Failed and superseded execution evidence is retained and identified.

## Reproduce

Run from this directory. The scientific Python dependencies used here are pinned in requirements.txt. Rendering also needs XeLaTeX, the stated fonts, and Poppler.

    python3 checks/make_visuals.py --output verification/manual_replay/visual_results.json
    python3 lean/build_concordance.py
    python3 lean/build_guide_body.py
    python3 checks/build_documents.py
    python3 checks/render_documents.py
    python3 checks/verify_release.py

The figure script writes the figure assets, so use a separate copy of the project for a reproduction that must preserve the original release bytes. Mathematical plot content is reproducible; PDF metadata can make repeated plot files differ bytewise. The archived bounded-run manifests identify the exact code, inputs, limits, environment, results, and asset hashes used for this release.

For a fresh formal replay, restore the external pinned Lean 4.34.0-rc2 runtime and its dependency cache. Mathlib is pinned at aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Then, from lean/checked_checkpoint/, run the supplied verifier with a new output directory:

    python3 scripts/verify_lean.py \
      --toolchain /path/to/Komorebi_Portable_Lean_4.34.0-rc2/toolchain \
      --packages /path/to/Komorebi_Portable_Lean_4.34.0-rc2/workspace/.lake/packages \
      --out verification/reproduction

The verifier does not fetch dependencies. The runtime itself is not bundled. The standard axiom union is propext, Classical.choice, and Quot.sound; the active source contains no admitted proof, custom axiom, native_decide, or unsafe declaration. Lean-kernel replay is not an independently implemented proof assistant.

## Source lineage and scope

downloads/ preserves the retrieved source archives and reports. inputs/ preserves their extracted contents. lean/checked_checkpoint/ is the unchanged later active project. provenance/ records input identities, hashes, internal lineage pages, and release integrity. reviews/ and literature/ record the bounded independent audit and attribution checks.

The authenticated internal Stratified Universality source is included for Proposition 21.11 and Boundary 21.12, printed pages 189–190. The later Block 17 patch repairs a separate numerical quantum-error-correction subsystem and was not applied to this exact Fourier project. It is preserved solely as related lineage, with that distinction recorded.

Ramanujan sums, Fourier orthogonality, rational cyclic projectors, and standard quantum measurement rules are classical. This publication supplies their exact integration, worked example, and evidence concordance. General-modulus prose proofs are distinguished from the fixed-modulus formalization. Finite regression checks are not universal proofs. Hardware realization, efficient circuit synthesis, general noise removal, and quantum advantage require separate results.
