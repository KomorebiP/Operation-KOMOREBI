# Reproduce the parity, quadratic and mixed continuation

Author: Komorebi P. Mathematical checkpoint: SEQ-DH-2026-11-20-002.

Extract sequence-formula-source.zip into a fresh directory. From its root,
Python 3.10+ and the standard library suffice for all five commands:

~~~text
python -B tools/verify_sequence_quadratic_hankel.py --output uniform-quadratic.json
python -B tools/verify_sequence_parity_structure.py --output parity-structure.json
python -B tools/verify_sequence_hankel_symbol.py --output symbol-ideal.json
python -B tools/verify_sequence_quadratic_certificate.py --input verification/sequence-library/hankel-compression/quadratic-certificate.json --output quadratic-audit.json
python -B tools/verify_sequence_mixed_hankel.py --input verification/sequence-library/hankel-compression/mixed-certificate.json --output mixed-audit.json
~~~

The first command checks the complete degree-25 triangular interpolation grid:
351 parameter points, 702 full 70-state identities and 5,616 early identities.
The four-difference stencil remains fixed even at degree drops. The parity check reaches even and odd operators at M=3. The symbol command
checks every coefficient of the five-variable polynomial ideal identity;
its output lists both quotient polynomials.

The quadratic audit uses ordinary 256-coordinate tensors and direct monomial
initial determinants. It verifies the reduced degree-63 OGF and its modular
Bezout minimality certificate. The mixed audit rebuilds all 12,870 states as
bitmasks, constructs band entries directly from the defining moments, and
checks the integer residual, OGF, order-112 minimality witness, and zero second
minor. Both are separately implemented project self-reviews.

The saved JSON files supply proposed coefficients, not trusted success flags:
the audits reconstruct the defining objects and check their identities.
Changing a recurrence coefficient invalidates the residual or GF comparison.
No NumPy, SymPy, random sampling, or modular-to-rational inference is required
for these replay commands. The historical discovery used modular propagation
and CRT, followed by a full integer check; discovery is not the proof boundary.

The proofs distinguish a uniform bound 126 for quadratic weights from exact
minimal orders 63 and 112 at the two stated examples. General mixed-parameter
minimality remains open; historical novelty is unassessed. Source preservation and
publication checks are recorded under verification/sequence-library/hankel-compression/.
