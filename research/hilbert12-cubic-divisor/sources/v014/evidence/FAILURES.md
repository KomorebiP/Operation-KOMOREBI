# Failures and corrections

1. The initial growth module did not compile: the simplifier normalized
inequalities/modulo expressions before the supplied lemma matched them, and
two hypothesis names were unused. Explicit case splitting and arithmetic
replaced the mismatched simp steps; hypothesis names were marked unused without
removing or weakening assumptions. The original draft and log are retained.
2. The first replacement used four unconditional `split` tactics even when
one condition was already simplified. The fourth split failed. Three splits
followed by omega complete the same statement. The second draft is retained.
3. The first broad public searches returned substantial irrelevant matches.
Only the directly opened primary BCG/DLMF pages and the exact author-written
Jensen notes are used. No conclusion was drawn from the irrelevant results.

No accepted exact or numerical production run failed. No numerical tolerance
was weakened. No main gamma-arithmetic equality was proved or assumed.
