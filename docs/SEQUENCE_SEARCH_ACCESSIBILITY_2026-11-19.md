# Sequence search, inspection and reproduction audit

Author: Komorebi P.
Date: 19 November 2026.

## Scope

This pass continues the calculator and proofreader work with the Sequence
Library search form, result disclosures, exact-value inspector, and record and
family reproduction instructions. Its browser evidence covers selected desktop
and phone views. It is not a whole-site accessibility certification or a manual
screen-reader compatibility study.

## Search state and keyboard use

- A visible clipboard fallback could retain an older search URL after the
  results or page changed. Query edits, completed searches, and pagination now
  invalidate that fallback. A delayed clipboard response cannot restore an
  obsolete URL or move focus after a newer action.
- Invalid queries retained earlier results without explaining their status.
  The results now identify the previous successful search. The invalid query
  stays available for correction, while scope and filter controls return to
  the applied settings. Explicit failed submission focuses the query and
  associates its error message.
- An invalid initial family-search URL previously left an incomplete view.
  It now shows coherent family controls, an explicit empty search state, and
  disabled result exports and sharing until a search succeeds.
- The generalized-family shortcut hid its own focused button. It now moves
  focus to the result count before scrolling there.
- Saved-record updates from another tab previously rebuilt every result,
  which could restore an older formula and index window from the URL. Without
  an active Saved filter, the update now changes only Save buttons. With that
  filter active, membership is recomputed from the applied search, preserving
  any unsubmitted query draft.

## Exact-value inspection

- Selecting an alternative formula now updates the visible disclosure label
  and its accessible name together.
- Reaching the first or last stored window moves focus from the newly disabled
  pager button to the labelled exact-value region. Intermediate paging retains
  focus on the invoked button.
- An empty index previously became zero through numeric conversion. The
  required field and explicit blank-input guard now retain the current window
  and request a valid stored index.

## Display

The search form and inspector no longer inherit large vertical button margins
from the general reader stylesheet. Mobile insets are capped so enlarged text
has usable space. Syntax-help and inspector controls use grids that can reflow
with font size. Formula selectors and editable index fields retain full text
enlargement.

The actual formula-disclosure label can wrap. Only its decorative source excerpt
is shortened. Result equations retain their natural SVG size inside scrollable
regions. Result-count focus and invalid-query styling are explicit.

## Proofreading and reproducibility

Record reproduction panels now link to each record's actual construction source.
Closed-form records no longer incorrectly name the general registry as their
source. The instructions identify the generator command's JSON output.

Family pages previously named test files missing from the source download. The
bundle now includes both closed-form test suites and their required imports.
Its README and family pages give the same quoted discovery command. Families
with stored records provide a real member ID for reproduction. Definitions
without indexed records use an appropriate heading for sources and checks.

Other prose corrections explain Clear's scope behavior, remove an assumption
that every OEIS comparison has matches, distinguish stored integers from original
rational coefficients, and correct a historical record-count statement. The
documentation now states that Restore defaults resets both differential views
to their shared defaults.

No source formulas, stored integer values, mathematical offsets, or record IDs
were changed.

## Verification

Local checks passed:

- 11 JavaScript search, sharing, and inspection-link tests.
- 12 Sequence Library tests and 10 sequence-atlas tests.
- A production sequence build retaining 2,327 records.
- 21 closed-form tests executed from an isolated extraction of the new source
  ZIP, using its documented command.
- Exact reproduction of the 24 stored terms, offset, and defining formula for
  `KFOR-CF-JET-01` from that extraction.

The focused browser suite is
`tools/test_sequence_search_accessibility_browser.cjs`. It checks the state and
keyboard paths above at 1440, 390, and 320 pixels. Its enlarged-text checks measure
input font size and usable editing room, control containment, and the visibility
of the actual formula label. It also checks selected light/dark text contrast,
plain/typeset preservation, forced colors, and reduced motion.

The suite writes its report and screenshots to the Sequence Library workflow
artifact, including failure evidence if a check fails. The workflow retains the
existing calculator, proof, family, transfer, math, usability, and chart suites.
Consult its report for the exact tested revision and rendered result. Browser
execution uses CI because the local environment's Chromium socket restriction
was already confirmed during the preceding pass.
