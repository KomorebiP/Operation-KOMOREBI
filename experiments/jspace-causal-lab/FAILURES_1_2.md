# Editor 1.2 limitations, corrections and blocked tests

## Blocked direct file-opening test

The extra `checks/check_file_open.py` assay attempted actual file:// navigation through Chromium. `Page.goto` failed with `net::ERR_BLOCKED_BY_ADMINISTRATOR` before page execution. Direct local-file opening is therefore not verified by this environment. The exact HTML did execute successfully via Playwright `set_content`, including model inference, imports, exports, and phone layout. This alternate route is not relabeled as a successful file-navigation test.

## Corrected interface ambiguities

The inherited slider caption said alpha zero was unchanged even when separate manual offsets remained nonzero. It now explicitly distinguishes a zero donor contribution from a manual offset. Sweep diagnostics always suppress manual offsets.

The inherited dimension chip and equation stayed at rank three when the complement or whole state was selected. They now report 61 or 64 edited directions and the appropriate operation.

The first new screenshot retained an intentionally invalid program from the negative test and horizontally clipped the mobile history table. The guided-case reset now resets its live inputs; narrow-screen history rows become complete stacked cards. Browser tests were repeated on the corrected build.

The initial session file-size cap was 1 MB, which could reject a legitimately long exported history. The final import cap is 4 MB while inference stays bounded at 64 actions and 256 total step units. Import never treats stored predictions as authoritative.

## Unchanged research limits

No new training or native-support audit was done. Earlier artificial-projection failures, incomplete memory preservation, no-wire competence, unilateral writing and partner transport are not repaired by this release. Case-selected dose points are exploratory controls, not held-out validation. Session snapshot replay certifies subsequent execution only, not the natural provenance of user-supplied states.
