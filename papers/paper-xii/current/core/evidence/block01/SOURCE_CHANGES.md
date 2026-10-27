# Paper XII — source change register

Reading release 1.0.0, 10 October 2026.

The 516 retained editable predecessor files have 496 byte-identical counterparts and 20 changed counterparts in the current source tree. New root build/replay tools and reading-route files are additions, not silently substituted scientific sources. The complete patch and per-file before/after hashes are in `SOURCE_CHANGES.patch` and `SOURCE_PRESERVATION.json`.

## Mathematical preservation

All 52 explicit main proof bodies and all 82 main statement-environment bodies are byte-identical. No new theorem amendment is introduced. The 96 production Lean modules, all raw declaration/claim JSON and CSV records, and the 24 exact teaching modules are unchanged. The rendered claim table differs only through added cross-document link wrappers; removing those wrappers recovers its exact previous text.

## Presentation changes

The three wrappers, styles, reader READMEs and build adapters use the coordinated release builder and installed fonts. The monograph has a new reading map and contents. The visual guide has explicit V-numbered lessons and one complete lesson per page. The Lean guide has a new evidence/reading route and a one-page contents list. Dates refer to the present reading release, not a new compiler run.

The bibliography and its generated BBL add the documented appendix relationship for Adequate subgroups. The other mathematical bibliography entries retain their data. All 27 citations resolve.

Four main vector files were replaced by corrected generated figures: `09_hecke_artin_packets.pdf`, `14_companion_spine.pdf`, `16_pointwise_automorphy.pdf`, and `17_final_completion.pdf`. Their routes avoid crossing labels and expose the stated mathematical hypotheses. Fourteen other main vector figures are unchanged. The rebuilt guide retains its existing exact visual objects and tests.

## Distribution exclusion

The retained predecessor contains 2,243 byte-preserved files. Nine standalone font files were deliberately omitted. The exclusion list contains their paths and hashes, not font bytes. The original received current manifest was checked before exclusion. The root release manifest is authoritative for the sanitized distribution.
