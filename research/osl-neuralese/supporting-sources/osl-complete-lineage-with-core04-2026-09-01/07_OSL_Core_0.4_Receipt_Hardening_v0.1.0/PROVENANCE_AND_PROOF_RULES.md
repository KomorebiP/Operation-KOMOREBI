# OSL-Core 0.4 Provenance and Proof Rules

Status: normative contract for the finite OSL-Core 0.4 reference runtime and independent kernel. The words **must**, **must not**, and **may** are requirements. The base profile described here preserves the accepted OSL-Core 0.3 source style while hardening receipt verification.

## 1. Verification model

The runtime emits `osl.core.receipt.v2` receipts. The independent kernel validates the source commitment, receipt envelope, known receipt kind, hash chain, terminal outcome, and exact security-critical transitions defined in this document. It reconstructs the protected identity, packet, proof, memory, capability, and action tables, plus transaction lifecycle and protected rollback projections, and compares the reconstructed protected state bidirectionally with the final state. A separately labeled same-runtime replay binds the full interpreter trace and final projection for delegated semantics; numerical algebra and full session-graph refinement are not part of the independent reconstruction and retain their named finite verifiers. A well-hashed payload is not automatically a legal transition; unknown kinds fail closed.

The kernel maintains separate tables for current packets by name, historical packet versions by digest, proofs by unique name and construction digest, proof-resource state, capabilities, memory records, and actions. A historical packet version may establish ancestry, but it may not replace the current named packet when authorizing a proof, memory write, or action.

All packet and proof names are fresh. In particular, `infer`, `communicate`, ordinary proof construction, and trusted attestation must not overwrite an existing name.

## 2. Canonical packet invariants

A packet has stable content identity and mutable policy state.

`content_digest` is the SHA-256 digest of the canonical tuple

```text
(name, content, source_agent, source_lineage, provenance, confidence,
 simulated, parent_digest, latent_source)
```

`packet_digest` is the SHA-256 digest of the canonical packet containing the content fields plus sorted access, binding, quarantine, endorsement, authorization, observation-token, status, obligation, support, refutation, and unresolved fields, excluding `packet_digest` itself.

For a fresh packet, unless a constructor below says otherwise:

- `accessible_to`, `bound_to`, `quarantined_by`, `endorsed_by`, `authorizations`, `observation_tokens`, and `obligations` are empty.
- `simulated` is false, `parent_digest` and `latent_source` are null, and `status` is `grounded`.
- `support` equals confidence, `refutation` is zero, and `unresolved` is `max(0, 1-confidence)` after canonical rounding.
- Confidence, support, refutation, and unresolved values are finite and lie in `[0,1]`.

Every constructor and mutation must produce the entire expected canonical packet. Comparing only selected fields or accepting a recomputed digest is insufficient.

## 3. Packet constructors

| Receipt | Preconditions | Exact construction rule |
|---|---|---|
| `observe` | The observing agent and its active lineage are declared. | Provenance is `observed`. Source agent and lineage are the observer and its lineage. Access, binding, and observation tokens are exactly `{observer}`. Status is `grounded`. There is no parent or latent source. This is the only primitive constructor that creates an observation token. |
| `infer` | The source packet is the current version named by the source program, its status is `grounded` or `admitted`, and the inferring agent can access it. | Provenance is `inferred`. Source agent and lineage are the inferring agent and its active lineage. Access and binding are exactly `{agent}`. `parent_digest` is the source packet's current `packet_digest`. The new content and confidence are the declared inference result. No observation token is created. |
| `simulate` | The simulating agent and lineage are declared. | Provenance is `simulated`, `simulated=true`, source is the simulating agent and lineage, and access and binding are exactly `{agent}`. No observation token or parent is created. |
| `inject` | The target agent is declared. | Source agent and lineage are `external`, provenance is `injected`, access is exactly `{target}`, binding is empty, quarantine is exactly `{target}`, and status is `quarantined`. No observation token is created. |
| `neural_proposal` | The target agent is declared and the feature name is present. | Source agent and lineage are `unresolved`, provenance is `unresolved`, access and quarantine are exactly `{target}`, binding is empty, status is `provisional`, `latent_source` is the declared feature, and obligations are exactly `{origin,lineage,task_relevance}`. No observation token is created. |
| `communicate` | Sender and recipient are declared. The parent is the current source packet, has status `grounded` or `admitted`, and is accessible to the sender. Any named session transition must also be valid. | Content, confidence, source agent, and source lineage are copied exactly from the parent. Provenance is `communicated`. Access and binding are exactly `{recipient}`. `parent_digest` is the parent's current `packet_digest`. Observation tokens, quarantine, endorsement, authorization, and obligations are empty. Status is `grounded`. |

Communication preserves the original source identity but does not transfer the source's direct-observation token. A recipient may therefore record a communicated packet as `communicated` or `foreign`, but never as its own direct observation.

## 4. Packet mutations

