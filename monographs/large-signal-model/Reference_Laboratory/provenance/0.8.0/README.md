# Komorebi Large Signal Model — foundations 0.8.0

**Komorebi P. · 9 October 2026**

This is a mathematical foundations and executable-reference release. Production PR-LASM remains version 2.3.0. No new Lean proof-kernel verification, public publication or license change is claimed.

## Read first

- `theory/FOUNDATIONS.pdf`: the cumulative 118-page volume, 87 propositions with written proofs.
- `theory/DATA_SUPPORTED.pdf`: the 15-page new block, Propositions 80–87, Sections 91–100.
- `theory/VISUAL_NOTES.pdf`: eight pages and six new separately generated mathematical figures.
- `RELEASE_AUDIT.md`: executed results, qualifications and failed attempts.
- `ASSUMPTIONS_AND_DEPENDENCIES.md`: the boundaries between a learned parameter, a supplied representation and a verified domain.

Editable Markdown and generated LaTeX accompany every current document. The unchanged 0.7.0 archive is under `predecessors/` and contains earlier releases.

## Principal results

The perturbed operator family from 0.7.0 is certified with reset weight 1/32 rather than 1/8 at the same declared degree-two coefficient-box radius 1/4096. Exact dual separation and independent Bernstein verification bracket the required repair for the fixed geometry and margin. This is not a global minimum-repair claim. The complete-record error bound stays nontrivial through horizon 29 rather than 7.

A separate, declared two-parameter nonlinear observable model is learned from a dependent five-node signal. Time-uniform regression intervals produce a whole-rectangle curved-domain certificate without reset correction. The feature dictionary, reference measure, parameter family and accessible state are supplied, not discovered. A general observable-moment regression theorem is proved, while its scalar specialization is implemented.

The exact discrete example has final intervals a in [0.356,0.462], b in [0.116,0.290], with density floor 0.248. Its conditional confidence level is 95% under its stated stochastic model and observation assumptions, not an empirical coverage measurement. Its complete-record error can still grow with the horizon. Under the additional Markov minorization hypothesis, single-time marginal errors have a uniform bound.

## Reproduce

Use a separate environment with the versions in `requirements-tested.txt` or compatible packages. No network access is needed for the reference calculations once those packages are available.

```sh
python checks/verify_bundle.py
python checks/verify_source_lineage.py
python run_reference_checks.py --verify-hashes
```

The last command runs eight suites and sixteen example/generator programs. It regenerates some reports and certificates, so verify hashes before replay, not afterward. A checkpointed bounded-runner alternative is:

```sh
python run_reference_checks.py --verify-hashes --batch-start 0 --batch-count 6 --session local
python run_reference_checks.py --batch-start 6 --batch-count 6 --session local
python run_reference_checks.py --batch-start 12 --batch-count 6 --session local
python run_reference_checks.py --batch-start 18 --batch-count 6 --session local
```

The report is marked complete only after all 24 successful scripts. Windows has a supplied PowerShell wrapper, but Windows execution was not performed here.

Individual examples:

```sh
python examples/dependent_signal_generator.py
python examples/dependent_data_certificate.py
python examples/replay_dependent_data_certificate.py
python examples/reduced_repair_example.py
python examples/replay_reduced_repair.py
```

The first command generates a seeded rational five-node process. It is not a sensor-data loader. The learner receives the saved node sequence and fixed protocol, not the generator's true parameters. The independent replay verifies arithmetic and submitted witnesses. It does not authenticate data or verify the physical model assumptions.

Document regeneration requires Pandoc, XeLaTeX and the installed LaTeX packages:

```sh
python theory/generate_data_figures.py
python theory/build_pdf.py all
python checks/audit_documents.py
```

## Release boundary

The new confidence rectangle does not cover the old 0.7.0 operator family: these are two separate examples. Matching reference moments does not identify the continuous and discrete observation measures. Unknown hidden-state identification, general nonlinear dictionary discovery, measurement-error correction and empirical coverage validation are not supplied by this release.

A foundations 1.0 can freeze the declared finite theory after a dependency and assumptions audit. It need not pretend to solve every possible extension. See `CLAIM_LEDGER.md` and `LICENSE_STATUS.md`.
