# Route record and implementation corrections

SF-B13-SCALAR starts at 718a037fd39c0f1bbad6c66e5e1b6fa570553447.
Target: global scalar reduction and the explicit half-scale formula, with
the named example/order-parameter correspondence. Mechanism: low coefficients
for necessity, actual scalar derivative equations and entire uniqueness for
sufficiency. Outcome: proved for the registered scope. Product equality
alone is refuted by the positive rational fixture; it is not the target.

SF-B13-REMAINDER: split the actual convergent odd series into its four-term
prefix and tail, then transport the earlier coefficient bound to the function
difference. Outcome: proved, with |error|<=|z|^9/8 for |z|<=1. This supplies
the printed O(z^9) meaning without claiming arbitrary-radius evaluation.

SF-B13-SURFACE: positive real powers and the unique characteristic root.
Outcome: proved for any t>0 with the strict budget. The boundary fixture
computes a=1 at equality, so the strict inequality is not dropped.

Development diagnostics were implementation corrections: a crossed-row
square identity needed an explicit linear rewrite; complex normed-space
instance diamonds needed convert! as in pinned Mathlib; a negated equality
was handled by introducing its equality premise; 1/t was rewritten to t^-1
for the real-power inverse API; coefficient inequalities were ring-normalized;
redundant tactics were removed under warnings-as-errors. None refuted the
registered mathematical target. The production source compiles; the positive
fixture succeeds and the rejection controls fail with their specified diagnostics.

The coefficient-only sufficiency route remains deferred, not exhausted:
resume for regimes without analytic uniqueness. The explicit sinh-series
route remains deferred for factorial-normalized coefficient formulas; the
direct derivative route already proves the global function identity.
No numerical fit, random search, literature novelty claim, delegated job
or delayed mathematical run supports this checkpoint. Formal attempts and
any failed replay are inventoried separately from the accepted execution.
