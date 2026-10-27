# Claims at checkpoint ABC-20261025-RR5

Base: RR4 archive SHA-256
689847eefd2cf75b9804b574d6613c13d10606e6e805a979cd74facb998ea8ae.
This ledger adds claims without changing the previous checkpoint records.

| ID | Exact scope | Evidence and status |
| --- | --- | --- |
| GG1 | Ordered primitive a+b=c<=X, rad(abc)<=Y: B(X,Y)<=3C(2,delta)Y^(2/3)X^(2delta), X>=2,Y>=1,delta>0 | Proved in routes/global_audit/STATUS_AND_CALIBRATION.md; independently audited. Known elementary baseline, no novelty claim. |
| GG2 | Every fixed epsilon,eta>0: E_epsilon(X)=O_(epsilon,eta)(X^[2/(3(1+epsilon))+eta]) | Formal substitution in GG1; independently audited. Does not imply finiteness. |
| GS1 | arXiv:2410.12234v2 Theorem 1.3 states N_lambda(X)<<_(eta,lambda)X^(0.6+eta), fixed lambda in (0,1) | Primary version and theorem statement checked. Whole source proof not audited here. |
| IG1 | Source location of the IUT III numerical inference and the current LANA eta-map compatibility formulation | Primary attribution/extraction checked; not an independent proof or disproof of actual IUT compatibility. |
| NB1 | For real q0 and V subset R, q0<=sup V iff all finite real upper bounds of V bound q0, equivalently upper cofinality; extended-supremum edge cases included | Proved in routes/numeric_bridge/PROOF_NOTE.md; independently audited. |
| NB2 | Realization within finite loss E>=0 plus common finite output bound b gives q0<=b+E; for nonempty bounded-above V the least loss is max(0,q0-sup V) | Proved and independently audited. Actual IUT realization and loss bound remain unverified. |
| NB3 | Fixed K>0, K log c<=K log rad(abc)+F and F<=delta log c+C_delta uniformly over all triples for every delta>0 imply all-epsilon constant-form ABC | Proved conditional implication and independently audited; no such F is constructed from IUT. |
| UH1 | Defined local lattices and GL_k(O) changes require normalized hull enlargement at least (average s_j-1)m log q, attained in the stated class | Proved in routes/unit_hull/PROOF_NOTE.md; independently audited. The corresponding sublinear-cost proposal is refuted only in this class. |
| IUT-OPEN | An admissible S produces the native q-pilot comparison eta^q=eta^anab_S while preserving sufficient hull bounds, under the full actual IUT definitions | Unverified here. LANA presents this as an unresolved compatibility in its own reconstruction. The source-to-original dictionary and downstream height implication also require checking. |
| ABC | Every-epsilon finiteness for unrestricted primitive positive additive triples | Open in this program; not implied by the established claims. |

Proof review: reviews/elementary_claims.md, with reviewed input hashes in
reviews/elementary_claims_inputs.json. Sources and their separate verification
limits are in SOURCES.md and the response route's SOURCE_RECORDS.json.
