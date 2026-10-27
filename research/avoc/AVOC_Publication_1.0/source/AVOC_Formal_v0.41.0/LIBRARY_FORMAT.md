# Checked global library format v1

The certificate is a JSON array:

    ["avoc-global-cost-library-v1", "bool3-not-and-or-xor-v1",
     "lexicographic-false-first-bit0", "eager-tree-nodes-v1", rows]

Rows have length 256 and are indexed by their truth-signature integer 0..255:

    [[b0,b1,b2,b3,b4,b5,b6,b7], nodeCount, expression]

All bi are JSON booleans. Integer bit i corresponds to the i-th lexicographic input (false before true), so variable 0 has mask 240, variable 1 mask 204, variable 2 mask 170. Row correspondence is verified, not presumed from its position.

Expressions:

    ["literal", false]
    ["variable", 0]
    ["not", expression]
    ["and", left, right]
    ["or", left, right]
    ["xor", left, right]

The raw Lean request is

    ["avoc-library-load-v1", certificate, credit, referenceExpressions]

Semantic descriptors must match exactly. Unknown constructors, metadata pretending to be a proof, malformed rows or out-of-bound inputs are rejected. The wrapper additionally rejects duplicate object keys and Boolean values used as integers.

## Published store

A new directory contains `library.json` (the exact validated UTF-8 snapshot), `manifest.json` and `READY` written last. Publication refuses any existing destination. Query checks the stored bytes' integrity, then calls Lean for a full new validity check. `initial_validation` in the manifest is history, not current authority.

No bank is accepted merely because its checksum was updated. Correct semantic witnesses alone also do not suffice: the global constructor inequalities must pass. A valid alternative minimum witness is allowed; optimum costs, not witness syntax, are canonical.

Incomplete stores remain noninvocable and are not automatically resumed. Protected local single-writer storage is assumed. No signature, remote attestation, migration or universal filesystem-recovery claim is made. Current query reads a snapshot; later path content changes do not retroactively change what was checked.

## Charges

The tariff is 196869 + rows + 8*actualNodeSum. Query tariff is 8*referenceNodes+1. Parsing and preflight are not included. A structurally valid but semantically invalid funded certificate consumes the declared validation tariff. An unfunded validator does not run its closure checks, although parsing/preflight still use real resources.

A query request gets an independent caller-supplied credit envelope. This is not a bank account or an idempotent prepaid campaign. Reopening performs full validation again; no cached Boolean approval replaces it.
