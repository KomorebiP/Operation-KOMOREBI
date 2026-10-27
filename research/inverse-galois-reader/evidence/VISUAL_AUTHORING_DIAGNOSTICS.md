# Visual authoring diagnostics

The first full figure generation stopped at plate 15. Matplotlib's mathtext
parser rejected an unbraced fraction denominator in the averaging formula.
The denominator was written as `{2}`, preserving the mathematical formula,
and all 22 figures then generated successfully. No failed rendering was used
as evidence or delivered as a final asset.

The first source and figure reviews found the following issues. They were
corrected before the first guide PDF review:

- Plate 02's subgroup inclusion arrows pointed toward smaller subgroups.
  The arrows now point from smaller to larger subgroups, opposite the field
  column. Both columns use subset inclusion labels. The degree equalities
  were separated into two lines to prevent juxtaposition looking like a product.
- Plate 04's original exchange arrows passed through the sign circles.
  They now terminate outside each circle.
- Plate 07 initially showed canonical cycle representatives without making
  their status explicit. Its labels now give cycle types 4 and 3+1. These are
  not assertions about simultaneous root numbering across two primes.
  The conclusion arrows were also shortened to avoid touching its formula.
- Plate 08's exchange arrows were replaced with a single two-ended arrow for
  each involution pair. Plate 12 received visible zero-cell grid lines.
- The guide's regularity source identifier was aligned with the published
  source key DebesHarbater2021, not its 2019 author-revision date.
- The embedding problem spread now states that its domain is profinite.

All 22 initial PNG plates were individually inspected at original resolution.
The eight revised plates were individually inspected again. Review of the
compiled guide is recorded separately and must refer to its final PDF hash.

The first compiled guide inspection covered all 24 physical pages at original
resolution. Page 24 rendered the reproduction option `--only` as a typographic
en dash followed by `only`. The TeX source now separates the two hyphens with
an empty group, preventing the ligature. The corrected page requires a fresh
render and inspection before the guide passes final layout review.

The first attempt to save that review record failed because the layout evidence
directory did not yet exist. The directory was created and the record was saved
successfully, including a passed subset for pages 1 through 23 and the explicit
exclusion of page 24.

The corrected guide was rebuilt and rendered. Physical page 24 was individually
inspected again at original resolution. It now visibly prints two separate
hyphens, and PDF text extraction confirms the literal option `--only`. Its
columns, edition boundary box, margins and footer passed inspection. Root
confirmed that the PNG bytes for pages 1 through 23 are identical to the
previously inspected baseline. The current guide's final page review is saved
in `evidence/layout/manual_visual_final_page.json`.

The exact S3 matrix input uses a different basis order from the displayed
matrices. The generator converts by actual permutation tuples and requires
exact rational equality of both subgroup averages and their commutator.
This is an intentional basis change, not a discrepancy in the data.
