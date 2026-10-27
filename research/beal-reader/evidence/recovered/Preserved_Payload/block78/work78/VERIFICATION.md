# Verification record

## Predecessor

Block77 default verifier was replayed before development:

    python -B verify.py --report ../Block77_Replay_for78.json

Result: PASS_DECLARED_CHECKS.

Authoritative predecessor SHA-256:
`e8815ff496368ff99ca583f422f14d5a0bce6df537187691c89e7848f7a7e8ec`.

## New finite arithmetic

Commands:

    python -B work78/computations/primary78.py
    python -B work78/computations/independent78.py

Both passed.

- 806736 first-order toric packets checked in each implementation.
- 7,260,624 direct primary formula checks.
- 588 dual-module action checks in each implementation.
- 691488 wrong-sign negative controls fail as expected.
- The two bases agree on an order-independent canonical packet sum and xor.

The finite programs audit the local matrix formula and coefficient-module action
translation. They do not prove Neukirch's localization theorem.

## External source

Neftin's author-hosted J. Algebra paper was inspected at Theorem2.1 and Corollary2.3.
Theorem2.1 reproduces Neukirch, Invent.Math.21 (1973), Korollar6.4. The exact
criterion H1(G',A')=0 used here is present. Corollary2.3 supplies the additional
finite-set fixed-value statement.

## Evidence boundary

No pattern is eliminated. No unramified-outside-S statement is inferred from
finite localization surjectivity. No Lean compilation or independent
mathematical review is claimed.
