# Strong Artin visual guide self review

Proofread: all 24 `GuideSpread` blocks in `body.tex`, the cover and macros in `main.tex`, and every figure label in `figures.py`.

- Routine edits: repaired long label wrapping, standardized visible exponents, removed crowded card text, and clarified schematic, finite, conditional, and theorem domains at the point of use.
- Mathematical token changes during conservative self review: none. Mathematical review separately corrected the initial degree one exception wording and changed the final diagram output from exact attachment to weak attachment with local checks remaining. It also made finite coefficient and finite ramification hypotheses explicit in the l adic spread. These are recorded authoring corrections, not silent typographic substitutions.
- Unresolved issues: the arithmetic application gates identified in the final spread remain open. No unresolved notation or mathematical scope error was identified in the completed guide review.
- Validation: every exact figure assertion, all native canvas bounds, and every card text containment check passed. The final computation manifest validated as a version 2 evidence record. A separate reviewer reconstructed the data without importing the generator. Native visual review covered all 24 figure PNGs. Assembled PDF verification is performed by the parent build workflow.
- Coverage: complete guide source and every figure label. Source pins are in `SOURCE_PINS.json`. Review pinning and assembled layout evidence are in the parent reports.

The review preserves the distinction between generic local algebra and arithmetic existence. No proof of Strong Artin, global automorphy, or a new Lean replay is claimed.
