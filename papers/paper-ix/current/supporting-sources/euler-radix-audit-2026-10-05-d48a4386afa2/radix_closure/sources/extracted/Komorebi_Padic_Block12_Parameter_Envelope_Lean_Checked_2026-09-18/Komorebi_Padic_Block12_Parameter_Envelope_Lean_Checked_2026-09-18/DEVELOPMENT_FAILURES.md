# Development failures and inconclusive attempts

1. The first baseline build command exceeded its outer execution window after
   successfully building 17 of the 19 production modules.  No pass was inferred.
   A subsequent cached build completed successfully, followed by a clean
   warning-as-error rebuild of all 1162 jobs.
2. The first aggregate clean vector replay exceeded its outer command window
   after nine of ten files had completed successfully.  The tenth file was run
   separately.  All ten files have individual zero-exit timing receipts.
3. No Lean proof draft was accepted by weakening a statement.  The exact
   auxiliary-index relation proved stronger than the proposed inequality.
4. No mathematical counterexample was found.
