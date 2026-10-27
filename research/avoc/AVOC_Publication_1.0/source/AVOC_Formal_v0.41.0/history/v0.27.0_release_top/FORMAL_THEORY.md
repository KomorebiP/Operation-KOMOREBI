# AVOC v0.27.0 — finite cost certificates and persistent semantic libraries

## 1. The change in guarantee

v0.26 semantic feedback retained an equivalent no-larger representative for every expression within a specified height. That is a bounded-grammar minimum. A complete behavior table alone does not prove that a deeper expression cannot be smaller.

v0.27 instead certifies lower bounds under every grammar constructor. Induction applies to any finite expression, so the resulting optimum has no grammar-height cutoff.

## 2. Generic lower-bound theorem

Let `Program` be the inherited pure syntax with Boolean literals, three variables, unary negation and binary conjunction, disjunction and xor. Let D be any semantic carrier with an interpretation of those constructors. Write [[p]] for compositional interpretation and |p| for tree-node count.

A table c:D->Nat is `LowerValid` if

    c([[literal b]]) <= 1,    c([[variable v]]) <= 1,
    c(neg(s)) <= c(s)+1,
    c(op(s,t)) <= c(s)+c(t)+1

for each of the three binary operations, every semantic argument and every primitive.

Structural induction proves

    c([[p]]) <= |p|

for every finite p. D need not be finite in this theorem. The syntax and additive unit-node cost are fixed; this is not yet a general variable-arity or arbitrary-cost syntax framework.

## 3. Realization supplies the matching upper bound

A witness family w:D->Program realizes c when

    [[w(s)]] = s,    |w(s)| = c(s).

The lower-bound theorem then gives

    [[p]]=s  =>  |w(s)| <= |p|.

Thus c(s) is attained and globally minimum within the declared grammar. Two accepted certificates must give the same cost for each semantic class, although their witness syntax may differ. Lower bounds remain useful without optimal witnesses: every matching program is an upper witness, leaving a possible gap. Zero-valued lower bounds illustrate why lower inequalities alone are insufficient.

Main names in `Komorebi.AVOC.CostCertificate`:
`lower_bound`, `witness_global_minimum`, `cost_is_attained_minimum`, `exact_cost_unique`.

## 4. Finite Boolean checker

The executable instance represents all eight truth values explicitly. Signature equality is equivalent to the inherited full-input `Equivalent` predicate. The signature index is the integer whose bit i is the output on the i-th lexicographic false-first input.

A row stores its claimed signature, claimed node count and complete expression. The checker requires exactly 256 canonical rows and verifies:

- every signature has a row with exactly matching semantics;
- the stored node count equals the actual expression size;
- all 5 primitive, 256 unary and 3*256*256 binary cost inequalities.

There are **196,869 constructor/primitive obligations**. The generic checker-soundness proof turns their Boolean acceptance into `LowerValid` and `Realizes` propositions.

`CheckedBank` contains rows and a proof of the executed check. Querying it selects the witness for the reference's complete signature. `query_globally_minimum` quantifies over every equivalent finite Program, not only those visited by the original producer or accepted by a bounded file parser.

## 5. Candidate data and evidence level

The supplied concrete bank has 256 behaviors, sum of minimum node costs 1,640, and maximum cost 10. It was generated independently in Python and also exported from a fresh run of the inherited Lean depth-three semantic-feedback generator. All 256 witnesses were byte-for-byte identical after serialization.

The actual new Lean importer accepted both serialized banks. The independent oracle enumerates by exact node-size layers through size 10, rather than repeating height-layer feedback, and agrees on every cost.

An optional monolithic `by decide` proof of the entire concrete table did not complete within its 30-second cap. It is preserved as an unsuccessful experiment, not as a declaration in the library. We rely on the kernel-checked soundness of the checker plus execution of that checker on the data, with the usual compiler/runtime trust. We do not claim a completed standalone kernel reduction of that concrete table.

## 6. Funded import and query

For parsed rows, define a declared full-validation tariff

    validationCharge = 196869 + number_of_rows + 8*sum(actual_expression_nodes).

For the concrete bank this is 210,245. The tariff is deliberately full-price even when a structurally valid but incorrect bank fails early. An unfunded check is not attempted. Parsing and determining the tariff happen outside it.

Each funded query p is charged `8*|p|+1`. The Lean import/query functions prove conservation and non-overspend, including batch queries. If a query is unfunded it returns no result and preserves its current credit; a later cheaper query may still run.

With 300,000 credit and references of 6,3,5 nodes, validation costs 210,245, queries cost 49+25+41=115, and remaining credit is 89,640. The returned programs have 3,3,5 nodes.

These are per-invocation accounting limits, not persistent charges, measured CPU costs or proofs that an unfunded request uses no physical resources.

## 7. A stopping bound

Let p be the incumbent, k=|p|, and l=|query(bank,p)|. Every equivalent candidate q satisfies |q|>=l. For M declared future executions,

    M*max(k-|q|,0) <= M*(k-l).

If a non-stop continuation costs at least M*(k-l), it cannot achieve positive net node-saving value under this task-only objective. At the certified minimum, further grammar search cannot reduce node cost at all.

This does not account for potential cross-task rule-discovery value, new operators, another cost model, approximate equivalence, or a change in the semantic target. It is not a universal metareasoning optimum.

## 8. Persistence

The Python coordinator reads a certificate snapshot, asks the actual Lean implementation to validate it, and publishes exact checked bytes into a new store. READY is written last. Reopening checks the manifest and then revalidates all semantic and cost obligations in a fresh Lean process. The recorded old success flag is never proof authority.

The loader checks schema, grammar, input-order and cost descriptors. Successful parsing supplies the exact rows checked by the semantic function; loaded queries inherit global optimality.

No synthesis is run during reload. A forged checksum or old approval cannot turn an invalid certificate into an accepted one, but checksums are still only integrity fingerprints. Host/source/runtime protection and faithful Python/JSON/filesystem operations remain trust assumptions.

## 9. Reconciliation with previous results

The finite-depth feedback theorem remains unchanged. Its generated output is one possible untrusted source of a certificate. Certification does not trust generation depth or a stability claim. Full validation of constructor lower inequalities is what supports the unrestricted-height conclusion.

The separate v0.26 learned-rewrite branch is not merged here. Its equal-budget early-stop failure is not contradicted: this block answers the exact full-grammar node-minimum question, not the optimal allocation of all physical search and reuse costs.
