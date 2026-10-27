# Development corrections and non-claims

This file records actual failed attempts and the fixes. Only later successful runs
supply the final audit. No failed attempt is relabeled as a pass.

1. An initial root-filter test substituted the rotated scalar instead of the rotated
   argument including z. The test implementation was corrected and then compared with
   independent coefficient selection.
2. Initial exact-bracket JSON serialization exceeded Python's integer-to-string digit
   guard because intermediate rational denominators were enormous. The mathematical
   calculation remains exact. Export now uses outward-rounded rational bounds at 70
   decimal places and checks signs after rounding, preserving a checkable certificate.
3. Two Python diagram strings had invalid escape warnings. They were changed to raw
   strings and the entire new build was rerun with warnings promoted to errors.
4. The first LaTeX draft had a 92-point overflow because the final table began in the
   preceding paragraph. Explicit paragraph starts removed it. The final log has no
   overfull/underfull boxes or unresolved references.
5. An initial integrated build used the wrong nested location for the source PDF.
   It exited before building. The path was corrected to the verified review root.
6. The local `bibtex` launcher is a broken symlink. The first original-source build
   failed at that command. The working `bibtex.original` binary was used instead.
   The portable helper now detects that fallback and has a matching frozen .bbl as
   a no-bibtex option. The final original rebuild matched all 39 pages in text/render.
7. A plate row with positive coefficients was clarified to say "negative logarithm"
   rather than "logarithm". Numeric scientific labels were typeset as powers of ten.
8. The deliberately false signed-matrix control uses direct matrix equality, rather
   than a scalar polynomial comparison helper. The final five controls are rejected
   by their appropriate exact comparisons.

The original snapshot is untouched. No Lean compiler was invoked. The inherited
independent audit's missing-Lake failure belongs to that earlier audit, not a newly
performed Lean attempt in this run. The Python suite checks stated finite identities
and local rational enclosures, not general proof contracts.
