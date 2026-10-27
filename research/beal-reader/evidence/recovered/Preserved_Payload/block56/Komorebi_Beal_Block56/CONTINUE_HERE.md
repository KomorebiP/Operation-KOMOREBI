# Continue with Block 57

Open Komorebi_Beal_Block56_Frobenius_Support_Exclusion_v5.6.0.zip as the sole
verified execution checkpoint. It contains the original Block55 ZIP, with
all earlier checkpoints nested unchanged.

Read completely before editing:

README.md; work56/TARGET_CONTRACT.md; work56/REPORT.md;
work56/PROOF_BOUNDARY.md; work56/THEOREM_INDEX.md; work56/GAP_LEDGER.md;
work56/notes/FROBENIUS_PRECISION.md;
work56/notes/FINITE_FROBENIUS_CERTIFICATE.md;
work56/notes/ARITHMETIC_CONSEQUENCES.md;
work56/notes/LOCAL_SURVIVOR_BOUNDARY.md;
work56/notes/SELF_REVIEW.md;
work56/source_records/SOURCE_CHECK.md;
work56/DEVELOPMENT_FAILURES.md; work56/VERIFICATION.md.

Extract cleanly and reproduce:

    python verify.py --replay-predecessors --report ../Block56_Replay.json

Preserve the exact theorem boundary. No new Lean certificate or independent
mathematical review occurred. Timeouts are inconclusive.

## New authoritative results

For the same actual good Frobenius, m=floor(n/2)+1 and h=v7(Q-1) give
r=min(n,m+h). The rank-two trace is Q+1 modulo7^r, the rank-four polynomial
is (T-1)^2(T-Q)^2 modulo7^r, and the Jacobian order is divisible by7^(2r).

Exact Frey counts prove:

    491 not dividing C => n=1.
    197 not dividing C => n<=2 and eta=1.
    eta nontrivial => n>=3 and 197*491 divides C.

The 56 modulo49 survivors at197 and 490 modulo7 survivors at491 must remain
preserved. They do not justify depth2 or depth1 elimination, respectively.

H(C) subset{97,293} now has depth1, with arbitrary additional h<=1 divisors.
H(C) subset{97,293,491} has n<=2. At n2 some beta-supporting prime has
v7(v_q(C))=1. A trivial eta is not a zero beta.

## Next substantive target

The SAME highest-layer character may still be supported at97/293 when C
also contains197 and491. Do not confuse highest-layer ramification with
H(C), the complete set of high-congruence divisors of C.

Target a compatible actual relation on this enlarged branch: local toric
matrices at the newly forced bad primes, actual Frobenius values at a
necessarily good place, or an integral representation/semilinear relation.
If using an auxiliary prime, first explain why it must be good under the
stated branch; do not turn another necessary divisor into a contradiction.
Other high conductor primes can change global ray-character values.

The exact local97/293 models and generic Weil-polynomial controls survive.
They show why neither a purely ramified-local argument nor a generic Weil
bound suffices. Do not simply repeat the old42 tests and announce zero.

Depth1, depth2, unrestricted higher support, actual coefficient/endpoint
compatibility, independent proof audit, CM nonboundary points, three higher
Hilbert levels, full signature, and full Beal remain separate obligations.
