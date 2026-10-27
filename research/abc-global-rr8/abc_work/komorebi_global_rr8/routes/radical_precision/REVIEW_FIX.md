# Positivity hypothesis corrected after independent review

Reviewer /root/rr8_precision_review found that Theorem 1 began with an
arbitrary integer triple and its later condition c>=max(a,b)>0 did not
require both a and b positive. For example, a=-31,b=1,c=1 violates the
asserted consequence |a+b-c|<=c. The proof already used positivity of
both coordinates, but the theorem statement did not state it correctly.

The consequence now explicitly assumes 0<a,b<=c. No other proof text
changed in this correction. The original is preserved as
snapshots/PROOF_NOTE.pre-positivity-fix.md, SHA-256
e7b9472eff5565403593b12567e0725a3065b8eaba5621aca0a73add2fa444fc.

The general modular certificate, the positive fixed-radical construction,
and the integer repair minimization are unchanged. The corrected proof
was sent back to the same independent reviewer for a final verdict.
