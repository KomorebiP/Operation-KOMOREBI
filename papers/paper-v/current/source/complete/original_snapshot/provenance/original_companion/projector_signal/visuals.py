from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .edges import (
    boundary_band,
    estimated_edge_reconstruct_1d,
    estimated_edge_reconstruct_2d,
    exact_edge_reconstruct_1d,
    exact_edge_reconstruct_2d,
    fft_lowpass_1d,
    fft_lowpass_2d,
)
from .experiments import make_disk_2d, make_multiedge_2d, make_signal_1d, sparse_haar_packet_reconstruction
from .filterbanks import haar_analyze, haar_packet_analyze
from .nonlinear import coefficient_packets, packet_product
from .polyphase import polyphase_analyze, polyphase_synthesize
from .smith import constant_reactance_arc, constant_resistance_circle, smith_sensitivity
from .adaptive import (
    all_haar_packet_nodes,
    best_pruning,
    enumerate_prunings,
    optimum_gap,
    packet_tree_costs,
    perturbation_envelope,
    pruning_cost,
    synthesize_pruning,
)


def _save(fig: plt.Figure, root: Path, stem: str) -> list[str]:
    root.mkdir(parents=True, exist_ok=True)
    files = []
    for ext in ("png", "pdf"):
        path = root / f"{stem}.{ext}"
        fig.savefig(path, dpi=220 if ext == "png" else None, bbox_inches="tight")
        files.append(str(path.name))
    plt.close(fig)
    return files


