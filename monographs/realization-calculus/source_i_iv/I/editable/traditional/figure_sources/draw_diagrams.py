"""Rebuild three exact schematic diagrams for the main paper.

These figures describe the mathematical structures in the adjacent prose.
The seed grammar is a presentation guide rather than an extra theorem.
The elliptic transfer uses the ordered packets (k[x], y k[x]). Its entries
are coefficient operators over k[x], so the odd to even weight is x^3-x.
The final map is a structural overview, not an exhaustive Lean dependency
graph. All positions are explicit so that fonts and connectors remain
inside the fixed PDF page box.
"""
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from common import canvas, save, INK, MUTED, TEAL, GOLD, LIGHT, GRID


def drawing(fig, height):
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 6.7)
    ax.set_ylim(0, height)
    ax.set_axis_off()
    return ax


def box(ax, x, y, width, height, title, detail=None, color=TEAL,
        face=LIGHT, fontsize=11):
    ax.add_patch(FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.025,rounding_size=0.06",
        facecolor=face, edgecolor=color, linewidth=1.2))
    if detail:
        ax.text(x+width/2, y+height*.66, title, ha="center", va="center",
                fontsize=fontsize, weight="bold", color=color)
        ax.text(x+width/2, y+height*.29, detail, ha="center", va="center",
                fontsize=10.2, color=INK)
    else:
        ax.text(x+width/2, y+height/2, title, ha="center", va="center",
                fontsize=fontsize, color=INK, linespacing=1.35)


def arrow(ax, start, end, color=TEAL, style="-", curve=0):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=12,
        connectionstyle=f"arc3,rad={curve}",
        color=color, linewidth=1.3, linestyle=style,
        shrinkA=3, shrinkB=3))


def grammar():
    h = 4.30
    fig = canvas("From seeds to a realization",
                 "A guide to the data used in a presentation.", height=h)
    ax = drawing(fig, h)
    xs = [.20, 2.48, 4.76]
    w, bh = 1.74, .68
    upper, lower = 2.75, 1.37
    upper_nodes = [
        ("Choose seeds", "generators in the object"),
        ("Address them", "indices for the seeds"),
        ("Apply operators", "words in the fixed algebra")]
    lower_nodes = [
        ("Reconstruct", "a realization map"),
        ("Form the hull", "span or closure"),
        ("Record relations", "kernel and quotient data")]
    for x, (title, detail) in zip(xs, upper_nodes):
        box(ax, x, upper, w, bh, title, detail, fontsize=11.2)
    for x, (title, detail) in zip(xs, lower_nodes):
        box(ax, x, lower, w, bh, title, detail, fontsize=11.2)
    for a, b in zip(xs[:-1], xs[1:]):
        arrow(ax, (a+w, upper+bh/2), (b, upper+bh/2))
    arrow(ax, (xs[-1]+w/2, upper), (xs[-1]+w/2, lower+bh))
    for a, b in zip(xs[:0:-1], xs[-2::-1]):
        arrow(ax, (a, lower+bh/2), (b+w, lower+bh/2))
    # The packet view is optional and does not enlarge the fixed algebra.
    ax.add_patch(FancyBboxPatch((.35, .25), 6, .55,
        boxstyle="round,pad=0.025,rounding_size=0.06",
        facecolor="white", edgecolor=GRID, linewidth=1))
    ax.text(.53, .525, "Optional packet view", fontsize=10.5,
            weight="bold", color=TEAL, va="center")
    ax.text(2.33, .525, "Project to expose blocks when projectors are available.",
            fontsize=10.2, color=MUTED, va="center")
    save(fig, "01_seed_operator_grammar")