Fields not named by a mutation remain bit-for-bit equal to the prior current packet.

| Receipt | Preconditions | Exact mutation |
|---|---|---|
| `bind` | Agent and packet exist; agent has access. | Add the agent to `bound_to`. |
| `quarantine` | Agent and packet exist. | Add the agent to `quarantined_by` and set status to `quarantined`. |
| `endorse` | Status is `grounded` or `admitted`; agent has access, is not in quarantine, and confidence meets the recorded threshold. | Add the agent to `endorsed_by`. |
| `authorize` | Status is `grounded` or `admitted`; agent has access and binding and is not in quarantine. If a proof is named, it is valid and consumed under the proof-use rules. | Add exactly the declared scope to that agent's authorization set. |
| `neural_admission` | The current packet is `provisional`. The recorded origin and relevance proof digests resolve to trusted, fresh attestations for the old candidate content and the admitting agent. | Set source agent and lineage from the origin attestation, provenance to `inferred`, and status to `admitted`; clear obligations; add the agent to binding; remove that agent from quarantine. Preserve all other fields. |
| `neural_rejection` | The current packet is `provisional`. | Set status to `rejected`, clear obligations, and add the rejecting agent to quarantine. Preserve content identity and all other fields. |

## 5. Status anti-laundering rule

Only packets in status `grounded` or `admitted` are eligible as sources for `infer` and `communicate`, or as subjects of endorsement, authorization, ordinary memory writes, and planning. Packets in status `provisional`, `quarantined`, or `rejected` cannot cross one of these boundaries and reappear as an unquarantined grounded packet.

This is a mandatory status rule, not an optional temporal contract. It prevents paths such as

```text
inject -> communicate -> ordinary memory
inject -> infer -> ordinary memory
reject candidate -> communicate -> plan -> execute
```

Reasoning about or communicating simulations remains expressible. Its immediate provenance and parent chain must remain exact, and it never creates a direct-observation token. Applications needing stronger transitive taint policy may inspect the ancestry chain or impose an additional policy profile.

## 6. Proof construction

Every proof name is unique. `created_step` equals its construction-receipt step. The proof digest commits to the construction state: persistent proofs begin with `remaining_uses=null`; affine and linear proofs begin with one remaining use; all begin with `consumed_step=null`. Consumption never changes the construction digest.

An ordinary `proof_construct` has `trusted=false`. A `trusted_attestation` may construct only the trusted origin and relevance forms below. Claims are fixed by proof kind and are not free-form evidence.

| Proof kind | Required construction predicate | Exact claims |
|---|---|---|
| `access` | Agent is in the current packet access set. | `workspace_access` |
| `origin` | Supplied source agent and lineage equal the packet source. | `origin_matches`, `lineage_matches` |
| `clear` | Agent is not in the packet quarantine set. | `not_quarantined` |
| `endorsement` | Agent is in the current endorsement set. | `epistemically_endorsed` |
| `authorization` | Scope is in the agent's current authorization set. | `use_authorized` |
| `observation` | Agent has the observation token and is the packet source with its active declared lineage. | `direct_observation_token` |
| `capability` | The exact capability epoch is live, unexpired, and unexhausted for the agent and effect. | `capability_available`, followed by its exact `grant_digest` |
| trusted `origin` | Packet is provisional; agent and supplied lineage match the declared active lineage. | `trusted_origin_attestation`, `trusted_lineage_attestation` |
| trusted `relevance` | Packet is provisional and the agent and scope are declared. | `trusted_task_relevance` |

Every packet proof binds the packet name, `content_digest`, and construction-time `packet_digest`. Primitive proofs are rechecked against current state when used. A capability proof is bound to the specific grant epoch, not merely to an agent/effect pair; revocation followed by an identical-looking regrant does not revive the old proof.

### Composite use proof

A `use` proof requires fresh premises of kinds `access`, `origin`, `clear`, `endorsement`, and `authorization`, all for the same packet content. The access, clear, endorsement, and authorization premises must refer to the composite agent. The authorization premise must cover the composite scope or the allowed `planning` fallback. At construction, the agent must have current access and binding, be outside quarantine, be endorsed, and have the required scope. Its exact claims are:

```text
workspace_access, origin_valid, not_quarantined, endorsed, authorized
```

### Composite ownership proof

An `ownership` proof requires fresh `access`, `origin`, and `clear` premises for the same packet content. For memory class `observed`, it additionally requires an `observation` premise for the writer. The access, clear, and observation premises must refer to the composite agent. The direct memory predicate in Section 8 must hold at construction. Its exact claim is `autobiographical_write_authorized`.

Premise names resolve to unique earlier proof constructions. Affine or linear premises are consumed once when used to construct a composite proof. Their proven facts remain part of that derivation; later composite validity does not require the already-consumed premise resource to become available again. The composite proof's own resource mode controls reuse of the composite.

## 7. Proof-resource use

