# Source map and literature-review scope
**Self-Improving Intelligence v0.2.0 · 8 October 2026**

The authoritative immediate predecessor is the supplied v0.1.0 PDF and source ZIP. Its full LaTeX was used as the editing base. All twelve statement/proof pairs and three core reference programs were checked for exact preservation. This is not a new independent audit of every inherited proof.

The original source map, including the selective scope of SRIC, Machine Understanding, Neuralese, OSL, and the earlier public literature review, is preserved as `lineage/v0.1.0/SOURCE_MAP.md`. No earlier neural performance result is imported as evidence for this manuscript.

## Added primary references

### [17] Arnab Nilim and Laurent El Ghaoui
*Robust Control of Markov Decision Processes with Uncertain Transition Matrices*. Operations Research 53(5), 780–798, 2005. DOI: 10.1287/opre.1050.0216.

Primary records checked:
- https://pubsonline.informs.org/doi/abs/10.1287/opre.1050.0216
- https://people.eecs.berkeley.edu/~elghaoui/pubs_rob_mdp.html

Use: background for control under uncertainty. The manuscript does not import a robust-MDP rectangularity theorem. Its unknown model label is fixed along each trajectory, and that dependence is preserved explicitly. Review was at primary abstract/metadata level rather than a complete proof audit.

### [18] Armando Solar-Lezama, Liviu Tancau, Rastislav Bodík, Sanjit A. Seshia, and Vijay Saraswat
*Combinatorial Sketching for Finite Programs*. ASPLOS 2006, 404–415. DOI: 10.1145/1168857.1168907.

Primary records and author copy checked:
- https://people.eecs.berkeley.edu/~sseshia/pubs/b2hd-solar-asplos06.html
- https://people.csail.mit.edu/asolar/papers/asplos06-final.pdf

Use: the established distinction between supplying a program sketch/template and synthesizing its completion. The author PDF was available for targeted text inspection. No claimed theorem from this paper is used as an unproved premise of the new compiler certificate.

## Inherited references checked again for the new use

**Howard, Ramdas, McAuliffe, and Sekhon, Time-uniform Chernoff bounds via nonnegative supermartingales**, Probability Surveys 17, 257–317, 2020, DOI: 10.1214/18-PS321. Primary metadata was recovered. A direct DOI fetch returned an internal error and an alternative full-text route did not supply readable content in this session. The new elementary betting-process proof is given in full; the citation locates the established general method, not an undisclosed imported theorem. Original arXiv record: https://arxiv.org/abs/1808.03204.

**AIDE²**, https://arxiv.org/abs/2609.26457 and https://arxiv.org/html/2609.26457v1. The primary record and selected text were rechecked, including the limitation that the tested outer-loop improvement performance was not decisively better than the strong baseline. The manuscript retains the preprint status and does not infer general recursive acceleration.

**Hyperagents**, https://arxiv.org/abs/2603.19461 and https://arxiv.org/html/2603.19461v1. Primary records were available. The prior review's qualifications about version metadata and the supplied selection procedure remain in force; this revision does not claim a fresh full-paper replication or reconciled author/version audit.

## Retrieval failures and limits

Some broad searches returned irrelevant pages, which were not used. Failed direct fetches were not counted as full-text review. Full texts were not obtained or re-audited for every inherited reference. This is a targeted primary-source check, not a comprehensive novelty or priority search. Bibliographic order and citation keys are checked mechanically in the main source audit.

No third-party full text, private conversation transcript, or font files are included. Sources remain independently inspectable at their original locations. The new results' validity rests on the self-contained conditional proofs, not on a count of references or test assertions.
