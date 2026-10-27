# Theorem index

The exact input contract H is in TARGET_CONTRACT.md. All arithmetic claims
below are written proofs under the listed inputs, not Lean-certified results.

| ID | Statement | Required inputs | Proof / finite evidence |
|---|---|---|---|
| B52.1 | Depth>=2 and residual diagonal1 force det_E(1-M) in49O and its norm in7^4Z7 | Integral matrix hypotheses only | notes/FROBENIUS_DEPTH.md §1 |
| B52.2 | Actual good v, Nv=1mod7, n>=2 force7^4 dividing twisted Jacobian order | H2,H3; classical Frobenius formula | Same, §2 |
| B52.3 | n>=2 implies29*43 dividing C | H1--H3; Weil bound; complete43 certificate | Same, §§3--4 |
| B52.4 |71 divides C on inherited reducible branch | H1,H2; complete71 certificate | Same, §4 |
| B52.5 | Good13 forces listed four residue pairs and actual twisted Frobenius -13I | H1,H2; complete13 certificate; Frobenius semisimplicity | notes/COMPATIBLE_KUMMER_COORDINATES.md §§1--2 |
| B52.6 | Good13 implies a_phi=0 | B52.5,H4; local Kummer comparison; exact symbols | Same, §3 |
| B52.7 | Good13 pins local eta_n(F13)=-1/13 mod7^n | B52.5,H3 | Same, §4 |
| B52.8 | Five compatible local coefficient functionals at29,43,71 | H4; exact local symbols | Same, §5 |
| B52.9 | Good29 and good43 force the listed coefficient nonvanishing conditions | H1,H2,H4; complete counts and rational7-torsion argument | Same, §6 |
| B52.10 | Good13 and n1 exclude beta-ramification at71 and simultaneous29/43; require another eligible divisor | H3--H5,B52.6,B52.8 | Same, §7 |
| B52.11 | Good13 excludes inert-minus ramified upper endpoints; ordinary n3 support lies in four residue classes | H3--H5,B52.6; elementary unit-power argument | Same, §8 |
| B52.12 | Old q1504231 nonliftable ray family cannot be the actual diagonal family when13 is good | H4,H5,B52.6; inherited ray obstruction; exact symbols | Same, §9 |

The three executable checks cover distinct finite assertions. They do not
certify the universal source-dependent statements by themselves.
