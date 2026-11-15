# Review queue: candidate integer sequences

**This is a triage list, not a novelty ranking.** Candidate IDs are internal. The following are particularly useful because they have exact formulas, clear normalization and independent numerical checks. Their first task is a search for known OEIS sequences, transforms, arrays and literature.

| Group and internal ID | Candidate | Why review |
| --- | --- | --- |
| `KOM030..KOM035` | Logarithmic derivatives of N=3..8 generalized Euler blocks | Exact integral filtered-EGF coefficients, with clear connection to the project's core machinery |
| `KOM023..KOM028` | Higher reciprocal powers N=5..8 | Integer Hurwitz products of established block sequences; compare carefully to Mittag-Leffler inverse-power arrays |
| `KOM043..KOM046` | Hankel determinants of generalized Euler blocks | Determinantal invariants of established integer families; short samples currently |
| `KOM047..KOM057` | Odd-prime valuations of Euler reciprocal blocks | Directly relevant to the earlier open p-adic valuation questions; choose nonconstant examples |
| `KOM066..KOM068` | Subsets of residues with prescribed sum mod N | Cyclic projector and roots-of-unity counting with a second brute-force verification |
| `KOM069..KOM074` | Kummer carry distributions and row valuation sums | Digit/carry statistics and Frobenius-error fingerprints |
| `KOM082..KOM084` | Smith-inspired transfer polynomial coefficient statistics | A specific integer polynomial recurrence with independent exact checks, not a claim about all RLC networks |
| `KOM085..KOM087` | Identity words in the 24-element single-qubit Clifford group | Matrix-free exact count of ordered gate words modulo global phase |
| `KOM058..KOM065` | Digit sum / polyphase residue counts | Explicit finite-state transition matrices; likely existing transforms, useful as controls |
| `KOM075..KOM081` | Totient prefix, Collatz and ladder controls | Mathematically well-defined, but often classically known or heavily represented in OEIS |

**Before any submission**, perform these checks in order:

1. Search the candidate's first 12–20 terms in the current OEIS corpus and on the OEIS website, including sign, shift, bisection, decimation, binomial and Stirling transforms.
2. Verify the exact offset, the formula in mathematical notation and an independent implementation of the generator. Avoid claiming a theorem based solely on matching output.
3. Check existing multi-parameter arrays. A new fixed-parameter row of a known array is rarely a new mathematical discovery.
4. Supply an explanatory interpretation, reference or nontrivial recurrence, not only a list of computed terms.
5. Extend short b-files for promising candidates where computationally practical, keeping every term exact and checking for index/normalization mistakes.
6. Attribute historical mathematics accurately. The original project has developed new transfer relationships, but one cannot infer that the underlying integer sequence is new.

Files `CANDIDATE_REGISTRY.csv` and `candidate_registry.json` are the authoritative machine-readable catalog for this batch.
