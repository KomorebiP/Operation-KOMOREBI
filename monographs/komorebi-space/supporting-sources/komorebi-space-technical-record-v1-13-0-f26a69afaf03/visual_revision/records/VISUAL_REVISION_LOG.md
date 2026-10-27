# Visual companion revision

Author identity: Komorebi P.  
Publication: Komorebi Space, edition 1.13.0.  
Task: make the visual guide less redundant with the monograph.

## Baseline and editorial decision

The recovered publication contained a 45-page visual guide with 40 figures. Thirty-eight figure assets also appeared in the monograph. Its sequence largely repeated the monograph's exposition. The original publication archive is retained in the accompanying Technical Record so this baseline can be reconstructed.

The revised guide contains 19 pages: cover, contents, a reading introduction, and sixteen one-page investigations. Each investigation declares a concrete model, presents a new graphic, explains a visible comparison, and works through a change to the model. Numbered monograph references carry the definitions, general hypotheses, and proofs. The revised guide reuses none of the monograph's figure assets.

The new collection covers coordinate overlaps, integer extension fibers, marked boundaries, composition coverage, order and phase, discarded detail, infinite tails, restricted repair, protected-angle cost, moving kernels, path movement, realizability thresholds, budget frontiers, noisy regularization, coordinate conditioning, and stopping schedules. Spatial examples use actual three-dimensional coordinates. No generated raster illustrations were used.

## Authorship and independent review

The foundation and analytic investigations were prepared in separate source files. A third reviewer independently read all sixteen scene records, the plotting formulas, the declared finite checks, and the relevant local monograph statements. It inspected all sixteen previews and checked their monograph pointers. The primary editor reviewed physical PDF pages 1–10; the independent reviewer reviewed pages 11–19 and the full extracted text for scope and reader role.

Fifty-two generator checks passed. This count includes typography checks as well as finite mathematical identities. Twenty-three separately implemented independent checks passed, using exact arithmetic where recorded. The independent computation manifest uses schema version 2; the generator-run manifest uses the supported legacy version 1 and states its limitations. Neither count represents new theorems or a new Lean run. Infinite conclusions are supported by written arguments and monograph references, never by the endpoint of a finite plot.

## Problems found and corrected

- The first monograph-reference build was launched from the wrong working directory and failed before compilation. It was rerun from the publication directory and completed successfully.
- Early foundation figures had clipped axes, a long clipped subtitle, and a collision between a point label and a repeated axis label. These were corrected and the rendered figures inspected again.
- The binary-gauge comparison initially said zero gauges were allowed while its rule allowed the frozen pair. It now says zero compatible gauges, which describes the comparison correctly.
- The phase example now explicitly assigns the two-bit labels to its two matrices.
- A three-dimensional budget frame initially crossed the crop boundary. Its axes panel was resized to contain the full frame.
- The first assembled PDF showed white seams between heatmap cells on physical pages 13 and 19, although the PNG previews were smooth. A thin initial edge treatment was insufficient; the final face-colored overlap removes the seams while retaining vector geometry. The figures and assembled pages were re-rendered and inspected.
- The introduction overstated color-independent accessibility. It now describes the role of labels and legends without making that claim.

Author-specific notes in `review/` retain the implementation attempts and corrections in more detail.

## Final build and preservation

The final guide completed three LaTeX passes with no unresolved-reference or layout warnings. Every physical page was rendered. No extracted word lies outside its page. Comparing the final page images with the first reviewed build shows changes only on physical pages 3, 13, and 19: the introduction and the two heatmaps. Those pages were reviewed again.

The monograph PDF, Lean guide PDF, all 161 files in the Lean directory, and all 11 existing example files retain their parent bytes. Among the original 128 source files, only the visual-guide master file changes. New figure assets and scene records are added. No theorem proof or production Lean source was edited, and no new complete Lean compilation is claimed.

`VISUAL_REVISION_RESULT.json` binds the final guide to its hash, page count, pointers, and source comparison. The packaging script regenerates complete archive checksum manifests. The separate delivery verification report is produced by the independent reviewer after the archives are frozen and records their actual hashes and integrity checks.
