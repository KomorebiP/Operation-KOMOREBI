# Route record: approximate polyphase light cone

- **Target:** certify Krylov leakage after thresholding weak inter-phase blocks.
- **Route:** replace binary adjacency by the weighted transfer matrix
  `B[h,g] = ||P_h H P_g||_2`, then compare `H^k` and `H_0^k` by telescoping.
- **Outcome:** proved as written.
- **Strongest result:** phasewise and global certificates for powers and finite
  Krylov polynomials.
- **Finite evidence:** deterministic PSD test, depths 1-8, threshold sweep,
  polynomial test; all certificates passed.
- **First remaining question:** choose a pruning pattern that minimizes measured
  communication subject to the transfer-matrix error budget.
