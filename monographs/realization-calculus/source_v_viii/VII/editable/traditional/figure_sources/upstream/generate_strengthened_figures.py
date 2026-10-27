from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
matplotlib.rcParams['font.size'] = 10
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / 'figures'
FIG.mkdir(parents=True, exist_ok=True)


def save(fig, name: str) -> None:
    fig.savefig(FIG / name, bbox_inches='tight')
    plt.close(fig)


def architecture() -> None:
    labels = [
        'seed', 'symmetry\npackets', 'circuit\npaths', 'channels',
        'constraints', 'effective\ndynamics', 'Euclidean\ntransfer', 'continuum\ntower'
    ]
    fig, ax = plt.subplots(figsize=(10.5, 2.3))
    ax.set_xlim(0, len(labels))
    ax.set_ylim(0, 1)
    ax.axis('off')
    for i, label in enumerate(labels):
        box = FancyBboxPatch((i + 0.08, 0.30), 0.84, 0.40,
                             boxstyle='round,pad=0.025', fill=False, linewidth=1.1)
        ax.add_patch(box)
        ax.text(i + 0.50, 0.50, label, ha='center', va='center')
        if i + 1 < len(labels):
            ax.add_patch(FancyArrowPatch((i + 0.92, 0.50), (i + 1.08, 0.50),
                                         arrowstyle='->', mutation_scale=12, linewidth=1.0))
    ax.text(4.0, 0.08, 'finite exact layer', ha='center', va='center')
    ax.plot([0.1, 6.9], [0.18, 0.18], linewidth=0.8)
    ax.text(7.5, 0.08, 'limit criteria', ha='center', va='center')
    save(fig, '01_quantum_architecture.pdf')


def seed_rank() -> None:
    d = 4
    r = np.arange(1, 5)
    orbit = d * r
    fig, ax = plt.subplots(figsize=(6.6, 4.1))
    ax.plot(r, orbit, marker='o', linewidth=1.6)
    ax.set_xlabel('Schmidt rank')
    ax.set_ylabel('dimension of the local operator orbit')
    ax.set_xticks(r)
    ax.set_title(r'Local orbit dimension for $d_A=4$')
    ax.grid(True, linewidth=0.4, alpha=0.5)
    save(fig, '02_seed_rank.pdf')


def symmetry_packets() -> None:
    fig, ax = plt.subplots(figsize=(8.0, 3.7))
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-0.7, 3.2)
    ax.axis('off')
    for j in range(4):
        ax.add_patch(Circle((j, 2.3), 0.22, fill=False, linewidth=1.1))
        ax.text(j, 2.3, rf'$P_{j}$', ha='center', va='center')
        ax.text(j, 2.85, rf'charge ${j}$', ha='center')
    for j in range(4):
        k = (j + 1) % 4
        ax.add_patch(FancyArrowPatch((j, 2.05), (k, 1.10),
                                     connectionstyle='arc3,rad=0.12',
                                     arrowstyle='->', mutation_scale=12, linewidth=1.0))
        ax.text((j + k) / 2, 1.50 if j < 3 else 0.85, r'$A_{+1}$', ha='center')
    ax.text(1.5, 0.15,
            r'$S A_q S^*=\omega^q A_q$ forces $A_q P_j\subseteq P_{j+q}\mathcal{H}$',
            ha='center')
    save(fig, '03_symmetry_selection.pdf')


def circuit_paths() -> None:
    fig, ax = plt.subplots(figsize=(9.0, 4.0))
    ax.set_xlim(-0.3, 4.3)
    ax.set_ylim(-0.4, 3.4)
    ax.axis('off')
    levels = 5
    charges = 3
    xs = np.arange(levels)
    for x in xs:
        for q in range(charges):
            ax.add_patch(Circle((x, q), 0.10, fill=False, linewidth=1.0))
            ax.text(x, q + 0.20, rf'$P_{q}$', ha='center', fontsize=8)
    allowed = {
        0: [(0, 0), (0, 1), (1, 1), (1, 2), (2, 0)],
        1: [(0, 1), (1, 0), (1, 2), (2, 1)],
        2: [(0, 2), (1, 1), (2, 2), (2, 0)],
        3: [(0, 0), (0, 2), (1, 1), (2, 2)],
    }
    for x in range(levels - 1):
        for a, b in allowed[x]:
            ax.add_patch(FancyArrowPatch((x + 0.11, a), (x + 0.89, b),
                                         arrowstyle='->', mutation_scale=8,
                                         linewidth=0.8, alpha=0.75))
    ax.text(2, 3.05, 'packet paths through a four gate circuit', ha='center')
    ax.set_xlabel('circuit depth')
    save(fig, '04_circuit_paths.pdf')


