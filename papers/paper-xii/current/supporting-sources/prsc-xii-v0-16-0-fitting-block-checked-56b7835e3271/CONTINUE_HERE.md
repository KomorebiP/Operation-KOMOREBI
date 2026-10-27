# Continue Paper XII after the Fitting block

1. Read README.md, CLAIM_DELTA.json, REVISED_COVERAGE.json, verification.json,
   UPSTREAM_PRESERVATION.json, and the complete remaining 3.1/3.3 records in claim_roadmap.json.
2. Replay `python3 checks/verify.py /path/to/Komorebi_Portable_Lean_4.34.0-rc2`.
   Use the pinned Mathlib revision. A stale PASS is not a substitute for the actual replay.
3. The current source closure proves Claims 6.3, 6.4, 6.5, and 7.1.
   Do not redo this Fitting foundation or treat presentation independence as an assumption.
4. Continue first with Claim 3.1: the actual completed tensor-product quotient
   comparison, retaining the topologies, closed ideals, and complete local-ring
   hypotheses in the source manuscript. Then use that to prove 3.3, the actual
   completed global base-change construction imposing the simultaneous local conditions.
5. Ordinary algebraic tensor right exactness is not the completed tensor theorem.
   Do not promote 3.1 or 3.3 from an ordinary tensor identity alone.
6. The directly replayed closure is under lean/. All 71 original source modules
   are also available unchanged under upstream/v0.15.0/lean/. To extend the whole
   paper, create a separate build root, merge those originals with the 10 new
   modules, and explicitly name which old modules are rebuilt. Do not overwrite
   the frozen upstream directory or copy stale object files into a clean replay.
7. Revised status: 47/49 complete, no partials, two unchecked (3.1, 3.3).
   Original-wording status: 39 complete, 7 partial, 3 unchecked.
   Keep every inherited arithmetic input and statement amendment separate.

## One-line restart prompt

Open this Paper XII v0.16.0 Fitting Block archive, read CONTINUE_HERE.md and README.md completely, replay the pinned Lean checks, preserve the four completed Fitting claims and every original-versus-revised boundary, and continue autonomously with the actual completed tensor-quotient comparison in Claim 3.1 before assembling Claim 3.3.
