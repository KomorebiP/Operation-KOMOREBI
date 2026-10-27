# Block 40 failure and repair ledger

Only terminal successful runs are counted as verification evidence.

1. **Two disposable work-container resets.** The in-progress source tree disappeared twice. The draft was reconstructed from the proof transcript and checkpointed outside the disposable tree before further compilation. No interrupted state was counted as a pass.
2. **Initial volume normalization proof.** The first proof left the identity `(2^n)^3 = 8^n` unresolved. It was replaced by an explicit power calculation.
3. **Preimage membership mismatch.** The first containment proof attempted to rewrite membership before unfolding the preimage. The target was changed explicitly to decoded-box membership.
4. **Finite-cylinder decomposition parser/proof failures.** Big-operator notation inside lambda expressions and an unstable contradiction branch were replaced by explicit `Finset.sum` terms and a unique-prefix pointwise argument.
5. **Span-induction misuse.** The first call supplied the final membership proof in the wrong argument position. It was repaired to match the actual `Submodule.span_induction` contract.
6. **Projection construction typeclass gap.** A direct redefinition of the orthogonal projection required an uninstalled complete-space instance. The concrete projection is instead definitionally the checked Block 39 projection, after proving equality of its range with the dyadic-box level.
7. **Premature packaging attempt.** An earlier packaging script ran against a source revision that still failed compilation. Those partial reports and archives were discarded and are not part of the final evidence.
8. **API namespace generation.** The earlier automatic generator did not qualify declarations in the nested `Prev` namespace. The final API file lists all 63 declarations explicitly; all checks pass.
