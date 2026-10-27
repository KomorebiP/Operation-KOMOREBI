# Block matrix and actual system development

The block matrix builder reported an initial compilation failure on local simplifier normalization. The proof was repaired without changing any theorem hypothesis, and PolynomialBlockInverse compiled with default limits and warnings treated as errors.

The actual system builder reported a first compilation failure involving disjoint Fin indices, followed by unused simplification-argument warnings treated as errors. The third compilation passed after the local equality simplification and unused arguments were repaired. PolynomialJointSystem retains the stated generic coefficient-ring definitions and actual derivative identities.

These are summaries of observed builder results, not reconstructed raw logs. Exact final source hashes and the authoritative fresh build are recorded separately by the source inventory, verification report and independent reconciliation.