def leakage() -> None:
    eps = 0.32
    H = np.array([[0.7, eps], [eps, -0.7]], dtype=complex)
    evals, evecs = np.linalg.eigh(H)
    t = np.linspace(0, 8, 500)
    leak = []
    for tt in t:
        U = evecs @ np.diag(np.exp(-1j * tt * evals)) @ evecs.conj().T
        leak.append(abs(U[1, 0]))
    bound = np.minimum(1.0, t * eps)
    fig, ax = plt.subplots(figsize=(7.2, 4.1))
    ax.plot(t, leak, label='exact leakage amplitude', linewidth=1.5)
    ax.plot(t, bound, linestyle=':', label='commutator bound', linewidth=1.4)
    ax.set_xlabel('time')
    ax.set_ylabel('off packet norm')
    ax.set_ylim(0, 1.05)
    ax.legend(frameon=False)
    ax.grid(True, linewidth=0.4, alpha=0.5)
    save(fig, '05_leakage_bound.pdf')


def kato_transport() -> None:
    theta = np.linspace(0.2, 1.1, 150)
    phi = 2.2 * theta
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    fig = plt.figure(figsize=(5.5, 5.0))
    ax = fig.add_subplot(111, projection='3d')
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 25)
    sx = np.outer(np.cos(u), np.sin(v))
    sy = np.outer(np.sin(u), np.sin(v))
    sz = np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(sx, sy, sz, rstride=4, cstride=4, linewidth=0.25, alpha=0.25)
    ax.plot(x, y, np.cos(theta), linewidth=1.8)
    ax.scatter([x[0], x[-1]], [y[0], y[-1]], [np.cos(theta[0]), np.cos(theta[-1])], s=25)
    ax.set_xlabel(r'$n_x$')
    ax.set_ylabel(r'$n_y$')
    ax.set_zlabel(r'$n_z$')
    ax.set_title('A moving rank one packet on the Bloch sphere')
    save(fig, '06_kato_transport.pdf')


def operator_packets() -> None:
    n = 8
    M = np.zeros((n, n))
    M[:3, :3] = 1.0
    M[:3, 3:6] = 0.55
    M[3:6, :3] = 0.35
    M[3:6, 3:6] = 0.9
    M[6:, 6:] = 0.75
    M[:6, 6:] = 0.2
    M[6:, :6] = 0.1
    fig, ax = plt.subplots(figsize=(5.0, 4.4))
    from matplotlib.patches import Rectangle
    for row in range(n):
        for col in range(n):
            shade = 1.0 - 0.85 * M[row, col]
            ax.add_patch(Rectangle((col - 0.5, row - 0.5), 1, 1,
                                   facecolor=(shade, shade, shade),
                                   edgecolor='none'))
    for cut in (2.5, 5.5):
        ax.axhline(cut, linewidth=1.0)
        ax.axvline(cut, linewidth=1.0)
    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(n - 0.5, -0.5)
    ax.set_aspect('equal')
    ax.set_title('Operator packets $P_a X P_b$')
    ax.set_xlabel('input packet coordinate')
    ax.set_ylabel('output packet coordinate')
    save(fig, '07_operator_packets.pdf')


def channel_coherence() -> None:
    gamma = 0.35
    rho = np.array([[0.35, 0.33], [0.33, 0.65]], dtype=float)
    k0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]])
    k1 = np.array([[0, np.sqrt(gamma)], [0, 0]])
    out = k0 @ rho @ k0.T + k1 @ rho @ k1.T
    vals = [abs(rho[0, 0]), abs(rho[1, 1]), abs(rho[0, 1]),
            abs(out[0, 0]), abs(out[1, 1]), abs(out[0, 1])]
    labels = [r'$\rho_{00}$', r'$\rho_{11}$', r'$|\rho_{01}|$',
              r'$\Phi(\rho)_{00}$', r'$\Phi(\rho)_{11}$', r'$|\Phi(\rho)_{01}|$']
    fig, ax = plt.subplots(figsize=(8.0, 4.0))
    ax.bar(np.arange(len(vals)), vals)
    ax.set_xticks(np.arange(len(vals)), labels, rotation=25, ha='right')
    ax.set_ylabel('magnitude')
    ax.set_title('Population and coherence transfer under amplitude damping')
    save(fig, '08_channel_coherence.pdf')