- A persistent proof may be used repeatedly while semantically fresh. Each protected use emits `proof_use` with `remaining_uses=null`.
- An affine proof may be consumed at most once.
- A linear proof must be consumed exactly once before normal program completion.
- An affine or linear consumption changes remaining uses from one to zero, records the current step as `consumed_step`, and emits `proof_consume` linked to the immutable construction digest.
- No receipt may recreate, increase, or reset a proof resource.

The use purpose and following protected operation must correspond:

| Purpose | Protected operation |
|---|---|
| `ownership` | `memory_write` using the same ownership proof |
| `use` | `plan` using the same use proof |
| `verification` | `authorize` using the named proof |
| `premise:<new-proof>` | construction of that composite proof |

A proof use emitted during a statement that later rejects may remain unmatched by a successful protected-operation receipt. It is valid only when the same statement boundary explicitly records rejection; its resource consumption is still real unless a surrounding transaction rolls it back.

### Base-profile protected operations

Explicit proofs strengthen a protected operation but are optional in the base profile:

- `authorize` always requires an eligible packet, access, binding, and absence of quarantine. A named proof must be semantically fresh, bound to the same packet and agent, and consumed with purpose `verification`.
- `write_memory` always satisfies every direct predicate in Section 8. A named proof must be an ownership proof for the same packet state, writer, and memory class, and is consumed with purpose `ownership`.
- `plan` always requires an eligible packet, access, binding, absence of quarantine, endorsement, and either `planning` or effect-specific authorization. A named proof must be a use proof for the same packet and agent, with scope `planning` or the planned effect, and is consumed with purpose `use`.

Thus `requires` never replaces the direct state checks, and omitting `requires` never weakens them.

## 8. Memory rules

The base profile always enforces the direct semantic memory predicate. An explicit `requires <ownership-proof>` clause is optional. Omitting it does not bypass provenance, status, access, binding, quarantine, lineage, or observation checks. If a proof is supplied, it is an additional certificate and must match and be consumed correctly.

For every `memory_write`:

1. Resolve `packet_name` to the current packet and require exact equality of `packet_digest`.
2. Require status `grounded` or `admitted`.
3. Require the writer to be declared, accessible, bound, and outside the packet's quarantine set.
4. Require the declared provenance-to-memory compatibility below.
5. Require record `packet_name`, `content`, `source_agent`, and `source_lineage` to equal the packet exactly.
6. If the class is `observed`, require packet provenance `observed`, an observation token for the writer, source agent equal to the writer, and source lineage equal to the writer's active lineage.
7. If `proof_digest` is non-null, require a fresh ownership proof for this packet content and state, writer, and memory class, with a corresponding proof-use or proof-consume receipt.
8. Recompute the record digest and append the record to the writer's ordered memory list.

The compatibility relation is:

| Packet provenance | Permitted memory classes |
|---|---|
| `observed` | `observed` |
| `inferred` | `inferred` |
| `recalled` | `recalled`, `reconstructed` |
| `simulated` | `simulated` |
| `communicated` | `communicated`, `foreign` |
| `injected` | `injected` |
| `foreign` | `foreign`, `communicated` |
| `reconstructed` | `reconstructed`, `recalled` |
| `conflicted` | `conflicted` |
| `unresolved` | `unresolved` |

A stricter deployment may require explicit ownership and use proofs for every protected operation. That is a separate profile; it is not the Core 0.4 base language because proofless, directly checked writes and plans are part of the canonical source corpus.

## 9. Trust and cryptographic boundaries

Canonical SHA-256 receipts provide integrity and predecessor linkage. Source, AST, statement-boundary, terminal, and final-state commitments make silent mutation detectable when the expected source or chain tip is known. The independent kernel must also reject a fully rehashed chain when its transitions violate these rules.

These guarantees have explicit limits:

- A hash chain does not authenticate a principal, sensor, tool, or model. Detecting wholesale replacement of an otherwise semantically valid trace requires a trusted chain tip, signature, authenticated channel, or external manifest.
- An observation token is constructor-exclusive inside OSL semantics. It means that a verified `observe` transition created the token; it is not cryptographic proof that an external event truly occurred.
- `trusted_attestation` receipts are trust roots. Core 0.4 checks their declared kind, subject, agent, lineage, scope, freshness, and use, but does not turn a neural relevance judgment into an independently learned causal proof.
- Capability receipts prove conformance to the reconstructed finite capability ledger. They do not prove that an external tool honored the request or that the represented principal is legally authorized outside OSL.
- The final runtime snapshot is evidence to compare against the independently reconstructed state, not an explanation that validates itself.
- These rules are a finite executable contract, not a proof of the Python implementation, universal noninterference, philosophical identity, awareness, or consciousness.

Within those boundaries, the intended claim is precise: an accepted Core 0.4 trace has a source-bound, kind-correct, fully reconstructed provenance and proof history, and no protected memory or action transition is accepted merely because its hashes are internally consistent.
