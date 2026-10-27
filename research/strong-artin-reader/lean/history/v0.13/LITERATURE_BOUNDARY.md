# Literature/application boundary

This file records the application boundary used when interpreting v0.13.

## Published adequate-image theorem

Miagkov and Thorne, *Automorphy lifting with adequate image*, Forum of Mathematics, Sigma 11 (2023), e8, Definition 1.1, formulate adequacy for a finite subgroup of `GL_n(k)` under hypotheses including `p ∤ n`. Their fourth adequacy condition is the spectral-projector detection clause: every irreducible `k[G]`-submodule of `ad^0 V` is detected by a functional `X |-> tr(e_{g,alpha} X)` for a generalized-eigenspace projector `e_{g,alpha}`.

The same paper's Proposition 6.7 constructs finite Taylor--Wiles data under its full global hypotheses, including adequate image, and controls the size of the auxiliary set by the relevant dual Selmer dimension.

## What v0.13 does and does not import

v0.13 formalizes a **local representation-theoretic weakening** of the spectral detection part:

- simple conjugation packets outside the scalar line must be detected;
- the scalar line is handled separately by one nonzero-trace projector;
- no hypothesis `char(k) ∤ dim(W)` is used in the Lean linear-algebra theorem.

This does not prove that Miagkov--Thorne's global automorphy-lifting theorem applies when their other hypotheses fail. In particular it does not replace the cohomological vanishing, regularity, decomposed-generic, local deformation, or global Taylor--Wiles hypotheses in their theorem.

The phrase `relative adequacy` in this checkpoint therefore names a candidate local replacement for one spectral separation mechanism, not a published global automorphy-lifting theorem.
