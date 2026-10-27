# Verification contract and observed development

The exact original Block55 verifier passed at startup, including its selected
nested predecessors. The complete report and log are retained here.

All three new production programs completed successfully during development.
The independent field/orbit/count implementation agreed at every one of the
39,886 directly generated good equation pairs. The algebra program passed
4,200 generated exact matrix cases and the stated local and Weil controls.

## Finite coverage

| Assertion | Coverage |
|---|---:|
| Good equation residues at 197 and 491 | 39,886 |
| Degree-one curve counts in each implementation | 692 |
| Degree-two curve counts in each implementation | 266 |
| Independent polynomial-gcd smoothness checks | 39,886 |
| Generated exact matrix precision/norm cases | 4,200 |
| Of these, nonrational coefficient cases | 3,780 |
| Cases attaining the stated precision bound | 3,600 |
| Cases improving the earlier general m-bound | 2,880 |
| Explicit ramified-local 97/293 controls | 2 |
| Generic compatible Weil-polynomial controls | 2 |

Degree-two counts are deliberately staged: split491 rows failing the necessary
degree-one trace modulo7 are rejected without inventing N2 data. The finite
proof of this reduction is in notes/FINITE_FROBENIUS_CERTIFICATE.md.

## Reproduction manifest

verify.py records actual argv, Python/platform, process IDs, timing, exit codes,
stdout/stderr, input hashes before and after, and result hashes. Each job has
an explicit wall limit. It imposes no additional CPU or memory limit beyond
the execution environment. Exact arithmetic is deterministic and unseeded.

The source archive, named inherited leaves, and all payloads are hashed.
Results are regenerated in a new scratch copy and compared in full, rather
than accepting a cached status flag. The negative control perturbs an N1
value and requires the independent computation to reject it.

Final extracted-ZIP replay and ZIP CRC/member/hash audit are recorded in the
external final verification and archive-audit files. Those records are not
included in their own immutable payload checksums. A separate altered-payload
control tests that the release integrity checker fails.

PASS verifies only the declared finite assertions and byte integrity. It is
not a proof of every unformalized geometric input, independent mathematical
review, a Lean compilation, or a proof of Beal.

The observed development replay returned PASS_DECLARED_CHECKS, including
all nested predecessor checks and the intentionally altered-count rejection.
Its report pins the pre-final-editorial snapshot. The separately recorded
fresh extracted-ZIP replay is authoritative for the final archive bytes.
