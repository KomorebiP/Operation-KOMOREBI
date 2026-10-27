# Block 06 — failures, repairs and retained limits

## Failed or interrupted attempts

1. The inherited monograph build could not invoke this environment's broken `bibtex` symlink. The corrected driver validates executable discovery and uses the available `bibtex.original` fallback. The traditional wrapper also required unbundled local fonts. Those dependencies were moved to an installed-font lookup, without shipping font files.
2. The inherited visual and Lean drivers failed because they did not copy `komorebi-publication.sty` into their build directories. The coordinated builder stages the shared style and include dependencies.
3. A preliminary system-family font experiment selected unsuitable font shapes and slowed the build. Explicit installed P052/Nimbus Sans variants replaced that experiment. A combined early invocation timed out before all work finished; the successful stage receipts, not the interrupted call, establish final completion.
4. The inherited monograph contents layout overlapped section numbers with titles. The first layout repair referred to an undefined `\@dotsep`. A local definition and explicit dotted TOC handlers fixed the issue. Final contact review then found an avoidable short TOC spill page; reducing contents paragraph spacing removed it.
5. A Lean chapter heading exceeded its box. Ragged-right chapter formatting repaired it. One historical table column and one explanatory paragraph were reflowed without changing selected formal source bytes.
6. The link audit found a malformed dimension expression in Appendix D. Markdown conversion had turned `[k:F_p](n−n/p)` into a hyperlink, losing the multiplicative factor in the printed formula. The raw source was recovered and the exact mathematical expression restored. The invalid PDF target is gone, and regression tests bind the correction to the raw note's hash.
7. One combined build-and-render tool invocation timed out. Each original reader was subsequently rendered in a separate successful invocation. An attempted shortcut to reuse earlier Lean renders asserted identical final PDFs and failed because the companion destinations had changed between candidate versions. That shortcut was abandoned. The final Lean PDF was rendered afresh in full. This was not a same-source reproducibility failure.

## Final nonfatal diagnostics

The final traditional build retains 55 underfull-spacing diagnostics in inherited dense prose. They are not overfull boxes, missing glyphs or unresolved references, but the build is not described as warning-free. The visual build retains the `epstopdf` warning that shell escape is disabled. All figures are already PDF and shell escape remains deliberately disabled. The final Lean build has no diagnostics.

## What was not done

No new Lean/Lake compiler run, arithmetic matrix-constructor replay, full seven-program historical Block 03 arithmetic replay, new classical-source audit, or external peer review occurred. Publication source preservation and finite-model tests do not substitute for those activities.

The complete editable Block 02 archive and terminal successful v0.45 target receipt remain unrecovered. Their absence is not evidence of a mathematical or compiler failure. The detailed Henniart–Lemaire primary-source reread retains the previously recorded access limitation. No new recovery attempt for those gaps is claimed here.

The two research companions were preserved, not rebuilt. The final three-original-reader isolated rebuild is byte-identical in this environment. This positive result does not erase earlier checkpoints' documented binary reproduction limitations.

## Scope of the review

All 397 revised original-reader pages were rendered and inspected through 21 contact sheets. Fourteen selected pages were inspected at 150 dpi. Automated checks cover page bounds, destination resolution, catalogue names, excerpt identities and source preservation. This is a synchronization and publication audit, not a fresh line-by-line reproof of every inherited mathematical argument.

## Mathematical endpoints

General arithmetic realization, same-candidate H5, corrected-character occurrence in the fixed candidate, and the stronger independently fixed native-marking certificate remain open. A successful abstract transvection or odd-order correction is not a computation of missing arithmetic data. The freely transported marking contract remains separate and is not silently strengthened.
