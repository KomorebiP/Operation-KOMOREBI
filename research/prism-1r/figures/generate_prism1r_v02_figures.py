from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

OUT = Path(__file__).resolve().parents[1] / "figures"
OUT.mkdir(parents=True, exist_ok=True)


def box(ax, x, y, w, h, text="", fs=9, lw=1.4, hatch=None):
    patch = Rectangle((x, y), w, h, fill=False, linewidth=lw, hatch=hatch)
    ax.add_patch(patch)
    if text:
        ax.text(x + w/2, y + h/2, text, ha="center", va="center",
                fontsize=fs, wrap=True)
    return patch


def arrow(ax, x1, y1, x2, y2, lw=1.1, rad=0):
    patch = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                            mutation_scale=10, linewidth=lw,
                            connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(patch)
    return patch


def save(fig, stem):
    fig.savefig(OUT / f"{stem}.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{stem}.svg", bbox_inches="tight")
    plt.close(fig)


def architecture_overview():
    fig, ax = plt.subplots(figsize=(17, 10.5))
    ax.set_xlim(0, 170); ax.set_ylim(0, 105); ax.axis("off")
    ax.text(85, 100, "PRISM-1R ARCHITECTURE BLUEPRINT",
            ha="center", va="center", fontsize=22, fontweight="bold")
    ax.text(85, 96.8,
            "Hierarchical implementation view: package -> compute chiplet -> packet streaming multiprocessor",
            ha="center", va="center", fontsize=10.5)

    box(ax, 3, 13, 49, 79, lw=2)
    ax.text(27.5, 89.3, "REFERENCE PACKAGE", ha="center", fontsize=13, fontweight="bold")
    chip_positions=[(7,69,"C0"),(29,69,"C1"),(7,49,"C2"),(29,49,"C3")]
    for x,y,c in chip_positions:
        box(ax,x,y,18,13,f"Compute Chiplet {c}\n16 PSMs | 4 quadrants\n8 transform | 4 solver",fs=8.2)
    box(ax,15,28,25,12,"I/O + Control Die\nRISC-V control | global scheduler\nPCIe / CXL | security | telemetry",fs=8.3)
    for i,x in enumerate([7,18,30,41]):
        box(ax,x,17,8,7,f"HBM4\n{i}",fs=8)
    for x,y,_ in chip_positions:
        arrow(ax,x+9,y,27.5,40.3,lw=0.8)
    for x in [11,22,34,45]:
        arrow(ax,x,24,27.5,28,lw=0.75)
    ax.text(27.5,43,"UCIe package fabric",ha="center",fontsize=8)
    ax.text(27.5,14.3,"4 x HBM4 | reference aggregate > 11.2 TB/s",ha="center",fontsize=7.7)

    box(ax,58,13,49,79,lw=2)
    ax.text(82.5,89.3,"ONE COMPUTE CHIPLET",ha="center",fontsize=13,fontweight="bold")
    ax.text(82.5,85.7,"Dual NoC: C0/C1 control + C2/C3 packet/reduction",ha="center",fontsize=8.5)
    quadrants=[(62,59,"Q0"),(84.5,59,"Q1"),(62,36,"Q2"),(84.5,36,"Q3")]
    for x,y,q in quadrants:
        box(ax,x,y,19,19,f"{q}\n4 PSMs\n4 MiB shared SRAM\n2 transform engines\n1 solver engine",fs=8.2)
    box(ax,68,18,25,10,"Exact arithmetic cluster\nmodular | CRT | wide certificate checks",fs=8.2)
    box(ax,96,18,7,10,"UCIe\nRouter",fs=8)
    for x,y,_ in quadrants:
        arrow(ax,x+9.5,y,80.5,28.2,lw=0.75)
    arrow(ax,93,23,96,23,lw=0.75)
    ax.text(82.5,30.2,"hierarchical certificate aggregation + cross-quadrant traffic",ha="center",fontsize=7.4)

    box(ax,113,13,54,79,lw=2)
    ax.text(140,89.3,"ONE PACKET STREAMING MULTIPROCESSOR",ha="center",fontsize=13,fontweight="bold")
    box(ax,117,79,20,7,"Packet front end\ncommand + descriptor fetch",fs=8.1)
    box(ax,143,79,20,7,"Dependency + generation\nscoreboard",fs=8.1)
    arrow(ax,137,82.5,143,82.5,lw=0.8)
    box(ax,117,68,20,7,"TRANSFORMATION PLANE\nrepresentation routing",fs=8.0,hatch="//")
    box(ax,143,68,20,7,"RESOLUTION PLANE\nsplit | coarsen | refine",fs=8.0,hatch="\\\\")
    arrow(ax,127,79,127,75.1,lw=0.8); arrow(ax,153,79,153,75.1,lw=0.8)
    arrow(ax,137.1,71.5,142.9,71.5,lw=0.8)
    ax.text(140,69.6,"generation-aware handoff",ha="center",fontsize=6.8)
    box(ax,117,55,46,9,"2 MiB PSM SCRATCHPAD | 16 x 128 KiB banks\nP packets | F factors/transforms | M metadata | R residual/certificate",fs=8.0)
    arrow(ax,127,68,127,64.1,lw=0.8); arrow(ax,153,68,153,64.1,lw=0.8)
    for i,x in enumerate([117,128.5,140,151.5]):
        box(ax,x,43,10,8,f"EG{i}\n16x16 MMA\n+ vector",fs=7.3)
        arrow(ax,x+5,55,x+5,51.1,lw=0.7)
    box(ax,117,31,13,7,"Projector /\npolyphase DMA",fs=7.2)
    box(ax,133.5,31,13,7,"Transform\nport",fs=7.2)
    box(ax,150,31,13,7,"Solver\nport",fs=7.2)
    arrow(ax,122,43,122,38.1,lw=0.7); arrow(ax,137,43,140,38.1,lw=0.7); arrow(ax,156.5,43,156.5,38.1,lw=0.7)
    box(ax,117,19,20,7,"Residual / certificate\naccumulator",fs=7.8)
    box(ax,143,19,20,7,"Commit / replay\ncontroller",fs=7.8)
    arrow(ax,137,22.5,143,22.5,lw=0.8); arrow(ax,123.5,31,123.5,26.1,lw=0.7)
    arrow(ax,163.5,22.5,164.8,70.8,lw=0.9,rad=-0.16); arrow(ax,164.8,70.8,163,71.5,lw=0.9)
    ax.text(165.2,47,"certificate failure -> local refine/replay",rotation=90,ha="center",va="center",fontsize=7.0)
    arrow(ax,52,66,58,66,lw=0.8); ax.text(55,67.4,"detail",ha="center",fontsize=7)
    arrow(ax,107,66,113,66,lw=0.8); ax.text(110,67.4,"detail",ha="center",fontsize=7)

    ax.text(85,8.2,"Execution rule: jointly choose representation, resolution, placement and precision",ha="center",fontsize=10,fontweight="bold")
    ax.text(85,5.2,"Commit rule: publish only after certificate acceptance and generation validation",ha="center",fontsize=9)
    ax.text(85,2.4,"Preserve structure | execute locally | refine only where evidence requires it",ha="center",fontsize=9)
    fig.tight_layout(pad=1.2)
    save(fig, "PRISM-1R_Python_Architecture_Blueprint")


