# Exploratory posthoc geometry audit

This audit was designed after the developmental pilot and is not preregistered evidence.
It asks whether successful decoded computation requires recurrent states to collapse onto the original state-embedding points.

| Arm | D4 length 8 decoded | Nearest original embedding | Nearest empirical state centroid | Within-state variance fraction | Hidden/embedding cosine | Hidden/embedding normalized L2 |
|---|---:|---:|---:|---:|---:|---:|
| linear_terminal | 0.9519 | 0.9246 | 0.9343 | 0.4794 | 0.6399 | 90.6560 |
| linear_relation | 0.9998 | 0.9998 | 1.0000 | 0.2129 | 0.8258 | 4.0390 |
| gru_terminal | 0.4812 | 0.3152 | 0.4539 | 0.8973 | 0.2188 | 1.0067 |

## Reading

High decoded accuracy with materially lower nearest-embedding recovery means the recurrent trajectory need not return to a single canonical point for each state. The relevant semantics can instead occupy a path-dependent region or decision-equivalence class. Relation regularization can then be evaluated by how strongly it contracts those classes without assuming exact point identity.
