# Komorebi Space — Lean progress v1.12.0

Accepted checkpoint: **KS-v1.12.0-WR15-complete**. Parent: v1.11.0. Acceptance recorded 2026-10-13T00:58:24.836245+00:00.

## WR15 completed

For every full basis B of the actual protected kernel, the formalization constructs its Gram matrix G = BᵀB and derives its invertibility. It computes the coordinate equation residual q and proves that the existing restricted Hilbert normal residual is g = B G⁻¹q, with **‖g‖² = qᵀG⁻¹q** in the original norm.

For every invertible C, it constructs an actual changed full basis B′ = BC, proves inverse coordinate transport c′ = C⁻¹c, derives S′ = SC, G′ = CᵀGC and q′ = Cᵀq from the computed equation, and proves the certificate unchanged. This includes zero-dimensional kernels and arbitrary nonorthonormal bases. The identities hold for every real α; optimizer bounds still have their separate positivity requirements.

The two modules add **43 explicit theorems and eight definitions**, or 51 named public declarations. The mathematical review checks all 16 clause and representation obligations. The full final export also includes generated compiler declarations, counted separately below.

## Verification

- Fresh project compilation: **156 targets**, comprising 153 production modules and three entrypoints. Cumulative explicit theorem/lemma count: **1,693**.
- Complete environment audit: **5,048 declarations**, including **66 new exports** and all **4,982 inherited identities**. Every new type is fully exported. Only `propext`, `Classical.choice`, and `Quot.sound` occur in the accepted axiom union.
- **44 controls**: 14 positive, 28 intended compiler rejections and two policy rejections. All **238 exact commands** passed their required outcomes.
- Independent mathematical/type audit and terminal evidence reconstruction passed. The runtime/cache endpoint inventory contains **130,284 files**. Dependencies were not rebuilt from source.

The new positive controls exercise a full basis vector 2 in ℝ, a negative parameter for the algebraic identity, an empty Euclidean Hilbert space, and a nonorthogonal scale-and-shear change. In the latter, the raw covector square changes from 1 to 5 while the Gram certificate stays 1. The negatives reject the raw-norm substitution, a proper-subspace certificate missing a permitted direction, and a singular Gram matrix. These finite controls support interface checking; they are not the proofs of the universal theorem.

## Recovery and mistakes retained

Workspace maintenance removed the earlier scratch files. The saved predecessor was recovered and all 5,863 archive files verified against its accepted checksum manifest. The four previously delivered links were restored at their original local paths with matching hashes. The compiler runtime was recovered from its seven saved offline parts; archive digest, compiler/adapter identities and all nine dependency pins matched. Direct compiler startup without the bundled executable-location adapter failed, and startup with the unchanged adapter passed.

An initial file-recovery request used the wrong identifier field and was rejected; resolving the exact saved-file identifiers corrected it. Lean development exposed namespace/API adaptation, sum rewrites, source-root/import layout, strict linter errors and an unsupported optional printing setting. The controls exposed an obsolete matrix import, a missing real-number import and a deprecated import. Their failed sources, commands, logs and corrected attempts are retained. No failure was relabeled as a successful control.

Before source freeze, a leftover development object was detected inside the formal overlay and moved outside it. The accepted replay used a fresh empty project-object directory. A reviewer also strengthened its independently authored terminal-check script before use after a separate read found missing record comparisons. Frozen integration helpers were unchanged. An extra archive-review worker could not start because of the thread limit, so artifact checking was assigned to an available agent independent of the packaging implementation; mathematical review remained separately owned.

## Remaining work and restart

**Thirteen of sixteen principal groups are complete; no group is partially formalized.** WR10–WR12 remain written-only. The next block is the actual infinite ℓ² diagonal model, followed by its certified tails, sharp budget asymptotic and rounded noisy rate. The frozen statements and exact restart obligations are included.

The whole-monograph audit, executable-code refinement, model identification and synchronized publication/guide updates remain separate. No revised PDF is claimed. The historical v1.10.0 monograph is preserved unchanged through the predecessor archive.

## Evidence and limitations

Receipt SHA-256: `2de09e2bdae21cd53e0b3ff294d706dbf1582446ef5a0e1b8bc875023a4737cb`. Postflight SHA-256: `262fd925eb8ad139bebfcfc7627545da04ad7b3de6f0b0d3e32e0de67b3e90af`. The JSON summary binds source, reports and reviews. The append-only journal is `records/EVENTS.jsonl`.

Lean's compiler/kernel, permitted axioms, pinned external caches and supporting runtime remain trusted. Endpoint hashes cannot detect a transient change restored between observations. Inherited declaration identity means name, originating module, kind, safety and axiom set, supported by unchanged inherited source and fresh compilation; it does not claim byte-identical proof expressions. The focused WR15 audit does not certify every sentence or executable example of the monograph.