def psm_microarchitecture():
    fig, ax = plt.subplots(figsize=(15, 9))
    ax.set_xlim(0, 150); ax.set_ylim(0, 90); ax.axis("off")
    ax.text(75, 86, "PRISM-1R PSM MICROARCHITECTURE", ha="center", fontsize=20, fontweight="bold")
    ax.text(75, 82.5, "Command, transformation, resolution, execution, certification and replay", ha="center", fontsize=10)
    box(ax, 5, 65, 22, 10, "Command Fetch\n256-bit PSC queue", 9)
    box(ax, 33, 65, 22, 10, "Decode + Validate\nABI / descriptor checks", 9)
    box(ax, 61, 65, 24, 10, "Dependency + Generation\nscoreboard", 9)
    box(ax, 91, 65, 23, 10, "Issue / Reservation\nresource allocation", 9)
    box(ax, 120, 65, 24, 10, "Completion Queue\nprovisional records", 9)
    for a,b in [(27,33),(55,61),(85,91),(114,120)]: arrow(ax,a,70,b,70)
    box(ax, 20, 48, 43, 10, "TRANSFORMATION PLANE\nrepresentation route | operator dispatch", 9, hatch="//")
    box(ax, 87, 48, 43, 10, "RESOLUTION PLANE\nsplit | coarsen | refine | invalidate", 9, hatch="\\\\")
    arrow(ax,73,65,42,58); arrow(ax,73,65,108,58)
    box(ax, 9, 30, 132, 12,
        "2 MiB PSM SCRATCHPAD - 16 x 128 KiB banks\nP packet banks | F factor/transform banks | M metadata banks | R residual/certificate banks",
        9.2)
    arrow(ax,42,48,42,42); arrow(ax,108,48,108,42)
    for i,x in enumerate([10,36,62,88]):
        box(ax,x,14,20,10,f"EG{i}\n16x16 MMA + vector",8.2); arrow(ax,x+10,30,x+10,24)
    box(ax,114,14,12,10,"XFORM\nport",7.8); box(ax,130,14,12,10,"SOLVER\nport",7.8)
    arrow(ax,120,30,120,24); arrow(ax,136,30,136,24)
    box(ax,20,2,38,7,"Residual / certificate accumulator",8.5)
    box(ax,92,2,38,7,"Commit / replay controller",8.5)
    for x in [20,46,72,98,120,136]: arrow(ax,x,14,39,9,0.65)
    arrow(ax,58,5.5,92,5.5); arrow(ax,111,9,111,48,0.9,rad=-0.23)
    ax.text(117,29,"fail -> local refine / replay",fontsize=7.7,rotation=90,ha="center",va="center")
    ax.text(75,-1.5,"Invariant: no provisional result becomes architecturally visible unless CERT_PASS and GEN_CURRENT both hold",ha="center",fontsize=9,fontweight="bold")
    save(fig, "02_psm_microarchitecture")


