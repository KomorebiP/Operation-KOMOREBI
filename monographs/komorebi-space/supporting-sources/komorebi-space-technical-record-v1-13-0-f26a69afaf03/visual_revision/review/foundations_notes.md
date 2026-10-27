# Foundation scene implementation and review

Eight new compositions are implemented by `tools/visual_companion/foundations.py`.
They use the shared Matplotlib style, a fixed 7 × 4.8 inch canvas, and font sizes of at least 10 points. All eight PDF pages have MediaBox `[0, 0, 504, 345.6]` and contain no image XObjects; their graphical content is vector. Matching PNGs are inspection previews.

The scene records are in `records/foundations_scenes.json`; every `monograph_labels` key resolves in `records/monograph_references.json`. No monograph chapter or shared style file was edited.

## Mathematical scope

The examples are coordinate views in R3; integer extension fibers; four explicitly enumerated binary gauges; a failing triangle and the four faces of an ordered four-view example; integer matrix actions and a two-bit phase; a five-value subsampling window; four displayed shift-remainder depths; and Euclidean projection in R3.

The accompanying eight checks pass. They verify the stated finite data and explicitly distinguish the displayed sequence window from the infinite formula in the monograph. The phase check exhausts the 64 triples and 16 scalar bit functions in this four-element model. No finite enumeration is presented as proof of a general theorem. JSON records include the command, arithmetic conventions, software versions, script hash, and PDF hashes.

Commands used:

```
python tools/visual_companion/foundations.py
```

A separate pypdf inspection verified all eight page sizes and zero raster image XObjects. A JSON key check verified the monograph references.

## Failed attempts and corrections

1. The first script invocation failed at Python parsing because the literal prime in a raw single-quoted LaTeX string ended that string. The prime was rewritten as `^{\prime}`. No output set was accepted from that failed invocation.
2. The next invocation reached figure generation but Matplotlib rejected `\mathbb Z` in mathtext. Braces were supplied: `\mathbb{Z}`. The entire eight-scene set was subsequently regenerated.
3. First visual inspection found that the right z label in the two-panel integer-fiber scene was outside the canvas. Both z labels were positioned explicitly inside their panels.
4. The first tetrahedron camera nearly superposed several edges. A new azimuth separates the three base vertices and all six edge labels.
5. The first phase figure placed the left panel's `(2, 1)` label against the second panel's repeated y-axis label. The redundant second y-axis label was removed. The setup now explicitly assigns the two-bit labels to the matrices.
6. The first recovery-depth subtitle exceeded the canvas, and the right z-axis label was clipped. The subtitle was shortened, both panels were resized, and the remainder labels moved above the cubes. A second label position was rejected because it overlapped a top trace; the final position is clear.
7. The binary-gauge caption initially said `0 allowed gauges`. It now says `0 compatible gauges`, because the frozen gauge is allowed by the rule but does not satisfy the indicated source-to-target comparison equation.

## Final inspection

Every preview was inspected at full output size. All altered figures were inspected again after regeneration. A separate read-only reviewer checked the formulas, captions, references, and all eight previews. The reviewer identified the label and wording items above; no formula correction was required.

The genuine spatial scenes use actual numerical 3D coordinates. In the recovery plot, connecting lines guide the eye between sequence values; markers identify the actual integer-indexed data. The tetrahedron is a spatial display of a full-patch composition cover, not an identification of the site with a geometric simplicial complex.

Conservative mathematical self-review covered only the new scene records and diagram labels. Routine changes were notation-safe string syntax, the explicit matrix-label assignment, and the gauge-comparison wording. No existing mathematical source statement was changed. No unresolved mathematical issue remains in these finite examples.
