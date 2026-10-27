# Scope of acceptance

This release accepts a fresh replay of the existing Paper IV core under its
reviewed source contract: 68 scoped manuscript results, 151 map rows and 1,164
mapped declarations. All 118 production modules are compiled from source. The
separate audit module is then checked, and the transitive namespace audit covers
2,234 declarations, including 1,999 theorem declarations. The allowed axioms are
only `propext`, `Classical.choice` and `Quot.sound`.

One complete project-source replay was performed in a new object directory.
External cached dependencies were reused under exact compiler and dependency
pins. This is not a second independently implemented proof checker or a cold
rebuild of Mathlib. Fresh-extraction integrity and finite/API tests are separate
from the complete primary formal replay.

## Preserved mathematical boundaries

No universal simplicity of all zeros, positivity of every reduced zero, full
displacement expansion or zeta functional equation is asserted. Eventual
simplicity and asymptotic results retain their hypotheses and ranges. Branch
conventions, multiplicities and the integer-order hypotheses of nearest-pole
statements are not removed. Standard fact 11.1 stays outside the 68-result map.

## Publication boundary

This is not a new typesetting of the full 245-page reader set. Its latest recovered
PDFs are preserved. All-page text geometry and internal-link bounds were checked,
and the new five-page verification report was rendered and inspected in full.
The main and Lean readers have identical extracted page text and 43.2-dpi renders
to the recovered baseline, but their PDF bytes differ. The later visual PDF has
changes on pages 1, 14 and 28. Exact later editable source was not recovered.

The existing reviewed statement correspondence was tested against its concrete
source/target contract. It was not independently re-established through a fresh
line-by-line mathematical review of every argument in this block. No research
status of another core paper is upgraded here.