def chiplet_noc():
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    ax.text(50,96,"PRISM-1R CHIPLET LOCALITY + NoC BLUEPRINT",ha="center",fontsize=18,fontweight="bold")
    ax.text(50,92.5,"Four quadrants, 4x4 PSM mesh, protected control service and structured payload service",ha="center",fontsize=9.5)
    for q,(x,y) in enumerate([(8,53),(52,53),(8,12),(52,12)]):
        box(ax,x,y,40,34,lw=1.8); ax.text(x+3,y+31,f"Q{q}",fontsize=11,fontweight="bold")
        coords=[]
        for r in range(2):
            for c in range(2):
                px=x+7+c*17; py=y+8+r*14
                box(ax,px,py,11,8,f"PSM\n{q*4+r*2+c}",7.5); coords.append((px+5.5,py+4))
        for a,b in [(0,1),(2,3),(0,2),(1,3)]:
            xa,ya=coords[a]; xb,yb=coords[b]; ax.plot([xa,xb],[ya,yb],linewidth=0.9)
        box(ax,x+7,y+2,18,4,"4 MiB shared SRAM",6.8)
        box(ax,x+27,y+2,10,4,"XFORM x2",6.5); box(ax,x+27,y+27,10,4,"SOLVER",6.5)
    box(ax,42,43,16,14,"Chiplet fabric\nC0/C1 control\nC2/C3 data/reduce",8)
    for x,y in [(48,70),(52,70),(48,29),(52,29),(28,53),(72,53)]: arrow(ax,50,50,x,y,lw=0.8)
    box(ax,42,3,16,8,"Exact arithmetic\ncluster",7.8); box(ax,68,3,18,8,"UCIe / HBM\nedge router",7.8)
    arrow(ax,50,43,50,11); arrow(ax,58,7,68,7)
    ax.text(50,89,"C0 = commit/fault (forward-progress guarantee) | C1 = metadata | C2 = payload | C3 = reduction",ha="center",fontsize=8.3)
    ax.text(50,0.2,"Placement objective: minimize hop-bytes subject to ownership, replication, certificate and replay constraints",ha="center",fontsize=8.5,fontweight="bold")
    save(fig, "03_chiplet_noc_locality")


