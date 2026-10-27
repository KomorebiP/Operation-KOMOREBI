# Assistance and provenance

The author credit in the reading edition is Komorebi P., following the established project identity.

The monograph and this final proofreading were prepared with AI assistance in the current collaboration. Work included organization of supplied notes, ordinary proof review and expansion, exact-arithmetic implementation, testing, reference checking, vector figures, and LaTeX production. This is not an independent human referee report, and it does not assert separate author approval of every proof.

The final review found and corrected an overstatement about reflection of isomorphisms by profinite completion. The earlier argument used D as a source object while its statement was restricted to the groups G_A. The revised text distinguishes those categories and proves the positive reflection statement for the paired-prime subcategory. It also corrects terminology for computable profinite presentations, clarifies proof hypotheses, and rejects malformed numeric inputs that the earlier implementation silently accepted.

The original two research archives remain unmodified in `provenance/`. `provenance/Prior_Monograph_Records.zip` preserves the predecessor's README, ledger, assistance note, and verification records. Those files are historical evidence, not the current verification record. `verification/input_provenance.json` identifies the supplied predecessor PDF and source archive by hash, and `verification/finalization.patch` records editable source changes.

The book supplies ordinary proofs. No Lean verification, independent external certification, or exhaustive historical-priority audit was performed. No noncomputable selector was evaluated by the Python programs. The current exact tests, source correspondence, and visual checks are recorded separately.

The reading edition intentionally omits development versions and operational logs from its narrative. Technical records remain available here for inspection.