def make_figures(root: str | Path) -> list[str]:
    root = Path(root)
    figure_dir = root / "figures"
    generated: list[str] = []

    # 1. Exact polyphase decomposition.
    n = np.arange(48)
    signal = np.sin(0.23 * n) + 0.35 * np.cos(0.71 * n) + 0.08 * n / len(n)
    channels = polyphase_analyze(signal, 4)
    reconstructed = polyphase_synthesize(channels, 4, len(signal))
    fig, axes = plt.subplots(5, 1, figsize=(10.2, 9.0), sharex=False)
    axes[0].plot(n, signal, marker=".")
    axes[0].set_title("Signal generated from one shift orbit")
    for r, channel in enumerate(channels):
        axes[r + 1].stem(np.arange(len(channel)), channel, basefmt=" ")
        axes[r + 1].set_ylabel(f"phase {r}")
    axes[-1].set_xlabel("decimated index")
    fig.suptitle(f"Four-phase analysis and exact synthesis; residual {np.max(np.abs(reconstructed-signal)):.1e}")
    fig.tight_layout()
    generated += _save(fig, figure_dir, "01_polyphase_analysis")

    # 2. Polyphase filter transfer kernels.
    h = np.array([0.15, -0.20, 0.45, 0.80, 0.45, -0.20, 0.15])
    from .polyphase import polyphase_filter_kernels
    kernels = polyphase_filter_kernels(h, 4)
    matrix = np.zeros((4, 4))
    labels = [[""] * 4 for _ in range(4)]
    for k in range(4):
        for s in range(4):
            matrix[k, s] = sum(abs(c) for c in kernels[k][s].coefficients)
            labels[k][s] = ", ".join(f"{d}:{c.real:g}" for d, c in zip(kernels[k][s].delays, kernels[k][s].coefficients, strict=True)) or "0"
    fig, ax = plt.subplots(figsize=(8.0, 6.4))
    image = ax.imshow(matrix, aspect="equal")
    fig.colorbar(image, ax=ax, label="sum of absolute tap weights")
    ax.set_xticks(range(4), [f"input {s}" for s in range(4)])
    ax.set_yticks(range(4), [f"output {k}" for k in range(4)])
    for k in range(4):
        for s in range(4):
            ax.text(s, k, labels[k][s], ha="center", va="center", fontsize=7)
    ax.set_title("Exact four-phase FIR transfer matrix (delay:coefficient)")
    generated += _save(fig, figure_dir, "02_filter_transfer_matrix")

    # 3. Haar analysis and energy.
    case = make_signal_1d(1024)
    low, high = haar_analyze(case["signal"])
    fig, axes = plt.subplots(3, 1, figsize=(10.2, 7.4))
    axes[0].plot(case["t"], case["signal"])
    axes[0].set_title("Piecewise-smooth signal")
    axes[1].plot(low)
    axes[1].set_title("Haar low packet")
    axes[2].plot(high)
    axes[2].set_title("Haar edge/detail packet")
    axes[2].set_xlabel("decimated index")
    fig.tight_layout()
    generated += _save(fig, figure_dir, "03_haar_edge_packets")

    # 4. Wavelet packet energy tree.
    packets = haar_packet_analyze(case["signal"], 4)
    paths = sorted(packets)
    energies = [float(np.vdot(packets[p], packets[p]).real) for p in paths]
    fig, ax = plt.subplots(figsize=(11.0, 5.0))
    ax.bar(np.arange(len(paths)), energies)
    ax.set_xticks(np.arange(len(paths)), paths, rotation=45)
    ax.set_ylabel("packet energy")
    ax.set_xlabel("wavelet packet address")
    ax.set_title("Energy distribution across a depth-four Haar packet tree")
    generated += _save(fig, figure_dir, "04_wavelet_packet_energy")

    # 5. 1D ringing comparison.
    modes = 18
    global1 = fft_lowpass_1d(case["signal"], modes)
    known1 = exact_edge_reconstruct_1d(case["smooth"], case["edge"], modes)
    estimated1, mask1, _ = estimated_edge_reconstruct_1d(case["signal"], modes)
    fig, axes = plt.subplots(2, 1, figsize=(11.0, 7.2), sharex=True)
    axes[0].plot(case["t"], case["signal"], label="original")
    axes[0].plot(case["t"], global1, label="global Fourier truncation")
    axes[0].plot(case["t"], known1, label="known edge packet")
    axes[0].plot(case["t"], estimated1, label="estimated edge packet")
    axes[0].legend(ncol=2)
    axes[0].set_title("One-dimensional edge reconstruction")
    axes[1].plot(case["t"], np.abs(case["signal"] - global1), label="global error")
    axes[1].plot(case["t"], np.abs(case["signal"] - known1), label="known-packet error")
    axes[1].plot(case["t"], np.abs(case["signal"] - estimated1), label="estimated-packet error")
    axes[1].fill_between(case["t"], 0, mask1.astype(float) * axes[1].get_ylim()[1], alpha=0.12, label="estimated packet")
    axes[1].legend(ncol=2)
    axes[1].set_xlabel("coordinate")
    axes[1].set_ylabel("absolute error")
    fig.tight_layout()
    generated += _save(fig, figure_dir, "05_edge_reconstruction_1d")

    # 6. Error against cutoff.
    cutoffs = np.arange(4, 49, 2)
    global_errors, known_errors, estimated_errors = [], [], []
    for cutoff in cutoffs:
        global_errors.append(np.sqrt(np.mean((case["signal"] - fft_lowpass_1d(case["signal"], int(cutoff))) ** 2)))
        known = exact_edge_reconstruct_1d(case["smooth"], case["edge"], int(cutoff))
        estimated, _, _ = estimated_edge_reconstruct_1d(case["signal"], int(cutoff))
        known_errors.append(np.sqrt(np.mean((case["signal"] - known) ** 2)))
        estimated_errors.append(np.sqrt(np.mean((case["signal"] - estimated) ** 2)))
    fig, ax = plt.subplots(figsize=(8.8, 5.3))
    ax.semilogy(cutoffs, global_errors, marker="o", label="global Fourier")
    ax.semilogy(cutoffs, known_errors, marker="o", label="known edge packet")
    ax.semilogy(cutoffs, estimated_errors, marker="o", label="estimated edge packet")
    ax.set_xlabel("retained Fourier modes")
    ax.set_ylabel("RMSE")
    ax.set_title("Smooth-packet accuracy and edge-packet leakage")
    ax.legend()
    ax.grid(alpha=0.25)
    generated += _save(fig, figure_dir, "06_edge_error_vs_resolution")

    # 7. Two-dimensional known packet comparison.
    disk = make_disk_2d()
    global2 = fft_lowpass_2d(disk["image"], 16)
    known2 = exact_edge_reconstruct_2d(disk["smooth"], disk["edge"], 16)
    fig, axes = plt.subplots(2, 3, figsize=(13.0, 8.5))
    panels = [disk["image"], global2, np.abs(disk["image"] - global2), disk["image"], known2, np.abs(disk["image"] - known2)]
    titles = ["Original", "Global Fourier reconstruction", "Global error", "Original", "Known-packet reconstruction", "Known-packet error"]
    for ax, panel, title in zip(axes.ravel(), panels, titles, strict=True):
        im = ax.imshow(panel, origin="lower")
        ax.set_title(title)
        ax.set_xticks([]); ax.set_yticks([])
        fig.colorbar(im, ax=ax, fraction=0.046)
    fig.suptitle("Sharp disk plus smooth background: exact edge packet versus global truncation")
    fig.tight_layout()
    generated += _save(fig, figure_dir, "07_known_edge_packet_2d")

    # 8. Data-driven two-dimensional estimator.
    estimated2, estimated_mask, _ = estimated_edge_reconstruct_2d(disk["image"], 16)
    fig, axes = plt.subplots(2, 3, figsize=(13.0, 8.5))
    panels = [disk["image"], estimated_mask, estimated2, np.abs(disk["image"] - global2), np.abs(disk["image"] - estimated2), disk["mask"] ^ estimated_mask]
    titles = ["Observed image", "Estimated binary packet", "Estimated-packet reconstruction", "Global error", "Estimated-packet error", "Mask disagreement"]
    for ax, panel, title in zip(axes.ravel(), panels, titles, strict=True):
        im = ax.imshow(panel, origin="lower")
        ax.set_title(title); ax.set_xticks([]); ax.set_yticks([])
        fig.colorbar(im, ax=ax, fraction=0.046)
    fig.suptitle("Narrow data-driven case: positive-contrast two-class packet estimation")
    fig.tight_layout()
    generated += _save(fig, figure_dir, "08_estimated_edge_packet_2d")

    # 9. Multi-edge/corner stress test.
    multi = make_multiedge_2d()
    global_multi = fft_lowpass_2d(multi["image"], 18)
    known_multi = exact_edge_reconstruct_2d(multi["smooth"], multi["edge"], 18)
    fig, axes = plt.subplots(2, 3, figsize=(13.0, 8.5))
    panels = [multi["image"], global_multi, known_multi, multi["edge"], np.abs(multi["image"] - global_multi), np.abs(multi["image"] - known_multi)]
    titles = ["Original multiedge image", "Global Fourier", "Known packet", "Exact edge packet", "Global error", "Known-packet error"]
    for ax, panel, title in zip(axes.ravel(), panels, titles, strict=True):
        im = ax.imshow(panel, origin="lower"); ax.set_title(title); ax.set_xticks([]); ax.set_yticks([]); fig.colorbar(im, ax=ax, fraction=0.046)
    fig.suptitle("Corners, curved boundaries, and multiple amplitudes")
    fig.tight_layout()
    generated += _save(fig, figure_dir, "09_multiedge_stress_test")

    # 10. Sparse Fourier versus Haar packet approximation.
    centered = case["signal"] - np.mean(case["signal"])
    keeps = [16, 32, 64, 128, 256]
    wave_err, fourier_err = [], []
    for keep in keeps:
        wave, _ = sparse_haar_packet_reconstruction(centered, 5, keep)
        spectrum = np.fft.fft(centered); idx = np.argsort(np.abs(spectrum))[::-1]; truncated = np.zeros_like(spectrum); truncated[idx[:keep]] = spectrum[idx[:keep]]
        four = np.real(np.fft.ifft(truncated))
        wave_err.append(np.sqrt(np.mean((centered-wave)**2))); fourier_err.append(np.sqrt(np.mean((centered-four)**2)))
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.loglog(keeps, wave_err, marker="o", label="Haar packet")
    ax.loglog(keeps, fourier_err, marker="o", label="largest Fourier coefficients")
    ax.set_xlabel("retained coefficients"); ax.set_ylabel("RMSE"); ax.set_title("Sparse approximation of a piecewise-smooth signal"); ax.legend(); ax.grid(alpha=.25)
    generated += _save(fig, figure_dir, "10_sparse_wavelet_fourier")

    # 11. Smith chart.
    angle = np.linspace(0, 2*np.pi, 1600); boundary = np.exp(1j*angle)
    fig, ax = plt.subplots(figsize=(9.5, 9.5)); ax.plot(boundary.real,boundary.imag,linewidth=1.8)
    for r in (.2,.5,1,2,5):
        g=constant_resistance_circle(r);ax.plot(g.real,g.imag,linewidth=.8)
    for x in (.2,.5,1,2,5):
        for sign in (1,-1):
            g=constant_reactance_arc(sign*x);ax.plot(g.real,g.imag,linewidth=.7,linestyle="--")
    N=16
    for k in range(N):
        th=2*np.pi*k/N;ax.plot([0,np.cos(th)],[0,np.sin(th)],linestyle=":",linewidth=.6)
    for rho in (.2,.4,.6,.8):
        g=rho*np.exp(2j*np.pi*np.arange(N)/N);ax.scatter(g.real,g.imag,s=20)
    ax.set_aspect("equal");ax.set_xlim(-1.1,1.1);ax.set_ylim(-1.1,1.1);ax.set_xlabel(r"$\Re\Gamma$");ax.set_ylabel(r"$\Im\Gamma$");ax.set_title("Projector-resolved polyphase Smith chart");ax.grid(alpha=.15)
    generated += _save(fig, figure_dir, "11_polyphase_smith_chart")

    # 12. Nested Smith refinement.
    fig, ax = plt.subplots(figsize=(8.2,7.7));rho=.76;ax.plot(boundary.real,boundary.imag)
    for N,size in ((2,150),(4,110),(8,70),(16,38),(32,18)):
        g=rho*np.exp(2j*np.pi*np.arange(N)/N);ax.scatter(g.real,g.imag,s=size,label=f"N={N}")
    ax.set_aspect("equal");ax.set_xlabel(r"$\Re\Gamma$");ax.set_ylabel(r"$\Im\Gamma$");ax.set_title("Exact nested phase refinement on one mismatch circle");ax.legend(ncol=5,loc="lower center",bbox_to_anchor=(.5,-.12));ax.grid(alpha=.2)
    generated += _save(fig, figure_dir, "12_smith_nested_refinement")

    # 13. Smith sensitivity.
    grid=np.linspace(-.995,.995,500);u,v=np.meshgrid(grid,grid);g=u+1j*v;inside=np.abs(g)<.995;w=np.full_like(u,np.nan);w[inside]=np.log10(smith_sensitivity(g[inside],1e-5))
    fig,ax=plt.subplots(figsize=(8.6,7.5));im=ax.imshow(w,origin="lower",extent=[grid.min(),grid.max(),grid.min(),grid.max()]);ax.plot(boundary.real,boundary.imag);ax.set_aspect("equal");ax.set_title("Symmetric sensitivity near open and short circuit");ax.set_xlabel(r"$\Re\Gamma$");ax.set_ylabel(r"$\Im\Gamma$");fig.colorbar(im,ax=ax,label=r"$\log_{10} w_{\rm Smith}$")
    generated += _save(fig, figure_dir, "13_smith_sensitivity")

    # 14. Nonlinear residue coupling.
    rng=np.random.default_rng(31);a=rng.normal(size=18);b=rng.normal(size=15);N=5;ap=coefficient_packets(a,N);bp=coefficient_packets(b,N);coupling=np.zeros((N,N))
    for i in range(N):
        for j in range(N): coupling[i,j]=np.linalg.norm(np.convolve(ap[i],bp[j]))
    fig,ax=plt.subplots(figsize=(7.2,6));im=ax.imshow(coupling);fig.colorbar(im,ax=ax,label="interaction norm");ax.set_xticks(range(N));ax.set_yticks(range(N));ax.set_xlabel("second input phase");ax.set_ylabel("first input phase");ax.set_title("Nonlinear/product packet interactions add modulo N")
    for i in range(N):
        for j in range(N): ax.text(j,i,f"→{(i+j)%N}",ha="center",va="center",fontsize=8)
    generated += _save(fig, figure_dir, "14_nonlinear_phase_coupling")

    # 15. Boundary-localized error.
    band=boundary_band(disk["mask"],3);gerr=np.abs(disk["image"]-global2);kerr=np.abs(disk["image"]-known2)
    fig,axes=plt.subplots(1,3,figsize=(12.6,4.2));panels=[band,gerr*band,kerr*band];titles=["Boundary band","Global error in band","Known-packet error in band"]
    for ax,panel,title in zip(axes,panels,titles,strict=True): im=ax.imshow(panel,origin="lower");ax.set_title(title);ax.set_xticks([]);ax.set_yticks([]);fig.colorbar(im,ax=ax,fraction=.046)
    fig.tight_layout();generated += _save(fig,figure_dir,"15_boundary_leakage")

    # 16. Status matrix.
    labels=["polyphase reconstruction","FIR transfer","Haar perfect reconstruction","known-edge theorem","mask perturbation bound","finite adaptive packet-tree optimum","positive-contrast estimator","Smith Mobius action","nonlinear packet product","universal edge discovery","infinite-tree/asymptotic selector"]
    status=np.array([[1,0,0],[1,0,0],[1,0,0],[1,0,0],[1,0,0],[1,0,0],[0,1,0],[1,0,0],[1,0,0],[0,0,1],[0,0,1]],float)
    fig,ax=plt.subplots(figsize=(8.5,6.6));ax.imshow(status,aspect="auto");ax.set_xticks([0,1,2],["proved","numerical/limited","open boundary"]);ax.set_yticks(range(len(labels)),labels)
    for i in range(len(labels)):
        for j in range(3): ax.text(j,i,"yes" if status[i,j] else "",ha="center",va="center")
    ax.set_title("Claim boundary for Paper V after the finite adaptive-tree theorem")
    generated += _save(fig,figure_dir,"16_claim_status")

    # 17. Globally optimal mixed-depth packet pruning.
    ta=np.linspace(0.0,1.0,128,endpoint=False)
    adaptive_signal=np.sin(2*np.pi*5*ta)+0.35*np.sin(2*np.pi*17*ta)*(ta<0.5)+0.80*((ta>0.62)&(ta<0.78))
    depth=5
    adaptive_nodes=all_haar_packet_nodes(adaptive_signal,depth)
    adaptive_cost=packet_tree_costs(adaptive_nodes,depth,complexity_per_node=.002)
    optimum=best_pruning(adaptive_cost,depth)
    selected=set(optimum.nodes)
    fig,ax=plt.subplots(figsize=(12.4,6.5))
    positions={}
    for d in range(depth+1):
        for k in range(2**d):
            path=format(k,f"0{d}b") if d else ""
            xcoord=(k+0.5)/2**d
            ycoord=depth-d
            positions[path]=(xcoord,ycoord)
            if d<depth:
                for bit in ("0","1"):
                    child=path+bit
                    cx=(2*k+(0 if bit=="0" else 1)+0.5)/2**(d+1)
                    ax.plot([xcoord,cx],[ycoord,ycoord-1],color="0.82",lw=.8,zorder=1)
    for path,(xcoord,ycoord) in positions.items():
        if path in selected:
            ax.scatter([xcoord],[ycoord],s=460,marker="s",zorder=3)
            label="root" if path=="" else path
            ax.text(xcoord,ycoord,label,ha="center",va="center",fontsize=7.4,color="white",weight="bold",zorder=4)
        else:
            ax.scatter([xcoord],[ycoord],s=18,color="0.72",zorder=2)
    ax.set_xlim(-.02,1.02);ax.set_ylim(-.45,depth+.55);ax.axis("off")
    ax.set_title("Dynamic programming selects a globally optimal complete packet pruning",fontsize=16,weight="bold")
    rebuilt=synthesize_pruning(adaptive_nodes,optimum.nodes,depth)
    ax.text(.5,-.28,"selected packets: "+", ".join(optimum.nodes)+f"    |    exact synthesis residual {np.max(np.abs(rebuilt-adaptive_signal)):.2e}",ha="center",fontsize=10)
    generated += _save(fig,figure_dir,"17_adaptive_packet_tree")

    # 18. Optimality gap and deterministic stability certificate.
    all_costs=np.sort(np.array([pruning_cost(pruning,adaptive_cost) for pruning in enumerate_prunings(depth)]))
    gap=optimum_gap(adaptive_cost,depth)
    envelope=perturbation_envelope({path:1e-6 for path in adaptive_cost},depth)
    fig,axes=plt.subplots(1,2,figsize=(12.4,4.8))
    display=min(3000,len(all_costs))
    axes[0].plot(np.arange(display),all_costs[:display]-all_costs[0],lw=1.4)
    axes[0].axhline(gap,ls="--",lw=1.1,label=f"first gap = {gap:.3e}")
    axes[0].set_yscale("log");axes[0].set_xlabel("pruning rank");axes[0].set_ylabel("cost above optimum");axes[0].set_title("Finite global optimum among 458,330 prunings");axes[0].grid(alpha=.2);axes[0].legend()
    axes[1].bar([0,1],[gap,2*envelope])
    axes[1].set_xticks([0,1],["optimum gap","twice perturbation envelope"]);axes[1].set_ylabel("cost");axes[1].set_title("Gap criterion certifies selector stability")
    axes[1].text(.5,.92,"stable" if gap>2*envelope else "not certified",transform=axes[1].transAxes,ha="center",fontsize=15,weight="bold")
    fig.tight_layout();generated += _save(fig,figure_dir,"18_adaptive_tree_stability")

    return generated
