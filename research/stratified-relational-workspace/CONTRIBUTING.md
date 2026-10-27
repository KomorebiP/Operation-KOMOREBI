# Contributing

The repository is intended first for mathematical review, reproducibility work, and correction of the monograph.

## Before opening a pull request

Open an issue when the proposed change affects a theorem, definition, priority classification, empirical gate, bibliography entry, or licensing statement. Small typographical corrections may proceed directly to a pull request.

## Mathematical review reports

A useful report contains:

1. the theorem, proposition, definition, equation, page, or source label;
2. the exact assumption or inference being challenged;
3. whether the concern is a false statement, missing hypothesis, proof gap, novelty overstatement, notation conflict, or empirical-identification problem;
4. a counterexample, derivation, citation, or reproducible calculation when available;
5. the smallest proposed correction that resolves the issue.

## Pull-request requirements

- Keep mathematical and editorial changes separate when practical.
- Do not edit generated files under `build/`, `dist/`, or `verification/results/`.
- Update `ERRATA.md` and `CHANGELOG.md` for substantive corrections.
- Update `audits/priority_register.csv` when a novelty or precedence assessment changes.
- Run `python scripts/repo.py verify --strict` before requesting review.
- Explain any deliberate change in page count, theorem count, or expected verification metadata.

## Contribution and licensing status

The repository currently uses an all-rights-reserved notice. Opening an issue does not transfer rights. Before a third-party contribution is merged, the maintainer and contributor should explicitly confirm the terms under which that contribution may be distributed. No pull request should alter authorship or licensing without prior discussion.

## Scholarly responsibility

Automated checks are regression tools, not independent proof verification. Contributors remain responsible for the mathematical and factual content of their submissions.
