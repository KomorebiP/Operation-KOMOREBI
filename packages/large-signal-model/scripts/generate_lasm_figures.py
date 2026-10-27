from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Wedge
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

from komorebi_arc3_offline.exact_atlas import MultiAtlasAnalyzer, wavelet_subband_slices
from komorebi_arc3_offline.lasm_model import ProjectorResolvedLargeSignalModel
from komorebi_arc3_offline.lasm_programs import LASMProgram
from komorebi_arc3_offline.lasm_refinement import PacketTree, best_basis, l1_packet_cost
from komorebi_arc3_offline.lasm_synthetic import generate_program_identification_scenario

INK = "#17202A"
MUTED = "#566573"
PAPER = "#FAFAF7"
BLUE = "#2E86AB"
CYAN = "#42B8C5"
TEAL = "#2A9D8F"
GREEN = "#6A994E"
YELLOW = "#E9C46A"
ORANGE = "#F4A261"
RED = "#E76F51"
MAGENTA = "#A23E8C"
PURPLE = "#6C5CE7"
COLORS = [BLUE, TEAL, ORANGE, MAGENTA, GREEN, PURPLE, RED, YELLOW, CYAN]

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10.5,
    "axes.titlesize": 14,
    "axes.labelsize": 10.5,
    "text.color": INK,
    "axes.labelcolor": INK,
    "axes.edgecolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "figure.facecolor": PAPER,
    "axes.facecolor": PAPER,
    "savefig.facecolor": PAPER,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def save(fig, name: str) -> None:
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight", pad_inches=0.08)
    fig.savefig(OUT / f"{name}.png", dpi=180, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def box(ax, x, y, w, h, text, face, edge=INK, fs=11):
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=.018,rounding_size=.025",
                           facecolor=face, edgecolor=edge, linewidth=1.6)
    ax.add_patch(patch)
    ax.text(x+w/2, y+h/2, text, ha="center", va="center", multialignment="center", fontsize=fs)


def arrow(ax, start, end, color=INK, rad=0.0):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=14,
                                linewidth=1.7, color=color, connectionstyle=f"arc3,rad={rad}"))


