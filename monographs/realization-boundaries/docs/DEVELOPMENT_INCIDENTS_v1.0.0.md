# Lean verification report — final release

**PASS. All 45 registered contracts are COMPLETE.**

66 production modules; 813 named source theorems/lemmas; 2188 audited declarations; 205 positive contract declarations; 44 rejection controls; 183 passing command gates.

Accepted receipt: `verification/accepted_v1.0.0/run.json`. Source identity and dependency identity both PASS. Runtime: Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d; Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

Accepted axiom dependencies are restricted to propext, Classical.choice, and Quot.sound. Production admits no placeholder proof, project axiom, unsafe declaration, or native-decision trust axiom. Kernel replay uses the same Lean implementation and pinned imported caches; this is not a second kernel, upstream source authentication, or external peer review.

## What failed during development and how it was resolved

* Full duplicate runtime extraction exhausted workspace disk space. The incomplete duplicate was removed and the already restored pinned portable kit was reused read-only.
* An initial compiler launch required the kit's executable-discovery adapter. The portable verification wrapper now probes and installs that adapter only for that known launch failure; its bytes are included in the accepted dependency snapshot.
* A preliminary baseline ran while new source modules were being added; its source-identity gate rejected the run. No acceptance is based on it.
* Preliminary numeric proof tests attempted kernel reduction through imported opaque definitions. The assertions were moved to explicit native runtime checks with intended failure markers. Universal correctness remains in the separately checked theorems.
* An unaccepted draft accidentally stated finite-code surjectivity onto the entire ambient product. Review rejected that false target; the final theorem quantifies over the actual finite-support subgroup and covers every original normal form.

* Four independent raw-list examples initially expected unused nonprime entries to vanish. The prime-coordinate semantics were correct. Corrected semantic equality tests passed; the failed expectations and explanation remain in review records.
* A preflight cache snapshot used an older import closure after adding new modules. Its final identity gate rejected the run because newly imported dependency endpoints were absent from that earlier snapshot, with no changed bytes at shared endpoints. The final accepted run starts from a fresh project build and snapshots the complete current import closure.
* The PDF build lacked newpx. The publication uses the available Palatino mathpazo family plus explicit AMS symbols; the rebuilt book passed visual review.

Only the final immutable integrated PASS receipt is accepted. Development and preliminary evidence remains labeled accordingly.
