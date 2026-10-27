# Route record: nonsemisimple norm

Base: v0.31 archive c9c0669f3993ffff06728ea5ae1d806a3201132747ceb162701c44a45638af59.
Target: compute the genuine norm image without a semisimple eigenvalue-only assumption.
Success: operator image/kernel theorem plus an iff for the inherited actual prescribed root.
Failure control: identity action versus unipotent action with the same sole eigenvalue 1.

Mechanism: factor S_d(X) at lambda, evaluate in the noncommutative endomorphism
ring, and retain the nilpotent power while proving the other factor is a unit.
Polynomial cancellation occurs only in k[X]. The final actual matrix comparison
proves its conjugation formula rather than assuming a list of spectral eigenvectors.

Outcome: proved at the scopes in RESEARCH_BOUNDARY.md; all numerical corroboration
is finite and independently specified. An actual unipotent cube prescription
has a nonzero liftable mismatch, while another prescribed mismatch is obstructed.

No norm-image statement is promoted to global arithmetic vanishing or automorphy.