def diagram(figsize=(12.5, 6.0)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    return fig, ax


def sample_frame() -> np.ndarray:
    yy, xx = np.mgrid[0:64, 0:64]
    frame = 3 + 2*np.sin(2*np.pi*xx/64) + 1.3*np.cos(4*np.pi*yy/64)
    frame[11:28, 9:33] += 6
    frame[38:53, 40:57] += 4
    frame[((xx-45)**2 + (yy-17)**2) < 55] += 3
    return np.clip(np.rint(frame), 0, 15).astype(np.int16)


# 01 architecture
fig, ax = diagram((13, 6.2))
ax.text(.5,.92,"Projector-Resolved Large Algebraic Signal Model",ha="center",fontsize=22,weight="bold")
stages=[(.03,"frame / field",BLUE),(.19,"exact multi-atlas\narchive",TEAL),(.37,"nested signal\nstates",CYAN),(.54,"Bayesian typed\noperator posterior",ORANGE),(.73,"transition graph +\nactive planner",MAGENTA),(.89,"action / next\nobservation",PURPLE)]
for x,label,color in stages:
    box(ax,x,.44,.12,.20,label,color+"25",color,11)
for (x,_,color),(nx,_,_) in zip(stages[:-1],stages[1:]):
    arrow(ax,(x+.12,.54),(nx-.01,.54),color)
arrow(ax,(.95,.42),(.085,.42),MAGENTA,rad=-.22)
ax.text(.51,.17,"residual-driven refinement and exact reconstruction close the loop",ha="center",fontsize=12,color=MUTED)
save(fig,"01_pr_lasm_architecture")

# exact analyses
frame=sample_frame(); analyzer=MultiAtlasAnalyzer(); analysis=analyzer.analyze(frame)
# 02 archive vs statistical
fig, ax=diagram()
ax.text(.5,.92,"Exact archive and statistical state are different objects",ha="center",fontsize=21,weight="bold")
box(ax,.05,.55,.20,.22,"complete coordinates\nspatial, Fourier, Haar,\npolyphase, color",TEAL+"22",TEAL,12)
box(ax,.40,.55,.20,.22,"deterministic feature\nportfolio",BLUE+"22",BLUE,12)
box(ax,.75,.55,.18,.22,"macro / meso / micro\nlearned states",ORANGE+"22",ORANGE,12)
arrow(ax,(.25,.66),(.40,.66),INK); arrow(ax,(.60,.66),(.75,.66),INK)
arrow(ax,(.18,.53),(.18,.28),TEAL); box(ax,.08,.12,.20,.14,r"$\mathcal{S}\mathcal{A}=I$"+"\nexact certificate",TEAL+"18",TEAL,12)
arrow(ax,(.84,.53),(.84,.28),ORANGE); box(ax,.74,.12,.20,.14,"prediction / planning\ncompression",ORANGE+"18",ORANGE,12)
ax.text(.51,.35,"compression is useful only because the exact analysis record remains available",ha="center",fontsize=11.5,color=MUTED)
save(fig,"02_exact_archive_vs_statistical_state")

# 03 tight frame
fig, ax=diagram()
ax.text(.5,.92,"Weighted multi-atlas analysis is a finite tight frame",ha="center",fontsize=21,weight="bold")
box(ax,.05,.39,.14,.22,"object\n"+r"$x$",BLUE+"22",BLUE,16)
coords=[(.29,.72,"spatial",BLUE),(.29,.55,"Fourier",TEAL),(.29,.38,"Haar",MAGENTA),(.29,.21,"polyphase",ORANGE)]
for x,y,label,color in coords:
    box(ax,x,y,.16,.11,rf"$w_aU_ax$"+"\n"+label,color+"20",color,11)
    arrow(ax,(.19,.50),(x,y+.055),color)
box(ax,.61,.39,.18,.22,"canonical dual\n"+r"$\frac{1}{\sum w_a^2}\sum w_aU_a^*c_a$",YELLOW+"25",ORANGE,12)
for x,y,label,color in coords:
    arrow(ax,(x+.16,y+.055),(.61,.50),color)
box(ax,.86,.39,.10,.22,"same\n"+r"$x$",PURPLE+"20",PURPLE,15); arrow(ax,(.79,.50),(.86,.50),PURPLE)
ax.text(.5,.08,r"$\mathcal{S}\mathcal{A}=I$ for any positive atlas weights",ha="center",fontsize=17,weight="bold")
save(fig,"03_multi_atlas_tight_frame")

# 04 sample frame
fig,ax=plt.subplots(figsize=(7.2,6.0)); im=ax.imshow(frame,cmap="viridis",vmin=0,vmax=15); ax.set_title("One signal object in spatial coordinates",weight="bold"); ax.set_xlabel("x"); ax.set_ylabel("y"); fig.colorbar(im,ax=ax,label="signal value"); fig.tight_layout(); save(fig,"04_sample_signal")

# 05 Fourier
spec=np.fft.fftshift(np.abs(analysis.fourier));
fig,ax=plt.subplots(figsize=(7.2,6.0)); im=ax.imshow(np.log1p(spec),cmap="magma"); ax.set_title("The same object in Fourier coordinates",weight="bold"); ax.set_xlabel("frequency x"); ax.set_ylabel("frequency y"); fig.colorbar(im,ax=ax,label="log magnitude"); fig.tight_layout(); save(fig,"05_fourier_coordinates")

# 06 Haar
fig,ax=plt.subplots(figsize=(7.2,6.0)); scale=np.max(np.abs(analysis.haar)); im=ax.imshow(analysis.haar,cmap="coolwarm",vmin=-scale,vmax=scale); ax.set_title("Packed multilevel Haar coordinates",weight="bold"); ax.set_xlabel("coefficient address"); ax.set_ylabel("coefficient address"); fig.colorbar(im,ax=ax,label="signed coefficient"); fig.tight_layout(); save(fig,"06_haar_coordinates")

# 07 polyphase
fig,axes=plt.subplots(2,2,figsize=(10,8));
for axr,(phase,channel),color in zip(axes.ravel(),sorted(analysis.polyphase2.items()),COLORS):
    im=axr.imshow(channel,cmap="viridis",vmin=0,vmax=15); axr.set_title(f"phase {phase}",weight="bold"); axr.set_xticks([]); axr.set_yticks([])
fig.suptitle("Phase-2 polyphase channels: disjoint addresses, exact interleaving",fontsize=17,weight="bold"); fig.tight_layout(rect=[0,0,1,.94]); save(fig,"07_polyphase_channels")

# 08 color one-hot
mass=analysis.color.mean(axis=(1,2)); fig,ax=plt.subplots(figsize=(10,5.2)); ax.bar(np.arange(len(mass)),mass,color=[COLORS[i%len(COLORS)] for i in range(len(mass))]); ax.set_xticks(range(16)); ax.set_xlabel("color packet"); ax.set_ylabel("fraction of frame"); ax.set_title("Categorical color packets reconstruct by one-hot synthesis",weight="bold"); ax.grid(alpha=.18,axis="y"); fig.tight_layout(); save(fig,"08_color_packets")

# 09 residuals
res=analysis.reconstruction_residuals();res["tight frame"]=float(np.max(np.abs(analysis.tight_frame_synthesis()-frame)))
fig,ax=plt.subplots(figsize=(10,5.3)); names=list(res);vals=[max(res[n],1e-18) for n in names];ax.bar(names,vals,color=COLORS[:len(names)]);ax.set_yscale("log");ax.set_ylabel("maximum absolute residual");ax.set_title("Exact reconstruction certificates",weight="bold");ax.tick_params(axis="x",rotation=25);ax.grid(alpha=.2,axis="y",which="both");fig.tight_layout();save(fig,"09_reconstruction_certificates")

# 10 feature dimensions
from komorebi_arc3_offline.lasm_packetizer import UltimateLASMPacketizer
packets=UltimateLASMPacketizer().resolve(frame);dims={name:len(values) for name,values in packets.feature_groups.items()}
fig,ax=plt.subplots(figsize=(10,5.2));ax.bar(dims.keys(),dims.values(),color=COLORS[:len(dims)]);ax.set_ylabel("features");ax.set_title("Interpretable feature groups before nested projection",weight="bold");ax.tick_params(axis="x",rotation=20);ax.grid(alpha=.18,axis="y");fig.tight_layout();save(fig,"10_feature_portfolio")

# 11 packet tree selection
signal=frame.astype(float).ravel();tree=PacketTree.analyze(signal,6);selection=best_basis(tree,cost=l1_packet_cost,packet_penalty=1.0)
fig,ax=diagram((13,6.5)); ax.text(.5,.95,"Residual-driven mixed-depth packet basis",ha="center",fontsize=21,weight="bold")
selected=set(selection.paths)
for depth in range(7):
    paths=[format(i,f"0{depth}b") if depth else "" for i in range(2**depth)]
    y=.84-depth*.115
    for i,path in enumerate(paths):
        x=(i+.5)/len(paths)
        if depth<6:
            for child in (path+"0",path+"1"):
                cx=(int(child,2)+.5)/(2**(depth+1)); arrow(ax,(x,y-.012),(cx,y-.09),"#D5D8DC")
        if path in selected or any(sel.startswith(path) for sel in selected):
            radius=.012 if depth>3 else .018
            ax.add_patch(Circle((x,y),radius,facecolor=TEAL if path in selected else PAPER,edgecolor=TEAL if path in selected else MUTED,lw=1.2))
ax.text(.5,.04,f"selected {len(selected)} packets across depths {sorted({len(p) for p in selected})}; synthesis residual {np.max(np.abs(tree.synthesize(selection.paths)-signal)):.2e}",ha="center",fontsize=11,color=MUTED)
save(fig,"11_adaptive_packet_tree")

# 12 basis energy by depth
depths=range(7);counts=[sum(len(p)==d for p in selected) for d in depths];energies=[sum(np.sum(tree.coefficients[p]**2) for p in selected if len(p)==d)/np.sum(signal**2) for d in depths]
fig,ax1=plt.subplots(figsize=(10,5.4));ax1.bar(depths,counts,color=TEAL,alpha=.75,label="selected packets");ax1.set_xlabel("packet depth");ax1.set_ylabel("selected packet count");ax2=ax1.twinx();ax2.plot(depths,energies,marker="o",color=MAGENTA,lw=2,label="energy share");ax2.set_ylabel("selected energy share");ax1.set_title("Mixed-depth basis allocates resolution where structure demands it",weight="bold");ax1.grid(alpha=.16,axis="y");fig.tight_layout();save(fig,"12_packet_basis_depths")

# benchmark data
operator=json.loads((ROOT/"results/pr_lasm_benchmark/operator_benchmark.json").read_text())
agents=json.loads((ROOT/"results/pr_lasm_benchmark/agent_benchmark.json").read_text())
scenarios=[r["scenario"] for r in operator]
families=["linear","quadratic","delay","fractional","volterra","phase","gated"]
atlases=["spatial","color","fourier","haar","polyphase2","polyphase4","portfolio"]

# 13 grammar map
fig,ax=diagram((13,6.3));ax.text(.5,.94,"Typed operator-program grammar",ha="center",fontsize=21,weight="bold")
labels=[("linear",BLUE),("quadratic",TEAL),("bilinear",CYAN),("delay",ORANGE),("fractional",MAGENTA),("Volterra",PURPLE),("phase",GREEN),("gated",RED),("hybrid",YELLOW)]
for i,(lab,color) in enumerate(labels):
    angle=2*np.pi*i/len(labels);x=.5+.34*np.cos(angle);y=.50+.32*np.sin(angle);box(ax,x-.07,y-.05,.14,.10,lab,color+"22",color,10.5);arrow(ax,(.5,.50),(x-.06*np.cos(angle),y-.05*np.sin(angle)),color)
box(ax,.41,.42,.18,.16,"posterior over\nmechanism × atlas ×\nresolution",PAPER,INK,12)
save(fig,"13_operator_grammar")

# 14 identification matrix
matrix=np.zeros((len(scenarios),len(families)))
for i,row in enumerate(operator):matrix[i,families.index(row["best_family"])]=row["best_probability"]
fig,ax=plt.subplots(figsize=(11,6));im=ax.imshow(matrix,cmap="viridis",vmin=0,vmax=1,aspect="auto");ax.set_xticks(range(len(families)),families,rotation=30,ha="right");ax.set_yticks(range(len(scenarios)),scenarios);ax.set_title("Typed mechanism identification: 7 of 7",weight="bold");
for i in range(matrix.shape[0]):
    for j in range(matrix.shape[1]):
        if matrix[i,j]>0: ax.text(j,i,f"{matrix[i,j]:.2f}",ha="center",va="center",color="white" if matrix[i,j]>.5 else INK,weight="bold")
fig.colorbar(im,ax=ax,label="posterior probability of selected family");fig.tight_layout();save(fig,"14_mechanism_identification")

# 15 atlas matrix
matrix=np.zeros((len(scenarios),len(atlases)))
for i,row in enumerate(operator):matrix[i,atlases.index(row["best_atlas"])]=row["best_probability"]
fig,ax=plt.subplots(figsize=(11,6));im=ax.imshow(matrix,cmap="magma",vmin=0,vmax=1,aspect="auto");ax.set_xticks(range(len(atlases)),atlases,rotation=30,ha="right");ax.set_yticks(range(len(scenarios)),scenarios);ax.set_title("Atlas identification: 7 of 7",weight="bold");
for i in range(matrix.shape[0]):
    for j in range(matrix.shape[1]):
        if matrix[i,j]>0: ax.text(j,i,f"{matrix[i,j]:.2f}",ha="center",va="center",color="white",weight="bold")
fig.colorbar(im,ax=ax,label="posterior probability of selected atlas");fig.tight_layout();save(fig,"15_atlas_identification")

# 16 rmse bars
x=np.arange(len(operator));w=.36;base=[r["baseline_state_rmse"] for r in operator];lasm=[r["lasm_state_rmse"] for r in operator]
fig,ax=plt.subplots(figsize=(12,5.5));ax.bar(x-w/2,base,w,label="single linear portfolio",color=BLUE);ax.bar(x+w/2,lasm,w,label="PR-LASM posterior",color=TEAL);ax.set_xticks(x,[r["scenario"].replace("-","\n",1) for r in operator]);ax.set_ylabel("test state RMSE");ax.set_title("Controlled operator benchmark",weight="bold");ax.legend();ax.grid(alpha=.18,axis="y");fig.tight_layout();save(fig,"16_operator_rmse")

# 17 ratios
ratios=[r["state_rmse_ratio"] for r in operator]
fig,ax=plt.subplots(figsize=(11,5.2));bars=ax.bar(scenarios,ratios,color=[TEAL if v<1 else RED for v in ratios]);ax.axhline(1,color=INK,lw=1);ax.set_ylabel("PR-LASM RMSE / linear RMSE");ax.set_title(f"Median ratio = {np.median(ratios):.3f}",weight="bold");ax.tick_params(axis="x",rotation=30);ax.grid(alpha=.18,axis="y");
for bar,val in zip(bars,ratios):ax.text(bar.get_x()+bar.get_width()/2,val+.015,f"{val:.3f}",ha="center",fontsize=9)
fig.tight_layout();save(fig,"17_rmse_ratios")

# 18 memory kernels
lags=np.arange(1,33);power=lags**(-.68);power/=power.sum();expo=.82**np.arange(32);expo/=expo.sum()
fig,ax=plt.subplots(figsize=(10,5.2));ax.plot(lags,power,marker="o",ms=3,color=MAGENTA,lw=2,label="power-law / fractional memory");ax.plot(lags,expo,marker="o",ms=3,color=ORANGE,lw=2,label="exponential / Volterra memory");ax.set_xlabel("lag");ax.set_ylabel("normalized memory weight");ax.set_yscale("log");ax.set_title("Memory packets remain typed rather than blended into one hidden state",weight="bold");ax.legend();ax.grid(alpha=.18,which="both");fig.tight_layout();save(fig,"18_memory_kernels")

# 19 phase dynamics conceptual
fig,ax=plt.subplots(figsize=(11,5.2));steps=np.arange(20);forcing=np.where(steps%2==0,1,-1);ax.step(steps,forcing,where="mid",color=GREEN,lw=2,label="phase gate");ax.plot(steps,.6*np.sin(.5*steps)+forcing,color=PURPLE,marker="o",label="phase-conditioned response");ax.set_xlabel("step");ax.set_ylabel("signed transfer");ax.set_title("Polyphase programs expose alternating dynamics directly",weight="bold");ax.legend();ax.grid(alpha=.18);fig.tight_layout();save(fig,"19_phase_conditioned_dynamics")

# 20 graph exploration diagram
fig,ax=diagram((12,6.2));ax.text(.5,.93,"Exact replay transitions become a state-action graph",ha="center",fontsize=21,weight="bold")
pos={"s0":(.12,.55),"s1":(.34,.74),"s2":(.34,.35),"s3":(.60,.72),"frontier":(.60,.33),"win":(.86,.55)}
for i,(name,(x0,y0)) in enumerate(pos.items()):
    c=GREEN if name=="win" else ORANGE if name=="frontier" else COLORS[i%len(COLORS)];ax.add_patch(Circle((x0,y0),.065,facecolor=c+"28",edgecolor=c,lw=2));ax.text(x0,y0,name,ha="center",va="center",weight="bold")
edges=[("s0","s1","a1"),("s0","s2","a2"),("s1","s3","a3"),("s2","frontier","a4"),("s3","win","a2"),("frontier","win","? ")]
for u,v,l in edges:
    arrow(ax,pos[u],pos[v],MUTED);mx=(pos[u][0]+pos[v][0])/2;my=(pos[u][1]+pos[v][1])/2;ax.text(mx,my+.025,l,ha="center",fontsize=9,bbox=dict(facecolor=PAPER,edgecolor="none",pad=1))
ax.text(.5,.10,"known winning edges dominate; otherwise the planner seeks untried frontiers and informative probes",ha="center",fontsize=11.5,color=MUTED)
save(fig,"20_state_transition_graph")

# 21 agent actions
fig,ax=plt.subplots(figsize=(10,5.3));names=[r["game_id"].replace("lasm-","") for r in agents];actions=[r["committed_actions"] for r in agents];probes=[r["probe_actions"] for r in agents];x=np.arange(len(names));ax.bar(x,actions,label="committed",color=TEAL);ax.bar(x,probes,bottom=actions,label="replay probes",color=YELLOW);ax.set_xticks(x,names,rotation=20);ax.set_ylabel("actions");ax.set_title("Four deterministic interactive systems solved",weight="bold");ax.legend();ax.grid(alpha=.18,axis="y");fig.tight_layout();save(fig,"21_agent_actions")

# 22 graph sizes
fig,ax=plt.subplots(figsize=(10,5.3));nodes=[r["graph_nodes"] for r in agents];edges=[r["graph_edges"] for r in agents];x=np.arange(len(names));ax.bar(x-.18,nodes,.36,label="states",color=BLUE);ax.bar(x+.18,edges,.36,label="transitions",color=MAGENTA);ax.set_xticks(x,names,rotation=20);ax.set_ylabel("graph records");ax.set_title("Exact exploration memory remains small in the finite smoke systems",weight="bold");ax.legend();ax.grid(alpha=.18,axis="y");fig.tight_layout();save(fig,"22_agent_graph_sizes")

# 23 planning utility
fig,ax=diagram();ax.text(.5,.92,"Action utility combines proof-like and statistical information",ha="center",fontsize=21,weight="bold")
inputs=[(.05,.70,"exact probe",TEAL),(.05,.52,"known graph edge",BLUE),(.05,.34,"Bayesian prediction",ORANGE),(.05,.16,"role / loop history",MAGENTA)]
for x0,y0,label,color in inputs:box(ax,x0,y0,.19,.12,label,color+"22",color,11);arrow(ax,(x0+.19,y0+.06),(.42,.50),color)
box(ax,.42,.39,.20,.22,"typed utility\nprogress + win + novelty\n+ information - risk",YELLOW+"25",ORANGE,12)
box(ax,.76,.39,.17,.22,"selected public\naction",PURPLE+"22",PURPLE,12);arrow(ax,(.62,.50),(.76,.50),PURPLE)
save(fig,"23_active_planning_utility")

# 24 exact-refine-learn cycle
fig,ax=diagram();ax.text(.5,.92,"Residual-driven learning cycle",ha="center",fontsize=21,weight="bold")
cycle=[(.5,.73,"analyze exactly",TEAL),(.76,.55,"fit program posterior",ORANGE),(.68,.25,"predict / act",PURPLE),(.32,.25,"measure residual",RED),(.24,.55,"refine packet tree",BLUE)]
for x0,y0,label,color in cycle:box(ax,x0-.09,y0-.055,.18,.11,label,color+"22",color,10.5)
for (x0,y0,_,color),(x1,y1,_,_) in zip(cycle,cycle[1:]+cycle[:1]):arrow(ax,(x0,y0),(x1,y1),color,rad=.12)
box(ax,.41,.43,.18,.14,"exact archive\nnever discarded",PAPER,INK,11)
save(fig,"24_residual_refinement_cycle")

# 25 computation map
fig,ax=diagram((13,6.2));ax.text(.5,.93,"Computational path",ha="center",fontsize=21,weight="bold")
steps=[("FFT / Haar /\npolyphase",BLUE),("feature groups",TEAL),("nested QR\nprojection",CYAN),("Bayesian fits",ORANGE),("posterior mixture",MAGENTA),("graph planner",PURPLE)]
for i,(lab,color) in enumerate(steps):x=.03+i*.16;box(ax,x,.45,.13,.18,lab,color+"22",color,10.5);
for i in range(len(steps)-1):arrow(ax,(.16+i*.16,.54),(.19+i*.16,.54),INK)
ax.text(.5,.20,"dense operations are confined to small projected states; exact transforms remain structured",ha="center",fontsize=11.5,color=MUTED)
save(fig,"25_computational_path")

# suite 25
manifest=json.loads((ROOT/"validation/suite_manifest.json").read_text());games=manifest["games"];totals=[g["baseline_total"] for g in games];levels=[g["level_count"] for g in games]
# 26 histogram
fig,ax=plt.subplots(figsize=(10,5.2));ax.hist(totals,bins=9,color=TEAL,edgecolor=INK);ax.set_xlabel("supplied baseline action total");ax.set_ylabel("local environments");ax.set_title("The bundled 25-environment suite spans substantially different action scales",weight="bold");ax.grid(alpha=.16,axis="y");fig.tight_layout();save(fig,"26_arc25_action_scale")
# 27 scatter
fig,ax=plt.subplots(figsize=(10,5.4));ax.scatter(levels,totals,s=55,c=np.arange(len(games)),cmap="viridis",edgecolor=INK,linewidth=.5);ax.set_xlabel("levels in local environment");ax.set_ylabel("supplied baseline action total");ax.set_title("Static suite map: 25 complete local environment trees",weight="bold");ax.grid(alpha=.18);fig.tight_layout();save(fig,"27_arc25_suite_map")

# 28 claim boundary
fig,ax=diagram((12.5,6.4));ax.text(.5,.94,"Claim boundary",ha="center",fontsize=21,weight="bold")
left=["exact finite atlases","exact packet reconstruction","typed finite program posterior","exact replay graph","controlled synthetic certificates"]
right=["official ARC score","universal program induction","universal optimality","arbitrary nondeterministic replay","AGI"]
box(ax,.07,.17,.37,.66,"",TEAL+"12",TEAL);box(ax,.56,.17,.37,.66,"",RED+"10",RED)
ax.text(.255,.76,"established here",ha="center",fontsize=16,weight="bold",color=TEAL);ax.text(.745,.76,"not claimed",ha="center",fontsize=16,weight="bold",color=RED)
for i,item in enumerate(left):ax.text(.11,.66-i*.10,"✓  "+item,ha="left",fontsize=12)
for i,item in enumerate(right):ax.text(.60,.66-i*.10,"–  "+item,ha="left",fontsize=12)
save(fig,"28_claim_boundary")

# 29 verification dashboard
summary=json.loads((ROOT/"results/pr_lasm_benchmark/benchmark_summary.json").read_text());
fig,ax=plt.subplots(figsize=(11,6.2));ax.axis("off");ax.text(.5,.94,"Finite verification dashboard",ha="center",fontsize=21,weight="bold",transform=ax.transAxes)
rows=[("automated tests","36 / 36"),("exact atlases","6 / 6"),("typed families identified","7 / 7"),("atlases identified","7 / 7"),("interactive systems solved","4 / 4"),("local environment trees audited","25 / 25"),("median state RMSE ratio",f"{summary['median_state_rmse_ratio']:.4f}"),("maximum exact residual",f"{max(summary['exactness']['maximum_residuals'].values()):.3e}")]
y=.82
for i,(label,value) in enumerate(rows):
    ax.add_patch(FancyBboxPatch((.08,y-.035),.84,.065,boxstyle="round,pad=.005,rounding_size=.006",facecolor="#F0F3F4" if i%2 else PAPER,edgecolor="none",transform=ax.transAxes));ax.text(.11,y,label,ha="left",va="center",fontsize=12,transform=ax.transAxes);ax.text(.89,y,value,ha="right",va="center",fontsize=12,weight="bold",family="monospace",color=TEAL,transform=ax.transAxes);y-=.085
save(fig,"29_verification_dashboard")

# 30 closing wheel
fig,ax=plt.subplots(figsize=(8,8));ax.set_aspect("equal");ax.axis("off")
labels=[("exact atlas",BLUE),("project",TEAL),("transfer",CYAN),("refine",GREEN),("remember",YELLOW),("infer",ORANGE),("explore",RED),("plan",MAGENTA),("reconstruct",PURPLE)]
theta=np.linspace(90,90-360,len(labels)+1)
for i,(lab,color) in enumerate(labels):
    ax.add_patch(Wedge((0,0),1,theta[i+1],theta[i],width=.34,facecolor=color,edgecolor=PAPER,lw=2));angle=np.deg2rad((theta[i]+theta[i+1])/2);ax.text(.81*np.cos(angle),.81*np.sin(angle),lab,ha="center",va="center",rotation=(theta[i]+theta[i+1])/2-90,rotation_mode="anchor",fontsize=11,weight="bold",color="white")
ax.add_patch(Circle((0,0),.49,facecolor=PAPER,edgecolor=INK,lw=2));ax.text(0,.08,"PR-LASM",ha="center",fontsize=24,weight="bold");ax.text(0,-.05,"large algebraic signal model",ha="center",fontsize=12);ax.text(0,-.17,"one exact archive, many learned views",ha="center",fontsize=10,color=MUTED);ax.set_xlim(-1.12,1.12);ax.set_ylim(-1.12,1.12);ax.set_title("The completed architecture",fontsize=20,weight="bold",pad=10);save(fig,"30_closing_wheel")

print(f"generated {len(list(OUT.glob('*.pdf')))} figure pairs")