def qec_syndromes() -> None:
    labels = ['no error', 'flip 1', 'flip 2', 'flip 3']
    mat = np.eye(4)
    fig, ax = plt.subplots(figsize=(5.2, 4.5))
    from matplotlib.patches import Rectangle
    for row in range(4):
        for col in range(4):
            shade = 0.18 if row == col else 1.0
            ax.add_patch(Rectangle((col - 0.5, row - 0.5), 1, 1,
                                   facecolor=(shade, shade, shade),
                                   edgecolor=(0.75, 0.75, 0.75),
                                   linewidth=0.5))
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(3.5, -0.5)
    ax.set_aspect('equal')
    ax.set_xticks(range(4), labels, rotation=25, ha='right')
    ax.set_yticks(range(4), labels)
    ax.set_title('Orthogonal syndrome packets for the three qubit repetition code')
    for i in range(4):
        ax.text(i, i, r'$2$', ha='center', va='center', color='white')
    save(fig, '09_qec_syndromes.pdf')


def feshbach() -> None:
    H = np.array([
        [-1.0, 0.18, 0.25, 0.05],
        [0.18, -0.35, 0.12, 0.20],
        [0.25, 0.12, 0.9, 0.15],
        [0.05, 0.20, 0.15, 1.55],
    ])
    eig = np.linalg.eigvalsh(H)
    A = H[:2, :2]
    B = H[:2, 2:]
    D = H[2:, 2:]
    x = np.linspace(-1.5, 2.0, 1000)
    detf = np.full_like(x, np.nan)
    for i, z in enumerate(x):
        if np.min(np.abs(np.linalg.eigvalsh(D) - z)) > 0.015:
            F = z * np.eye(2) - A - B @ np.linalg.inv(z * np.eye(2) - D) @ B.T
            detf[i] = np.linalg.det(F)
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.plot(x, np.clip(detf, -4, 4), linewidth=1.2)
    ax.axhline(0, linewidth=0.8)
    for e in eig:
        ax.axvline(e, linestyle=':', linewidth=0.8)
    ax.set_ylim(-4, 4)
    ax.set_xlabel('spectral parameter')
    ax.set_ylabel('clipped determinant of the Feshbach map')
    ax.set_title('Zeros of the effective determinant recover the full spectrum')
    save(fig, '10_feshbach_spectrum.pdf')


def memory_kernel() -> None:
    D = np.diag([0.8, 1.7, 2.6])
    B = np.array([[0.5, 0.25, 0.2]])
    t = np.linspace(0, 14, 600)
    k = np.array([(B @ np.diag(np.exp(-1j * tt * np.diag(D))) @ B.T)[0, 0] for tt in t])
    fig, ax = plt.subplots(figsize=(7.4, 4.1))
    ax.plot(t, k.real, label='real part', linewidth=1.4)
    ax.plot(t, k.imag, linestyle=':', label='imaginary part', linewidth=1.4)
    ax.set_xlabel('time')
    ax.set_ylabel('memory kernel')
    ax.legend(frameon=False)
    ax.grid(True, linewidth=0.4, alpha=0.5)
    save(fig, '11_memory_kernel.pdf')


def reflection_positivity() -> None:
    vals = np.array([1.0, 0.72, 0.38])
    T = np.diag(vals)
    rng = np.random.default_rng(17)
    v = rng.normal(size=(5, 3))
    times = np.arange(5)
    G = np.empty((5, 5))
    for i in range(5):
        for j in range(5):
            G[i, j] = v[i] @ np.linalg.matrix_power(T, times[i] + times[j]) @ v[j]
    eig = np.linalg.eigvalsh(G)
    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    ax.bar(np.arange(1, 6), eig)
    ax.axhline(0, linewidth=0.8)
    ax.set_xlabel('Gram eigenvalue index')
    ax.set_ylabel('eigenvalue')
    ax.set_title('Finite transfer reflection positivity')
    save(fig, '12_reflection_positivity.pdf')