def commit_state_machine():
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 140); ax.set_ylim(0, 70); ax.axis("off")
    ax.text(70,65,"PRISM-1R COMMAND / COMMIT STATE MACHINE",ha="center",fontsize=18,fontweight="bold")
    states=[(8,37,"QUEUED"),(28,37,"READY"),(48,37,"DISPATCHED"),(70,37,"PROVISIONAL"),(94,37,"CERTIFIED"),(118,37,"COMMITTED")]
    for x,y,s in states: box(ax,x,y,14,8,s,8.2)
    for (x1,_,_),(x2,_,_) in zip(states[:-1],states[1:]): arrow(ax,x1+14,41,x2,41)
    box(ax,65,13,19,8,"REFINE / REPLAY",8); box(ax,103,13,16,8,"ABORT",8)
    arrow(ax,77,37,75,21,rad=0.1); arrow(ax,84,17,54,37,rad=-0.18); arrow(ax,77,37,111,21,rad=-0.12)
    ax.text(64,28,"certificate fail,\ngeneration stale,\nprecision insufficient",fontsize=7.7,ha="center")
    ax.text(112,28,"fatal fault or\npolicy stop",fontsize=7.7,ha="center")
    ax.text(106,50,"CERT_PASS + GEN_CURRENT\n+ no uncorrectable fault",fontsize=8,ha="center")
    ax.text(70,4,"Critical safety property: COMMITTED is unreachable from PROVISIONAL unless all declared commit predicates hold",ha="center",fontsize=9,fontweight="bold")
    save(fig, "04_commit_refinement_state_machine")


def deployment_ladder():
    fig, ax = plt.subplots(figsize=(16, 7))
    ax.set_xlim(0, 160); ax.set_ylim(0, 70); ax.axis("off")
    ax.text(80,65,"PRISM-1R DEPLOYMENT LADDER",ha="center",fontsize=18,fontweight="bold")
    stages=[("0","Golden model","semantic truth"),("1","CUDA backend","representation baseline"),("2","Cycle simulator","physical bottlenecks"),("3","FPGA PSM","measured control + locality"),("4","Shuttle chiplet","same-representation advantage"),("5","Reference chiplet","timing / power / floorplan"),("6","Full package","system validation")]
    x=6
    for i,(n,name,goal) in enumerate(stages):
        w=19; box(ax,x,28,w,18,f"STAGE {n}\n{name}\n\n{goal}",8.1)
        if i < len(stages)-1:
            arrow(ax,x+w,37,x+w+3,37); ax.text(x+w+1.5,43,"gate",ha="center",fontsize=7)
        x += 22
    ax.text(80,17,"Advance only when the previous stage preserves the semantic contract and exposes a measured reason for specialization",ha="center",fontsize=9,fontweight="bold")
    ax.text(80,10,"STOP examples: semantic mismatch | no structured gain | C0 starvation | stale commit | NoC/SRAM cost erases advantage",ha="center",fontsize=8.5)
    save(fig, "05_deployment_ladder")


def command_envelope():
    fig, ax = plt.subplots(figsize=(16, 6))
    ax.set_xlim(0, 256); ax.set_ylim(0, 55); ax.axis("off")
    ax.text(128,50,"PROPOSED 256-BIT PACKET SEED COMMAND ENVELOPE",ha="center",fontsize=18,fontweight="bold")
    fields=[("opcode",8),("flags",8),("abi",8),("fmt",8),("packet_id",32),("src_desc",32),("dst_desc",32),("dep_token",24),("generation",24),("cert_id",24),("payload/imm",56)]
    cur=0
    for name,w in fields:
        box(ax,cur,24,w,13,f"{name}\n{w}b",7.3); ax.text(cur,20,str(cur),ha="center",fontsize=6.5); cur += w
    ax.text(256,20,"256",ha="right",fontsize=6.5)
    ax.text(128,11,"Candidate ABI layout: semantics should freeze before exact bit allocation. Fields may be re-packed after RTL/synthesis.",ha="center",fontsize=8.5)
    ax.text(128,5,"Envelope invariant: command carries enough identity to validate version, dependency, generation and certificate obligations before commit.",ha="center",fontsize=8.5,fontweight="bold")
    save(fig, "06_command_envelope")


if __name__ == "__main__":
    architecture_overview()
    psm_microarchitecture()
    chiplet_noc()
    commit_state_machine()
    deployment_ladder()
    command_envelope()
    print(f"Generated figures in {OUT}")
