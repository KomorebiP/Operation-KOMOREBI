# Visual rebuild — Proof Path Theory 1.5.0

This is a redesign of the mathematical illustrations and reading structure,
not a second color treatment of the prior figures.

## The visual argument

The opening pages introduce the distinction between a certificate and its
ambient proof field. Five illustrated part openers then lead into the actual
mathematics. Four worked visual studies sit beside the realization bridge:
restriction maps, missing whole supports, an exact negative witness, and
rank-based information gain. The preceding theorem and the visual example
remain separate, so neither is presented as a substitute for the other.

The compressed-certificate diagram now shows a concrete collision between two
archives. The recoverability figure uses the exact four-archive retention
diamond, rather than suggesting that teaching, discovery, and formal views
always occupy a fixed hierarchy. Set Cover is shown as a membership matrix,
with an explicit AND gate for the target. The canonical core retains its real
conjunctive premise and marks the failed candidate as uncertified.

The binary realization figure uses a genuine three-dimensional cube with all
eight vertices labeled. No continuous solution plane is implied. Review
figures separate correlation from a persistent common offset, state their
parameters, label logarithmic axes, and avoid using consensus as a truth score.

## Page and type design

- Native LaTeX mathematics and selectable text are preserved.
- White reading pages use quiet running heads, restrained pine/ochre accents,
  and figures built at their intended physical width.
- Repeated rounded theorem boxes were removed. A light left rule marks theorems
  and worked examples without turning every paragraph into a panel.
- Five part openers have distinct mathematical illustrations, not generic plates.
- Long section titles break between words, not through them.
- The theorem ledger has wider statements, separate evidence labels, and
  implementation support on a second line.
- A nearly empty overflow page was removed by adjusting one figure's height,
  not by reducing the type throughout the book.
- The cover uses the exact dependency geometry of the canonical AND-DAG, not
  ornamental circles or an unrelated illustration.

## Figure inventory

The manuscript contains 22 numbered figures. The cover motif is separate.

- `fig_00_theory_map`: Five reading routes through the monograph.
- `fig_01_architecture`: The same proof field supports distinct verification, realization and recovery questions.
- `fig_02_and_dag_core`: Exact least core of examples/and_dag.json; the AND premise is retained.
- `fig_03_alternative_hypergraph`: Two alternative certified routes with stored costs one and three.
- `fig_04_certificate_complexity`: Membership matrix for the exact Set Cover instance with one minimum highlighted.
- `fig_05_recoverability_preorder`: Exact four-archive retention diamond, not a claimed hierarchy of all presentation formats.
- `fig_06_loss_vectors`: Exact five-coordinate retained/lost values from the canonical AND-DAG.
- `fig_07_bridge_dominators`: Declared bridge graph with a bypass and a two-target dominator.
- `fig_08_submodular_greedy`: Exact and greedy values from the retained finite coverage instance.
- `fig_09_version_invalidation`: Changed L1 and its exact syntactic descendant review set.
- `fig_10_effective_reviewers`: The equicorrelated-review count with explicit logarithmic scaling and endpoint values.
- `fig_11_audit_queues`: Three committed constant-rate audit trajectories.
- `fig_12_refinement_goals`: Objective values and exact minimizing depths for three declared tasks.
- `fig_13_repository_workflow`: Inspect the actual record, software, checks and publication layers.
- `fig_14_ambient_field`: Certified, unresolved and locally refuted routes have distinct logical roles.
- `fig_15_whole_support`: Worked pairwise-cover counterexample to whole-support gluing.
- `fig_16_restriction_bridge`: Explicit local rule model diagram and its restriction maps.
- `fig_17_binary_cube`: Eight binary vertices with four parity states and two protected realizations.
- `fig_18_observation_partitions`: Three observations of the same binary fiber, including a redundant two-row output.
- `fig_19_obstruction_witness`: An explicit F2 row witness for the incompatible protected example.
- `fig_20_compression_collision`: Two archives collapse to one certificate and make a side-record task undecodable.
- `fig_21_review_error_floor`: Three explicit MSE curves distinguish individual noise, common offset and shared dependence.

## Reproduction and preservation

Run `python scripts/design_figures.py`. The generator reads the committed
example records and finite data tables. It emits both vector PDFs and PNGs.
The PDF metadata are fixed. Regeneration produced identical hashes for all 46
figure and cover PDF/PNG files in this environment. The Lato font is an installed
dependency; its font files are not included in the delivery.

All 131 mathematical statement/proof environments match the 1.4.0 source.
All 33 stable result IDs are retained. The Python package, tests, formal source,
and inherited Lean evidence are unchanged. Fresh tests and publication checks
are documented in `VERIFICATION_SUMMARY.md`.

The eight-page visual sampler is extracted directly from the final monograph.
It retains the original page numbers and is not a separate mathematical edition.
