# Chapters IX–X prose review: SEALED

All eligible nonliteral prose in the six current reader roles has received a comprehensive additional contextual proofreading pass. This is an editorial review, not a proof audit. The root reviewer read the recovered historical appendix and all 16 of its captions; the IX–X owner reviewed the other prose, applied all changes, and reread the changed wording in context.

There are 77 exact edits in 31 files: 68 terminology, navigation, and running-header adjustments, and nine grammar or local clarity corrections. Ordinary internal references now use Chapter or main text, and the formal companion uses Plate X references. The grammar repairs include classification/is agreement, clarifying roots of square systems, making the decomposition-group comparison explicit, and the root-reviewed historical-prose corrections. Historical checkpoint statuses, document identities, source keys, execution records, and provenance qualifications remain intact.

## Coverage

| Chapter | Reader role | Nongenerated active source files | Raw source words before edits |
|---|---|---:|---:|
| IX | traditional | 40 | 65,662 |
| IX | visual | 3 | 4,027 |
| IX | lean | 14 | 12,420 |
| X | traditional | 5 | 18,759 |
| X | visual | 2 | 6,727 |
| X | lean | 4 | 4,784 |

The unique active source closure contains 73 TeX files, including six generated inputs. Its 67 nongenerated sources contain 111,266 raw whitespace-separated source words. These are source counts, including formulas and macros, not an exact English-prose count; role totals overlap on the shared worked atlas. Continuous narrative, theorem/proof connecting prose, instructional explanations, open-problem qualifications, and bibliographic presentation were read. Mathematical displays, dense numeric and identifier tables, exact code/literal records, and scientific figure payloads were preserved and excluded from correctness review. Generated-table opening explanations were read; the dense catalog was not treated as running prose. The inactive historical checkpoint front matter in Chapter X is excluded from coverage.

## Validation

The before/after comparisons preserve all 7,541 mathematical regions, eight literal environments, and 696 inline code/path regions extracted by the documented checks. Labels, input routes, citation targets, graphics commands, environment order, and brace balances are unchanged. The exact old/new journal reconstructs every final source byte for byte from the backups. Two captions have root-reviewed prose changes: an article and introductory comma, and an ordinary paper-to-chapter reference. Their images, formulas, labels, and visual code are unchanged.

No mathematical-token changes were made. No new compilation, Lean checking, external-source verification, or mathematical proof audit is claimed. The root coordinates rebuilding and rendered verification.

## Records

- `ix_x_journal.json`: exact old/new text, locations, rationale, and root review credit.
- `ix_x_changes.patch`: complete source diff.
- `ix_x_validation.json`: per-file hashes and protected-region comparisons.
- `ix_x_report.json`: per-file and per-role coverage.
- `ix_x_before/`: preserved originals for every edited source.

## Remaining editorial item

The generated formal-companion crosswalk still uses “paper column” and “Paper” as a table header. It was left untouched under the no-generated-source-edit rule. The root may adjust its generator during rebuilding. No unresolved objective grammar issue remains in the reviewed eligible prose.

Final terminology closure: five additional ordinary paper-to-chapter references were corrected at the root's request. The protected-region comparisons and exact journal reconstruction passed again via `python editorial/prose_review/ix_x_validate.py`.
