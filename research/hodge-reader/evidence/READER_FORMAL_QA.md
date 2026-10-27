# Reader mathematical proofreading and source assurance

Review mode: conservative review only. No author-owned mathematical source was edited by this reviewer. This is source assurance and local mathematical proofreading, not Lean compiler verification or an independent proof of every manuscript theorem.

## Completed source scope

Read the complete first August development and then reread the revised local passages. Read all final reader inputs: `main.tex`, `opening.tex`, `august_development.tex`, `carrier70.tex`, `transfer210.tex`, `capacity_cycles.tex`, `weil_audit.tex`, `edition_audit.tex`, `appendices.tex`, and `bibliography.tex`, all six table inputs, and `shared/preamble.tex`. The complete reviewed 17-file input set is pinned in `reader_source_assurance.json`. The earlier pre-assembly inventory is retained in `reader_source_probe_before_assembly.json`.

The applicable proofread-math skill was read in full, with its checklist. Findings outside a uniquely forced local correction were reported to the author instead of repaired silently.

## Findings sent to the author

| Location or formula | Finding | Requested local resolution |
|---|---|---|
| Master obstruction projector | Rational Hodge and cycle subspaces are used as ranges of orthogonal operators on real cohomology | Define their real extensions and use these as projector ranges |
| Balanced Fourier criterion (7.3) | `a` is a six-entry address, while `B_m` was defined as a count-vector set | Write `n(a)` in `B_m`, or state the identification |
| Three-primary four-packet | The `r,b` domain is not stated and the displayed entries require a nontrivial modulus and a positive unit representative below `q` | State the admissible domain and treat the base modulus separately |
| Five-primary formula (12.2) | At `r=1` the final entry is zero, outside the primitive address domain | Restrict the displayed exceptional family to `r>=2` |
| Weighted dyadic reconstruction | `rho_s` is used although only `rho_m` was defined | Define the shorthand `rho_s=rho_{2^s}` and state the exponent range |
| Dual charges | A count vector is used as if it were a residue multiset | Use the weighted residue sum or define the multiset convention |
| K23 Hodge-level identity | `h_{C_P}`, `h_{S_T}`, and `h_L` are not defined locally | Define the Hodge-level sum for a general character block |
| Imaginary selector (16.2) | Product over the set `{c,d,e}` can drop repeated entries | Use the indexed triple or three explicit sine factors |
| CM target correspondence | Later prose refers to `(17.1)` but the revised display has no tag or label | Add a label and use `eqref` |
| Range contraction proof | Final strict inequality is false at `a=b`, although its intended Lipschitz estimate is valid | Express the contraction constant as less than one or qualify distinct points |

All ten findings were communicated to the author and resolved in the final source read. The prime-power base-stratum issue was also sent to the independent mathematical reviewer. The author supplied the separate base-prime argument and cited its classical nonvanishing leaf. The obsolete CM equation-number reference was removed in favor of a descriptive target reference. These findings did not authorize this reviewer to supply a new proof or change theorem scope.

Additional source issues were identified and corrected by the author: the carrier's initial Markdown conversion had destroyed its single-backslash math delimiters, a chapter label did not match the reference, Pandoc imports required `tightlist` and `calc`, Unicode proof-ending marks required normalization, and two local edit strings contained literal backslash-n tokens. The carrier was regenerated and reread in full. The Weil Hermitian definition was corrected from the image macro `im` to the intended imaginary-part notation `Im`. The author also converted manual historical equation tags into scoped labels and automatic equation numbering.

Routine edits made by this reviewer: none. Mathematical-token edits made by this reviewer: none. Author revisions prompted by this review are listed above and preserve their explicit boundary in the reconciled edition.

## Initial static checks

The available seven TeX input files have no duplicate labels and no mismatched or unclosed `begin`/`end` environments. The only symbolic reference unresolved within those then-available files is `ch:carrier70`, expected to be supplied by the new reader main file. Ten citation keys are used in the August development. Their final bibliography resolution is pending final assembly.

The numeric references to the retained historical equation tags were read manually. The missing `(17.1)` reference was reported. Removed figure blocks do not leave any symbolic figure references in the available source.

## Final static assurance

The reviewed final source set has 111 labels, 32 symbolic references, and 35 bibliography keys. There are no duplicate labels, unresolved symbolic references, missing citation keys, duplicate bibliography keys, missing input files, missing referenced graphics, mismatched or unclosed environments, or literal backslash-n insertion tokens in the checked source. The retained `ch:carrier70` reference now resolves. These are static source checks rather than a full TeX parser or theorem verification.

The final stabilized build log reports a 126-page PDF. It has no undefined references or citations, multiply defined labels, missing characters, fatal errors, or overfull boxes. The four overfull warnings in the initial 130-page build were reported and resolved, and the cramped inherited diagrams were replaced before this freeze. The final presentation revision widens the contents number slot and replaces three inherited proposition-heading descriptions; these changes do not alter a theorem or proof. A successful build does not independently certify the mathematics. The final reader SHA-256 is `9fe0ad078543e195cbf8d1ff7bd0115de23c9adefbb09a7e4b7e48c3a71775ee`.

The static check can be refreshed after any source or layout change with:

```text
python evidence/reader_source_assurance.py
```

The script writes hashes, locators, exact reference/citation inventories and build-log observations to `reader_source_assurance.json`. A change in a pinned source requires this assurance record to be refreshed before treating it as the current revision.

## Counts and status consistency

Read `computation/COMPUTATION_AUDIT.md` and the scalar fields of the current result records used for the reader's key counts. The reader agrees with the fresh records: 24 carrier checks, 46 transfer checks, 137 capacity/cycle assertions, 241,920 support monomials, 218,836 balance instances, 364 regenerated K23 certificates, 8,336 age comparisons, and 87,376 weighted dyadic coefficient checks for exponents 3 through 9. The 924-basis Weil claim and 18 tolerance-based toy checks agree with their declared finite domains. These figures are not summed into independent geometric theorem counts.

The 89,478,480 coefficient count through exponent 14 is explicitly historical and was not fully replayed. The degree-100 global packet table remains archival rather than a fresh complete census. Uniform dyadic coverage remains a downgraded manuscript claim. The fresh K23 count is an independently regenerated bounded corpus, not universal mixed-conductor coverage or a Chow-map construction. The formal status correctly reports source inspection and a compiler attempt blocked before elaboration. No stale stronger interpretation of those counts was found in the completed source read.

Two additional notation clarifications were reported and resolved: the residue charge is extended by `w(n)=sum_r n_r w(r)`, and the count-vector scaling map `L_k` is defined in the conductor decomposition. No new proof or geometry is involved.

## Remaining review boundary

This review found no remaining source blocker at the final pinned revision. The final build has no layout warnings. Every assigned physical page 51–76 of the preceding 125-page snapshot was inspected individually at full resolution and passed layout assurance. These map to final physical pages 52–77: 25 page bodies are pixel-identical to the inspected baseline pages, and changed page 64 was individually reinspected at full resolution and passed. Footer numbers were validated separately. `READER_FORMAL_LAYOUT_QA.json` pins the final 126-page PDF, the exact revision-comparison file, every final page image and the retained baseline review. The retained diagram's missing spaces before three dimension numerals are a nonblocking copy observation: the numerical values and readability are intact. External theorem authentication and substantive proof auditing are supplied by their separate reports, not inferred from this source check.