def spectral_dimension() -> None:
    def ds_grid(N: int, d: int, t: np.ndarray) -> np.ndarray:
        k1 = np.fft.fftfreq(N) * N
        lam1 = 4 * N * N * np.sin(np.pi * k1 / N) ** 2
        if d == 1:
            lam = lam1
        else:
            lam = (lam1[:, None] + lam1[None, :]).reshape(-1)
        out = []
        for tt in t:
            w = np.exp(-tt * lam)
            out.append(2 * tt * np.sum(lam * w) / np.sum(w))
        return np.array(out)

    t = np.logspace(-4, 0.2, 450)
    d1 = ds_grid(96, 1, t)
    d2 = ds_grid(48, 2, t)
    fig, ax = plt.subplots(figsize=(7.2, 4.3))
    ax.semilogx(t, d1, label='cycle')
    ax.semilogx(t, d2, label='two dimensional torus')
    ax.axhline(1, linestyle=':', linewidth=0.8)
    ax.axhline(2, linestyle=':', linewidth=0.8)
    ax.set_xlabel('diffusion time')
    ax.set_ylabel('spectral dimension')
    ax.set_ylim(0, 2.5)
    ax.legend(frameon=False)
    save(fig, '13_spectral_dimension.pdf')


def tower() -> None:
    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 5)
    ax.axis('off')
    widths = [2.0, 3.0, 4.2, 5.4]
    for i, width in enumerate(widths):
        x = 4 - width / 2
        y = 0.55 + i
        ax.add_patch(Rectangle((x, y), width, 0.58, fill=False, linewidth=1.0))
        ax.text(4, y + 0.29, rf'$\mathcal{{H}}_{i}$ with $H_{i},\ P_{{i,\alpha}},\ C_{{i,a}}$',
                ha='center', va='center')
        if i < 3:
            ax.add_patch(FancyArrowPatch((4, y + 0.58), (4, y + 1.0),
                                         arrowstyle='->', mutation_scale=12))
    ax.text(4, 4.72, 'refinement tower with declared compatibility defects', ha='center')
    save(fig, '14_continuum_tower.pdf')


def constraint_obstruction() -> None:
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    ax.set_xlim(0, 8.5)
    ax.set_ylim(0, 3.6)
    ax.axis('off')
    boxes = [
        (0.4, 1.5, 1.7, 0.7, r'$[C_a,C_b]$'),
        (3.0, 1.5, 2.0, 0.7, r'$\operatorname{End}(\mathcal{H})/\operatorname{span}\{C_c\}$'),
        (6.1, 1.5, 1.9, 0.7, 'closure\nobstruction')
    ]
    for x, y, w, h, text in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.03', fill=False))
        ax.text(x + w / 2, y + h / 2, text, ha='center', va='center')
    ax.add_patch(FancyArrowPatch((2.1, 1.85), (3.0, 1.85), arrowstyle='->', mutation_scale=12))
    ax.add_patch(FancyArrowPatch((5.0, 1.85), (6.1, 1.85), arrowstyle='->', mutation_scale=12))
    ax.text(4.25, 0.65,
            r'Compression to the physical kernel is not a closure test for self adjoint constraints.',
            ha='center')
    save(fig, '15_constraint_obstruction.pdf')


def boundary_ladder() -> None:
    labels = [
        'finite packet\nidentities',
        'compatible\nrefinement tower',
        'self adjoint\ncontinuum limit',
        'reflection positive\nEuclidean limit',
        'local Lorentzian\nfield theory',
        'Einstein infrared\ncriterion',
        'positive massless\nspin two sector'
    ]
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    ax.set_xlim(0, 7.5)
    ax.set_ylim(0, 5.2)
    ax.axis('off')
    for i, label in enumerate(labels):
        x = 0.35 + i * 1.0
        y = 0.35 + i * 0.60
        ax.add_patch(FancyBboxPatch((x, y), 1.35, 0.65,
                                    boxstyle='round,pad=0.025', fill=False, linewidth=1.0))
        ax.text(x + 0.675, y + 0.325, label, ha='center', va='center', fontsize=8.2)
        if i + 1 < len(labels):
            ax.add_patch(FancyArrowPatch((x + 1.35, y + 0.55),
                                         (x + 1.0, y + 0.75),
                                         arrowstyle='->', mutation_scale=10))
    ax.text(3.8, 4.95, 'Every step requires a separate theorem', ha='center')
    save(fig, '16_continuum_boundary.pdf')


if __name__ == '__main__':
    architecture()
    seed_rank()
    symmetry_packets()
    circuit_paths()
    leakage()
    kato_transport()
    operator_packets()
    channel_coherence()
    qec_syndromes()
    feshbach()
    memory_kernel()
    reflection_positivity()
    spectral_dimension()
    tower()
    constraint_obstruction()
    boundary_ladder()
    print(json.dumps({'figures': len(list(FIG.glob('*.pdf')))}, indent=2))