def elliptic():
    h = 4.15
    fig = canvas(r"Multiplication by $y$ exchanges two packets",
        r"Use $k[x]\oplus yk[x]$ in $k[x,y]/(y^2-x^3+x)$.", height=h)
    ax = drawing(fig, h)
    ax.text(.24, 3.04, "Weighted transfer blocks", fontsize=11,
            color=TEAL, weight="bold")
    ax.text(3.66, 3.04, "Packet exchange", fontsize=11,
            color=TEAL, weight="bold")
    ax.plot([3.40, 3.40], [.91, 3.05], color=GRID, linewidth=.8)
    # Ordered rows and columns are (even, odd). Draw brackets explicitly
    # rather than rely on a LaTeX matrix unavailable in portable MathText.
    ax.text(.22, 2.19, r"$M_y=$", fontsize=17, va="center")
    for x, side in [(1.03, 1), (3.07, -1)]:
        ax.plot([x+.12*side, x, x, x+.12*side],
                [2.71, 2.71, 1.65, 1.65], color=INK, linewidth=1.3)
    for x, label in [(1.54, "even"), (2.57, "odd")]:
        ax.text(x, 2.91, label, fontsize=10, color=MUTED, ha="center")
    for x, y, value in [(1.54, 2.48, r"$0$"),
                         (2.57, 2.48, r"$x^3-x$"),
                         (1.54, 1.88, r"$1$"),
                         (2.57, 1.88, r"$0$")]:
        ax.text(x, y, value, fontsize=18, color=INK, ha="center", va="center")
    ax.text(1.73, 1.31, "Columns are inputs.", fontsize=10, color=MUTED,
            ha="center")
    ax.text(1.73, 1.06, "Rows are outputs.", fontsize=10, color=MUTED,
            ha="center")
    bx, by, bw, bh = 3.72, 1.85, 1.12, .73
    box(ax, bx, by, bw, bh, "even", r"$k[x]$", fontsize=11.5)
    box(ax, 5.40, by, bw, bh, "odd", r"$yk[x]$", fontsize=11.5)
    # Upper arrow sends a(x) to y a(x). The return uses y^2=x^3-x.
    arrow(ax, (4.50, 2.58), (5.75, 2.58), curve=-.43)
    ax.text(5.12, 2.91, r"$1$", fontsize=14, color=TEAL,
            ha="center", va="center")
    arrow(ax, (5.75, 1.85), (4.50, 1.85), color=GOLD, curve=-.43)
    ax.text(5.12, 1.44, r"$x^3-x$", fontsize=14, color=GOLD,
            ha="center", va="center")
    ax.text(3.35, .55, r"$M_y^2=(x^3-x)I$", fontsize=16,
            color=TEAL, ha="center", va="center")
    ax.text(3.35, .20, "Two applications preserve each packet.", fontsize=10,
            color=MUTED, ha="center", va="center")
    save(fig, "08_elliptic_packet_transfer")


def dependencies():
    h = 4.55
    fig = canvas("Two proof families meet in the worked models",
                 "Generator arguments and packet arguments form parallel routes.",
                 height=h)
    ax = drawing(fig, h)
    xs = [.20, 1.85, 3.50]
    w, bh = 1.30, .70
    top, bottom = 2.68, 1.38
    ax.text(.20, 3.62, "Generator arguments", fontsize=10.5,
            color=TEAL, weight="bold")
    ax.text(.20, 2.32, "Packet arguments", fontsize=10.5,
            color=GOLD, weight="bold")
    for x, label in zip(xs, ["Fixed operator\ngrammar",
                             "Hulls and\npresentations",
                             "Generator counts\nand bounds"]):
        box(ax, x, top, w, bh, label, color=TEAL, fontsize=10.5)
    for x, label in zip(xs, ["Finite projector\nsystem",
                             "Analysis and\nsynthesis",
                             "Blocks and\ntransport"]):
        box(ax, x, bottom, w, bh, label, color=GOLD,
            face="#F8F4EB", fontsize=10.5)
    final_x, final_y = 5.31, 2.00
    box(ax, final_x, final_y, 1.20, .84, "Worked\nrealizations",
        color=TEAL, face="#E3EEEB", fontsize=11)
    for y, color in [(top, TEAL), (bottom, GOLD)]:
        for a, b in zip(xs[:-1], xs[1:]):
            arrow(ax, (a+w, y+bh/2), (b, y+bh/2), color=color)
        arrow(ax, (xs[-1]+w, y+bh/2), (final_x, final_y+.42), color=color)
    ax.plot([.20, 6.5], [1.00, 1.00], color=GRID, linewidth=.8)
    formulas = [
        (1.23, "Coordinate invariance", r"$P_\alpha\mapsto UP_\alpha U^{-1}$"),
        (3.43, "Realization", r"$\Phi A=\varphi(A)\Phi$"),
        (5.61, "Transfer block", r"$Q_\beta A Q_\alpha$")]
    for x, label, formula in formulas:
        ax.text(x, .78, label, color=MUTED, fontsize=9.7, ha="center")
        ax.text(x, .39, formula, color=INK, fontsize=12, ha="center")
    save(fig, "10_theorem_dependency")


def main():
    grammar()
    elliptic()
    dependencies()


if __name__ == "__main__":
    main()
