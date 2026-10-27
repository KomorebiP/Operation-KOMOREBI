# OSL-Core 0.3 and SIWC v0.5 continuation summary

## Central advance

This continuation closes the prior gap between tested interpreter behavior and independently checkable finite semantics.

OSL-Core 0.3 now has four distinct evidence layers:

1. source-program conformance over 66 accepted and safe-rejection programs
2. deterministic source-to-receipt replay
3. an independent receipt/proof reconstruction kernel
4. exhaustive exploration of one integrated and five decomposed finite transition systems

The combined finite evidence covers 1,149 receipts, 70 proof terms, 2,330 reachable abstract states, and 47,958 attempted transitions. All declared checks pass.

## New language mechanisms

- persistent, affine, and linear proof resources
- exactly-once completion checks for linear proofs
- append-only audit receipts surviving rollback
- source-statement before/after semantic boundary receipts
- proof freshness and semantic revalidation
- finite session graph verification
- explicit secret-to-metadata flow analysis
- adversarial rehashed semantic-forgery rejection
- a unified machine-readable certificate stack

## SIWC integration

The SIWC manuscript now contains an executable realization section mapping its modal relations into OSL runtime objects and proof resources:

- workspace access
- causal binding
- quarantine
- endorsement
- typed autobiographical ownership
- planner use
- authority and execution
- consequence feedback

The section states finite correspondence, non-forging, planner-use, linear ownership, and bounded-feedback results while retaining a clear boundary around the still-open proof-assistant and open-environment theory.

## Exact boundaries

The finite certificates do not prove arbitrary OSL programs, universal noninterference, unbounded distributed liveness, neural semantic truth, or phenomenal consciousness. The Python implementations and certificate generators remain trusted software. The next formal milestone is a proof-assistant kernel for the typed AST, safe progress, linear-resource preservation, and receipt-trace correspondence.
