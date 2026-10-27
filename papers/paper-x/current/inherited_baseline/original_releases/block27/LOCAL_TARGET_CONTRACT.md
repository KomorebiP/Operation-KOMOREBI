# Block 22 target contract

Base: Block 21 final archive SHA256 fbe69e04d5e693f6f91b7af7090b04ec43a3467feea1c17cd53fbc9cd9cffbf2, 138 frozen production modules.

Goal: identify a genuine local arithmetic condition on the fixed quadratic G_Q packet, prove its finite coefficient interpretation, and apply completion to it. Full arithmetic Claim8.2 is not silently replaced by this restricted goal; full ledger15/5 remains unless its entire source statement is proved.

Routes: (1) local splitting via sqrt(-1) in Q_p and the actual absolute-Galois restriction map; root owns comparison and character condition; padic_squares owns exact field arithmetic. (2) Actual inertia via the pinned ramification APIs; local_inventory owns read-only feasibility check. (3) Finite-depth detection and completion of whichever actual local condition route1 or2 supplies; no generic local labels count as the new arithmetic identification.

Proof means compiled Lean under the pinned toolchain with no added axioms/placeholders and exact hypotheses, plus independent raw-source audit. Finite tests provide bounded corroboration only. The critical comparison is the map from absolute local Galois actions to the global root action, not merely a homomorphism named restriction.

## Structural checkpoint

All eight production sources now compile under warnings-as-errors. Route1 supplies the actual field-map comparison and the criterion for every arithmetic prime, not merely3/5. Route2 supplies actual valuation-inertia fixing, together with existence of locally dominating valuation rings. Route3 supplies simultaneous completion of actual local restrictions with proved closure and explicit finite equations, including odd-prime inertia conclusions. The intended stronger statement identifying every local decomposition subgroup with the whole absolute Galois group was not needed and is not asserted. Full PaperX arithmetic packet and period comparisons remain unresolved.
