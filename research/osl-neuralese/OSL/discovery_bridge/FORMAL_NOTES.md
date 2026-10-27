# Finite admission semantics

Let $S_W$ be the complete legal state set of a finite world $W$, let $G_W$ be its primitive operators, and let

\[
\mathcal P_{W,d}=\bigcup_{k=0}^{d}G_W^k
\]

be the bounded program universe through depth $d$.

Each program $p$ has the exact signature

\[
\sigma_W(p)=\bigl(p(s)\bigr)_{s\in S_W}.
\]

The bridge quotients programs by

\[
p\equiv_W q \quad\Longleftrightarrow\quad \sigma_W(p)=\sigma_W(q).
\]

A demonstration set $D=\{(s_i,t_i)\}$ identifies the compatible quotient set

\[
\mathcal C(D)=\{[p]_{\equiv_W}:p(s_i)=t_i\text{ for every }i\}.
\]

The decision rule is:

- `UNSATISFIABLE` when $|\mathcal C(D)|=0$
- `AMBIGUOUS` when $|\mathcal C(D)|>1$
- identified when $|\mathcal C(D)|=1$
- `ADMITTED` only when the identified class is nontrivial and every claimed relation holds on all of $S_W$

## Finite soundness statement

If the bridge emits `ADMITTED`, then within the declared world and depth:

1. exactly one transformation class agrees with every demonstration
2. the selected representative is the shortest lexicographically first program in that class
3. every listed equivalent spelling has the same full transformation signature
4. every claimed law holds on every legal state
5. the transformation is not equivalent to the identity or a single existing primitive

This follows directly from complete enumeration of $\mathcal P_{W,d}$, complete evaluation over $S_W$, and exact JSON-state equality. The certificate includes the complete normalized proposal, quotient size, state count, representative, transformation identifier, signature digest, law results, and proposal digest. Certificate verification recomputes the decision rather than trusting the stored status.

## Witness completeness

For `AMBIGUOUS`, the bridge returns a legal state on which two compatible classes differ. Adding that state and the intended output to the demonstrations removes at least one compatible class.

For a false law, the bridge returns a legal state and the unequal outputs of the two sides.

For inconsistent demonstrations, the bridge returns the duplicated input and its conflicting outputs.

## Registry property

Each registry entry contains the complete admission certificate and commits to its predecessor, candidate identity, representative, and transformation identifier. Verification replays the embedded proposal and certificate before checking sequence, digest, chain continuity, and transformation uniqueness. Editing, insertion, internal deletion, reordering, or duplication breaks verification from the modified point onward, assuming SHA-256 collision resistance.

An unanchored hash chain cannot detect deletion of its final suffix. The verifier therefore accepts an optional externally retained `expected_tip`; a suffix-truncated registry fails when checked against that trusted tip.

## Trusted base

The Python implementation, finite world declarations, primitive executor, and SHA-256 implementation remain trusted. A declared source digest is a commitment, not authentication, unless a trusted party anchors it externally. This is executable finite metatheory, not a proof-assistant theorem about the Python runtime.
