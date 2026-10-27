from __future__ import annotations

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm
from scipy.special import eval_hermitenorm
from scipy.stats import beta as beta_distribution

from .packets import coordinate_projectors, packet_blocks
from .markov import symmetric_random_walk, exact_lumped_chain, survival_curve
from .bayes import (
    packet_bayes_update, beta_binomial_posterior, bayesian_flow, hmm_filter,
    bayes_update, coarsen_probability, bayesian_coarsening_defect,
    bayesian_sufficient_partition,
)
from .conditional import ornstein_uhlenbeck_eigenvalues
from .fractional import (
    fractional_semigroup,
    fractional_intertwining_defect,
    fractional_holder_bound,
    fractional_gap_bound,
    fractional_semigroup_intertwining_defect,
    fractional_semigroup_bound,
)
from .pde import dirichlet_laplacian_1d, continuous_dirichlet_green, discrete_green_scaled, low_mode_eigenvalue_error
from .semigroup import memory_kernel, semigroup_refinement_residual
from .feynman_kac import discrete_feynman_kac


def _save(fig: plt.Figure, directory: Path, stem: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    fig.savefig(directory / f"{stem}.png", dpi=220, bbox_inches="tight")
    fig.savefig(directory / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def make_visuals(output_dir: str | Path) -> list[str]:
    out = Path(output_dir)
    stems: list[str] = []

    # 1. Program architecture.
    fig, ax = plt.subplots(figsize=(13.2, 3.8))
    labels = ["seed", "transfer", "project", "condition", "refine", "complete", "reconstruct"]
    x = 1.35 * np.arange(len(labels), dtype=float)
    ax.scatter(x, np.zeros_like(x), s=760)
    for i, label in enumerate(labels):
        ax.text(x[i], 0, label, ha="center", va="center", fontsize=10.5)
        if i < len(labels) - 1:
            ax.annotate("", xy=(x[i + 1] - 0.34, 0), xytext=(x[i] + 0.34, 0), arrowprops={"arrowstyle": "->", "lw": 1.2})
    ax.text(x[len(labels)//2], -0.56, "semigroup / resolvent / Bayesian normalization / fractional power", ha="center", fontsize=10)
    ax.set_xlim(x[0] - 0.65, x[-1] + 0.65)
    ax.set_ylim(-0.85, 0.65)
    ax.axis("off")
    ax.set_title("Common operator language of the transfer-semigroup realization")
    _save(fig, out, "01_transfer_semigroup_architecture")
    stems.append("01_transfer_semigroup_architecture")

    # 2. Packet block heatmap for a semigroup.
    rng = np.random.default_rng(123)
    a = rng.normal(size=(12, 12))
    generator = -0.12 * (a.T @ a)
    projectors = coordinate_projectors([list(range(0, 4)), list(range(4, 8)), list(range(8, 12))], 12)
    blocks = packet_blocks(expm(0.7 * generator), projectors)
    norms = np.array([[np.linalg.norm(blocks[i][j]) for j in range(3)] for i in range(3)])
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    image = ax.imshow(norms)
    fig.colorbar(image, ax=ax, label="Frobenius norm")
    ax.set_xticks(range(3), ["input 0", "input 1", "input 2"])
    ax.set_yticks(range(3), ["output 0", "output 1", "output 2"])
    ax.set_title("Packet transfer blocks of a contraction semigroup")
    _save(fig, out, "02_packet_semigroup_blocks")
    stems.append("02_packet_semigroup_blocks")

    # 3. Random walk.
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    for steps in (4, 12, 30):
        positions, probs = symmetric_random_walk(steps)
        ax.plot(positions, probs, marker="o", label=f"n={steps}")
    ax.set_xlabel("position")
    ax.set_ylabel("probability")
    ax.set_title("One point-mass seed under repeated Markov transfer")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "03_random_walk_transfer")
    stems.append("03_random_walk_transfer")

    # 4. Exact and defective lumping.
    k, c, kbar = exact_lumped_chain()
    p0 = np.array([0.7, 0.1, 0.1, 0.1])
    exact_fine = []
    exact_coarse = []
    perturbed_coarse = []
    kp = k.copy()
    kp[:, 0] += np.array([0.02, 0.0, -0.02, 0.0])
    for n in range(21):
        exact_fine.append((c @ np.linalg.matrix_power(k, n) @ p0)[0])
        exact_coarse.append((np.linalg.matrix_power(kbar, n) @ (c @ p0))[0])
        perturbed_coarse.append((c @ np.linalg.matrix_power(kp, n) @ p0)[0])
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.plot(exact_fine, label="fine then coarse")
    ax.plot(exact_coarse, linestyle="--", label="exact coarse chain")
    ax.plot(perturbed_coarse, label="perturbed fine chain")
    ax.set_xlabel("step")
    ax.set_ylabel("mass in coarse packet A")
    ax.set_title("Exact Markov lumping and refinement defect")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "04_markov_lumping")
    stems.append("04_markov_lumping")

    # 5. Bayesian packet update.
    prior = np.array([0.12, 0.18, 0.30, 0.40])
    likelihood = np.array([0.2, 0.8, 0.6, 0.3])
    packet = packet_bayes_update(prior, likelihood, [[0, 1], [2, 3]])
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    positions = np.arange(4)
    width = 0.34
    ax.bar(positions - width / 2, prior, width, label="prior")
    ax.bar(positions + width / 2, packet["posterior"], width, label="posterior")
    ax.axvline(1.5, linestyle="--", linewidth=1)
    ax.set_xticks(positions, ["0", "1", "2", "3"])
    ax.set_ylabel("mass")
    ax.set_title("Bayesian normalization couples packet evidences exactly")
    ax.legend()
    _save(fig, out, "05_bayesian_packet_update")
    stems.append("05_bayesian_packet_update")

    # 6. Beta-binomial conjugacy.
    posterior = beta_binomial_posterior(2.0, 3.0, 7, 10)
    x = np.linspace(0.001, 0.999, 600)
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.plot(x, beta_distribution.pdf(x, 2, 3), label="Beta(2,3) prior")
    ax.plot(x, beta_distribution.pdf(x, posterior["a"], posterior["b"]), label=f"Beta({posterior['a']:.0f},{posterior['b']:.0f}) posterior")
    ax.set_xlabel(r"$\theta$")
    ax.set_ylabel("density")
    ax.set_title("Conjugate Bayesian transfer of exponent packets")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "06_beta_binomial_conjugacy")
    stems.append("06_beta_binomial_conjugacy")

    # 7. Bayesian flow.
    score = np.array([-0.4, 0.1, 0.8, 1.2])
    times = np.linspace(0, 6, 180)
    flow = np.array([bayesian_flow(prior, score, t) for t in times])
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    for i in range(4):
        ax.plot(times, flow[:, i], label=f"state {i}")
    ax.set_xlabel("likelihood time")
    ax.set_ylabel("posterior mass")
    ax.set_title("Bayesian update as a nonlinear semigroup")
    ax.legend(ncol=2)
    ax.grid(alpha=0.25)
    _save(fig, out, "07_bayesian_flow")
    stems.append("07_bayesian_flow")

    # 8. Hermite / OU decay.
    xh = np.linspace(-4, 4, 600)
    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    for n in range(5):
        mode = eval_hermitenorm(n, xh) * np.exp(-xh**2 / 4)
        mode = mode / np.sqrt(np.max(mode**2))
        ax.plot(xh, mode + 1.6 * n, label=f"n={n}")
    ax.set_xlabel("x")
    ax.set_yticks([])
    ax.set_title("Gaussian/Hermite packets: eigenmodes of the Ornstein-Uhlenbeck semigroup")
    _save(fig, out, "08_hermite_packets")
    stems.append("08_hermite_packets")

    # 9. Fractional semigroup kernels.
    lap, grid, _ = dirichlet_laplacian_1d(90)
    source = np.zeros(90)
    source[44] = 1.0
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    for alpha in (0.5, 1.0, 1.5):
        kernel = fractional_semigroup(lap, alpha, 0.025) @ source
        ax.plot(grid, kernel, label=rf"$\alpha={alpha}$")
    ax.set_xlabel("x")
    ax.set_ylabel("kernel response")
    ax.set_title("Fractional spectral transfer from one source packet")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "09_fractional_semigroup")
    stems.append("09_fractional_semigroup")

    # 10. Green function comparison.
    discrete, grid, _ = discrete_green_scaled(63)
    exact = continuous_dirichlet_green(grid, grid)
    j = len(grid) // 3
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.plot(grid, exact[:, j], label="continuous Green section")
    ax.plot(grid, discrete[:, j], linestyle="--", label="scaled discrete inverse")
    ax.set_xlabel("x")
    ax.set_ylabel("G(x,y)")
    ax.set_title("Poisson Green kernel reconstructed from the resolvent")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "10_poisson_green_kernel")
    stems.append("10_poisson_green_kernel")

    # 11. PDE convergence.
    ns = np.array([15, 31, 63, 127, 255])
    hs = 1 / (ns + 1)
    errors = np.array([low_mode_eigenvalue_error(int(n), 1) for n in ns])
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.loglog(hs, errors, marker="o", label="first eigenvalue error")
    ax.loglog(hs, errors[-1] * (hs / hs[-1]) ** 2, linestyle="--", label=r"$O(h^2)$ guide")
    ax.set_xlabel("mesh width h")
    ax.set_ylabel("absolute error")
    ax.set_title("Second-order low-mode convergence")
    ax.legend()
    ax.grid(alpha=0.25, which="both")
    _save(fig, out, "11_pde_refinement_convergence")
    stems.append("11_pde_refinement_convergence")

    # 12. Finite Feynman-Kac.
    k2 = np.array([[0.75, 0.25], [0.25, 0.75]])
    potential = np.array([0.15, 0.7])
    terminal = np.array([1.0, 2.0])
    values = np.array([discrete_feynman_kac(k2, potential, terminal, n) for n in range(16)])
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.plot(values[:, 0], marker="o", label="start state 0")
    ax.plot(values[:, 1], marker="o", label="start state 1")
    ax.set_xlabel("number of weighted transfer steps")
    ax.set_ylabel("Feynman-Kac value")
    ax.set_title("Finite-state Feynman-Kac transfer")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "12_feynman_kac_transfer")
    stems.append("12_feynman_kac_transfer")

    # 13. Memory kernel.
    latent_operator = np.array([[-1.2, 0.3, 0.4, 0.0], [0.2, -0.9, 0.0, 0.25], [0.35, 0.0, -1.7, 0.5], [0.0, 0.4, 0.2, -1.4]])
    times = np.linspace(0, 8, 200)
    norms = [np.linalg.norm(memory_kernel(latent_operator, [0, 1], t)) for t in times]
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.plot(times, norms)
    ax.set_xlabel("time")
    ax.set_ylabel("memory-kernel norm")
    ax.set_title("Hidden packets return as an exact memory kernel")
    ax.grid(alpha=0.25)
    _save(fig, out, "13_latent_memory_kernel")
    stems.append("13_latent_memory_kernel")

    # 14. Refinement defect over time.
    coarse = np.array([[-0.4, 0.2], [0.4, -0.2]])
    c = np.array([[0.5, 0.5, 0.0, 0.0], [0.0, 0.0, 0.5, 0.5]])
    e = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0]])
    micro = np.array([[-1.0, 1.0, 0.0, 0.0], [1.0, -1.0, 0.0, 0.0], [0.0, 0.0, -1.3, 1.3], [0.0, 0.0, 1.3, -1.3]])
    fine = e @ coarse @ c + micro
    perturbation = np.array([[0.02, 0.0, -0.01, 0.0], [0.0, -0.02, 0.0, 0.01], [-0.02, 0.0, 0.01, 0.0], [0.0, 0.02, 0.0, -0.01]])
    times = np.linspace(0, 5, 160)
    exact_norm = [np.linalg.norm(semigroup_refinement_residual(c, fine, coarse, t)) for t in times]
    perturbed_norm = [np.linalg.norm(semigroup_refinement_residual(c, fine + perturbation, coarse, t)) for t in times]
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.plot(times, exact_norm, label="exactly intertwined")
    ax.plot(times, perturbed_norm, label="nonzero generator defect")
    ax.set_xlabel("time")
    ax.set_ylabel("semigroup refinement residual")
    ax.set_title("Generator defects propagate by the Duhamel identity")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "14_semigroup_refinement_defect")
    stems.append("14_semigroup_refinement_defect")

    # 15. HMM filter.
    likelihoods = [np.array([0.85, 0.25]), np.array([0.35, 0.8]), np.array([0.9, 0.2]), np.array([0.4, 0.9])]
    states = np.array(hmm_filter(k2, np.array([0.6, 0.4]), likelihoods))
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.plot(states[:, 0], marker="o", label="hidden state 0")
    ax.plot(states[:, 1], marker="o", label="hidden state 1")
    ax.set_xlabel("filtering step")
    ax.set_ylabel("posterior state probability")
    ax.set_title("Prediction followed by nonlinear Bayesian normalization")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "15_hidden_markov_filter")
    stems.append("15_hidden_markov_filter")

    # 16. Survival and hazard.
    transient = np.array([[-0.45, 0.12, 0.0], [0.30, -0.52, 0.18], [0.0, 0.28, -0.60]])
    curves = survival_curve(transient, np.array([1.0, 0.0, 0.0]), np.linspace(0, 12, 241))
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.plot(curves["time"], curves["survival"], label="survival")
    ax.plot(curves["time"], curves["hazard"], label="hazard")
    ax.set_xlabel("time")
    ax.set_title("Survival and hazard generated by a transient semigroup")
    ax.legend()
    ax.grid(alpha=0.25)
    _save(fig, out, "16_survival_hazard")
    stems.append("16_survival_hazard")

    # 17. Exact Bayesian refinement square.
    prior_ref=np.array([0.10,0.25,0.20,0.45])
    groups=((0,1),(2,3))
    likelihood_ref=np.array([0.4,0.4,1.7,1.7])
    _,coarse_likelihood=bayesian_sufficient_partition(likelihood_ref,groups)
    fine_posterior=bayes_update(prior_ref,likelihood_ref)
    coarse_prior=coarsen_probability(prior_ref,groups)
    fine_then_coarse=coarsen_probability(fine_posterior,groups)
    coarse_then_update=bayes_update(coarse_prior,coarse_likelihood)
    residual=np.max(np.abs(fine_then_coarse-coarse_then_update))
    fig,ax=plt.subplots(figsize=(10.5,5.8));ax.axis("off")
    boxes={
        "fine_prior":(.08,.64,"fine prior\n$p$"),
        "fine_post":(.68,.64,"fine posterior\n"+r"$\mathcal{B}_{\lambda}(p)$"),
        "coarse_prior":(.08,.18,"coarse prior\n"+r"$C_{\pi}p$"),
        "coarse_post":(.68,.18,"coarse posterior\n"+r"$\mathcal{B}_{\bar{\lambda}}(C_{\pi}p)$"),
    }
    for x0,y0,label in boxes.values():
        ax.text(x0,y0,label,ha="center",va="center",fontsize=14,bbox={"boxstyle":"round,pad=.7","facecolor":"white","edgecolor":"black"})
    ax.annotate("",xy=(.58,.64),xytext=(.18,.64),arrowprops={"arrowstyle":"->","lw":1.8});ax.text(.38,.70,r"$\mathcal{B}_{\lambda}$",ha="center",fontsize=13)
    ax.annotate("",xy=(.58,.18),xytext=(.18,.18),arrowprops={"arrowstyle":"->","lw":1.8});ax.text(.38,.24,r"$\mathcal{B}_{\bar{\lambda}}$",ha="center",fontsize=13)
    ax.annotate("",xy=(.08,.28),xytext=(.08,.54),arrowprops={"arrowstyle":"->","lw":1.8});ax.text(.02,.41,r"$C_{\pi}$",ha="center",fontsize=13)
    ax.annotate("",xy=(.68,.28),xytext=(.68,.54),arrowprops={"arrowstyle":"->","lw":1.8});ax.text(.74,.41,r"$C_{\pi}$",ha="center",fontsize=13)
    ax.text(.5,.04,f"blockwise-constant likelihood: commutation residual {residual:.2e}",ha="center",fontsize=12,weight="bold")
    ax.set_title("Bayesian conditioning commutes with coarsening exactly at sufficient packets",fontsize=16,weight="bold")
    _save(fig,out,"17_bayesian_refinement_square");stems.append("17_bayesian_refinement_square")

    # 18. Information-loss packet and defect bound.
    contrasts=np.linspace(0,1.0,120)
    defect_norm=[];bounds=[]
    coarse_declared=np.array([0.55,1.10])
    for contrast in contrasts:
        likelihood=np.array([0.55-0.35*contrast,0.55+0.35*contrast,1.10+0.30*contrast,1.10-0.30*contrast])
        record=bayesian_coarsening_defect(prior_ref,likelihood,groups,coarse_declared)
        defect_norm.append(np.linalg.norm(record["defect"],1))
        bounds.append(record["l1_bound"])
    example=bayesian_coarsening_defect(prior_ref,np.array([0.2,0.9,1.4,0.8]),groups,coarse_declared)
    fig,axes=plt.subplots(1,2,figsize=(11.8,4.8))
    axes[0].plot(contrasts,defect_norm,label="exact coarsening defect")
    axes[0].plot(contrasts,bounds,linestyle="--",label="$L^1$ certificate")
    axes[0].set_xlabel("within-packet likelihood contrast");axes[0].set_ylabel("$L^1$ norm");axes[0].set_title("Defect grows from hidden within-packet evidence");axes[0].grid(alpha=.25);axes[0].legend()
    xloc=np.arange(2);width=.35
    axes[1].bar(xloc-width/2,example["effective_likelihood"],width,label="effective likelihood")
    axes[1].bar(xloc+width/2,coarse_declared,width,label="declared coarse likelihood")
    axes[1].set_xticks(xloc,["packet 0","packet 1"]);axes[1].set_ylabel("likelihood");axes[1].set_title("The information-loss packet is their difference");axes[1].legend()
    fig.tight_layout();_save(fig,out,"18_bayesian_information_loss");stems.append("18_bayesian_information_loss")

    # 19. Fractional naturality bounds.
    fine_frac=np.diag([0.45,0.9,1.8,3.2])
    coarse_frac=np.array([[0.6,-0.08],[-0.08,1.4]])
    coarsener_frac=np.array([[0.8,0.1,0.0,0.2],[0.0,0.25,0.5,0.55]])
    alphas=np.linspace(0.08,0.92,120)
    actual=[];holder=[];gap=[]
    for alpha in alphas:
        actual.append(np.linalg.norm(fractional_intertwining_defect(fine_frac,coarse_frac,coarsener_frac,float(alpha)),2))
        holder.append(fractional_holder_bound(fine_frac,coarse_frac,coarsener_frac,float(alpha)))
        gap.append(fractional_gap_bound(fine_frac,coarse_frac,coarsener_frac,float(alpha)))
    alpha0=.58
    times=np.linspace(0,3.0,140)
    sem_actual=[];sem_bound=[]
    for time in times:
        sem_actual.append(np.linalg.norm(fractional_semigroup_intertwining_defect(fine_frac,coarse_frac,coarsener_frac,alpha0,float(time)),2))
        sem_bound.append(fractional_semigroup_bound(fine_frac,coarse_frac,coarsener_frac,alpha0,float(time),use_gap=True))
    fig,axes=plt.subplots(1,2,figsize=(11.8,4.8))
    axes[0].plot(alphas,actual,label="actual fractional defect")
    axes[0].plot(alphas,holder,linestyle="--",label="gap-free Hölder certificate")
    axes[0].plot(alphas,gap,linestyle=":",label="spectral-gap certificate")
    axes[0].set_xlabel(r"fractional exponent $\alpha$")
    axes[0].set_ylabel("operator 2-norm")
    axes[0].set_title("Generator defects transfer to fractional powers")
    axes[0].grid(alpha=.25);axes[0].legend(fontsize=8.5)
    axes[1].plot(times,sem_actual,label="actual semigroup defect")
    axes[1].plot(times,sem_bound,linestyle="--",label="Duhamel certificate")
    axes[1].set_xlabel("time")
    axes[1].set_ylabel("operator 2-norm")
    axes[1].set_title(r"Fractional semigroup refinement, $\alpha=0.58$")
    axes[1].grid(alpha=.25);axes[1].legend(fontsize=9)
    fig.tight_layout();_save(fig,out,"19_fractional_naturality");stems.append("19_fractional_naturality")

    return stems
