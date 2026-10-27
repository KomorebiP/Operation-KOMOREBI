# Development history

An earlier frozen development version passed 16 of 18 endpoints. It solved the natural hierarchy and all cut ablations, but some downstream action heads reached only 89.1% to 98.4% under counterfactual workspace transplantation. Thresholds were not relaxed.

The final dev3 design adds predeclared causal-recombination training only at the downstream interface while freezing the local and global workspace encoders. Fresh holdout seeds are used. This tests whether the hierarchy supports modular counterfactual recombination rather than only naturally co-occurring states.
