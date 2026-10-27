# Komorebi Unified Inference / Stochastic / Bayesian — v6

All previous checked releases remain unchanged. The active addition is

    CHECKED_RELEASES/FD_Packet_Energy_v0.1.0_Checked

Read its PROOF_NOTE.md, CONTINUE_HERE.md, FINAL_VERIFICATION_RECEIPT.json and sources.
The active slice has 41 compiled modules, 165 audited theorem/lemma declarations,
and 46 new declarations. Counts include support identities and checks.

## Newly CLOSED_CHECKED

Finite self-adjoint rectangular packet energy:

    ||A||F^2 = sum_a sum_b ||Pi_a A Lambda_b||F^2

when both output and input families are complete. Local parent-to-descendant
energy is exactly additive without requiring global completeness. A coarsen
constructor proves grouped packets valid and preserves completeness. Vector mean
energy has the matching theorem. The norm convention is explicitly connected to
the earlier Frobenius energy and genuine Euclidean norm.

For the gain residual F=PH^T-BS and noise floor R>=sigma I, sigma>0:

    W2^2 <= (sum_ab ||Pi_a F Lambda_b||F^2)
              * (1/sigma+||y-Hm||^2/sigma^2).

The squared stopping condition and a version using certified local upper bounds
are checked. The full two-model factor-coupling cost also equals the sum of mean,
prior-latent and noise-latent packet energies. These are actual-law consequences
of the retained Gaussian coupling, not only matrix identities.

## Strongest next bounded target

Supply certified numerical residual-energy majorants and a noise-floor certificate
to posterior_wasserstein2_le_of_packet_majorants. Start with exact rational or
interval certificates, preserving the interpretation as real matrices and genuine
posterior laws. Then prove a sound candidate-acceptance rule that retains a valid
certified incumbent. Do not silently count ordinary floating-point output as an
enclosure. Strict progress, finite termination and optimality are later claims.

A separate lower-risk target is the unformalized sharper four-term covariance
identity in the research-review supplement. Finite-horizon filtering kernel
recursion is the later probability block.

## Boundaries

Self-adjointness is explicit; it is not inferred from pairwise annihilation.
Square-sum energy is Frobenius/Hilbert-Schmidt, not operator norm. Complete
accounting for a fixed residual preserves total energy and does not improve a
changed approximation automatically. Coupling cost need not be optimal transport
cost. No recovery of all primitive model defects from posterior agreement.

P may be singular, R is positive definite. Explicit posterior versions pointwise;
canonical equality has the original evidence-a.e. scope. The arbitrary-gain Joseph
Gaussian remains an approximation. No automatic factor alignment, verified
floating point, adaptive termination, new general metric axioms, optimal plans,
full sequential filtering, singular innovation, nonlinear/Ito extension or
literature-priority claim.

## Verification protocol

Pinned Lean 4.34.0-rc2, mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
Use the active release MODULE_ORDER.json and verify_blocks.py, one module per
bounded invocation, -j1 -DwarningAsError=true, 40-second process cap. Use a larger
outer tool timeout to let the verifier write a completion receipt. Thirty retained
active modules were freshly rebuilt. No full older continuous-time rebuild is claimed.
All active theorem axioms and final source/direct-dependency hashes are audited.
audit_integrity.py is read-only by default; --seal intentionally creates a new
receipt and requires regenerating affected output/archive manifests.

Root v6 controls supersede older next-task instructions. The predecessor controls
are preserved under HISTORY/v5_root_control and the full v5 ZIP under PRIOR_CHECKPOINTS.
