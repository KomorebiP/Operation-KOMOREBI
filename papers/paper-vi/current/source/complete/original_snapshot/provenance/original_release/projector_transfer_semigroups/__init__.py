"""Projector-resolved transfer semigroups.

Finite and spectral models for Markov, Bayesian, fractional, PDE, and latent-state
transfer systems used in Projector-Resolved Seed Calculus VI.
"""

from .packets import (
    coordinate_projectors,
    packet_blocks,
    reconstruct_from_blocks,
    block_composition,
)
from .semigroup import (
    matrix_semigroup,
    packet_semigroup_blocks,
    feshbach_effective_operator,
    projected_resolvent,
    memory_kernel,
    generator_refinement_defect,
    semigroup_refinement_residual,
    duhamel_defect_integral,
)
from .markov import (
    symmetric_random_walk,
    exact_lumped_chain,
    evolve_markov,
    lumping_defect,
    survival_curve,
)
from .bayes import (
    bayes_update,
    packet_bayes_update,
    beta_binomial_posterior,
    bayesian_flow,
    bayesian_flow_generator,
    hmm_filter,
    coarsen_probability,
    effective_coarse_likelihood,
    bayesian_coarsening_defect,
    bayesian_sufficient_partition,
    canonical_bayesian_partition,
)
from .conditional import (
    weighted_conditional_expectation,
    martingale_differences,
    gaussian_hermite_gram,
    ornstein_uhlenbeck_eigenvalues,
)
from .fractional import (
    spectral_fractional_power,
    fractional_semigroup,
    scalar_square_root_subordination,
    generator_intertwining_defect,
    fractional_intertwining_defect,
    fractional_holder_bound,
    fractional_gap_bound,
    fractional_semigroup_intertwining_defect,
    fractional_semigroup_bound,
)
from .pde import (
    dirichlet_laplacian_1d,
    continuous_dirichlet_green,
    discrete_green_scaled,
    low_mode_eigenvalue_error,
)
from .feynman_kac import (
    discrete_feynman_kac,
    enumerate_feynman_kac,
)

__all__ = [name for name in globals() if not name.startswith("_")]
