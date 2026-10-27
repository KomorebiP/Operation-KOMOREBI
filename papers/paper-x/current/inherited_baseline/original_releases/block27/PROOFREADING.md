# Block 27 proofreading and scope review

Proofread: the new Block 27 manuscript passage, current status sentences, source patch, and release documents.

- Corrected wording: the ledger now says trace independence from Frobenius witness choices; the former wording could be confused with linear independence of characters.
- Mathematical-token corrections in the manuscript after review: none. Current status sentences were updated to include Block 27's result, and the rational arithmetic base was made explicit for general-base source applications.
- Remaining mathematical obligation: general prescribed-conjugacy prime coverage is unproved, as explicitly stated in BLOCK27_SCOPE_RESOLUTION.md. No reviewed current document claims full Claim 9.1 is checked.
- Validation: lexical LaTeX structure passed. Fresh git-apply replay reproduced exact final source bytes. The original Claim 9.1 and proof remain unchanged. No TeX compiler or PDF typesetting was run.
- Independent manuscript review: privatechecks/block27_manuscript_review.md, which discloses the reviewer's authorship of one production module. The separate proof audit independently examined all eight final modules. The final verification substitutions below were checked directly against the completed build and archive-replay JSON.

All 178 production modules passed the clean build. The 2,064 named declarations passed the transitive axiom audit using only Classical.choice, Quot.sound and propext. The block adds 59 theorem/lemma declarations and 16 other named declarations; the cumulative theorem/lemma count is 1,455. All 12 positive controls passed, and 25 false claims plus the placeholder were rejected as intended. All 170 predecessor source and rebuilt proof-object hashes match Block 26. Fresh archive replay reproduced all 8 new proof objects and the retained Block 22 exact regression. Independent exact-source review of all new modules and manuscript review passed.

Reviewed artifact hashes:

- `BLOCK27_TARGET_CONTRACT.md`: `b159f644fecb5201bd0e2289f70c382bbad0439e2fe3e976edfd69950f21bdea`
- `BLOCK27_SCOPE_RESOLUTION.md`: `4d3e5c42a11bd1320cca4698b8ec69137a46e9705c9985d42880b8bd1e92bbc1`
- `GENERAL_COVERAGE_INTERFACE.md`: `a60a1fcaf122da8a5ef1cdbbab33b946d129387288f1a435d73445156b3ccaee`
- `README.md`: `0dc6890fa7e808a26dc012c8e7f7e72e7583a60934e43a40c0f4570007339bbe`
- `Paper_X_TwentySeventh_Block_Ledger.md`: `d1e7252b9102b3c302530970462e0ecdaf19c2c6a2b71fb6339779d52ddfc866`
- `FIVE_PARTIALS_STATUS.md`: `7fceda9bb04d9c9b960cdb685f83468b1f3ffd72b9fcef74cb610a67734f31d3`
- `NEXT_TARGET.md`: `5c713da4d68e148dbe65208fdb82f4ab535b31bd8b5b2364a46a5e21562a3fad`
- `DEVELOPMENT_BLOCK27.md`: `b9e2aa4179ccd406cba141d1ddb9e624d7521aced8440ff8dc2da652cf53bb15`
- `source/Projector_Resolved_Seed_Calculus_X_Block27_Amended.tex`: `e4bf41c74d11e30cb392bf451ab8dff426bc77ae829266d3672ae01b77abdc0f`
- `source/Block27_Amendments.patch`: `fc47ea31cfbd5d907dc60c6df6a20672335eb7e5cb7ef8c96b8f4572e435fee0`
- `proofreading_structure.json`: `b97951956c57506ee6ae82448b0eeb3e900c67994daa8fda7de5296d8e30496b`
- `proofreading_patch.json`: `6114560237d572ab1ad67515738f78d2f7f2a55b511bbb04d4348fef71950c26`
- `privatechecks/block27_manuscript_review.md`: `ee1848d9e32814a492ce40dd5faf1c50da33ad0208adbeffaebf276140780f9e`
- `BLOCK27_PROOF_AUDIT.md`: `e2be6ef546738414683120732fefc7467ef7dfb37ed6f557b16df61a0ad1ef5e`
- `BLOCK27_PROOF_AUDIT_SOURCES.json`: `75d084cc928f13503a0ca71e270c4c40fa36676701365429e7353728ca74e377`
