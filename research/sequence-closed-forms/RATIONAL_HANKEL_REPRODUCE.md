# Reproduce the rational Hankel continuation

Author: Komorebi P.

Extract sequence-formula-source.zip and run these commands from its root.
Python 3.10+ with the standard library suffices for the two mathematical
verifiers; cross-language checks additionally require Node.js 24.

~~~text
python -B tools/verify_sequence_rational_hankel.py --output rational-hankel-checks.json
python -B tools/verify_sequence_linear_hankel.py --output linear-hankel-certificate.json
python -B -m unittest discover -s tools -p test_sequence_linear_hankel_bridge.py -v
~~~

The first verifier checks 3,830 finite assertions, including complete
transfer-vector recurrence certificates and invalid-certificate rejection.
The second verifies every evaluation required by the linear-weight theorem's
degree-18 polynomial reduction: 19 full vector identities, 152 early-index
identities, and 342 independent direct determinants through size 17. Its output
contains every coefficient of the general rational numerator and the sample
Bezout identity establishing minimal order nine at a=b=1.

The bridge compares Python and JavaScript at 53 integer parameter pairs
through index 256, with independent Schur and fraction-free determinant checks.
It also compares five rational-kernel formula cases. None of these finite
comparisons alone establishes historical novelty.

For rational Python parameters, pass fractions.Fraction values to
sequence_rational_hankel.linear_hankel_determinants. The browser accepts
integer coefficients from -12 through 12, at most 32 displayed values, and
indices through 256. The differential Schur view keeps its existing size-64
interface.

The general existence proof covers arbitrary fixed finite degrees and orders.
Explicit transfer construction has a 20,000-state default cap in the supplied
Python implementation. Its large state bound is not an efficiency theorem.
