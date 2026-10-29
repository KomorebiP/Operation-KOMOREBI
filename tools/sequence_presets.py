"""Browser experiments tied to Komorebi's reciprocal and sequence work."""

SEQUENCE_PRESETS = {
    'sequence-growth': dict(
        title='Reciprocal sequences and factorial growth', group='Komorebi sequence research',
        packages=['numpy'], works=['paper-iv'], run_label='sequence growth',
        guide='reciprocal-growth',
        description='Use Komorebi Math to compare exact reciprocal coefficients with (Nn)!, then inspect the coefficients after factorial normalization. Start with N = 4 and r = 1.',
        expected='Reciprocal family: N=4, r=1\nComputed n=0 through 15 with exact integers.\nA(0..4): (1, 1, 69, 33661, 60376809)\nExported exact coefficients and rational normalizations.\n',
        code='''from fractions import Fraction
from math import factorial, log10
from komorebi_math.sequences import reciprocal_coefficients
from komorebi_browser import show_plot, export_file

# D_N(t)^(-r) = sum A(n) t^(N*n) / (N*n)!
# Change these integer parameters and run again.
N, r, count = 4, 1, 16
if not (type(N) is int and 2 <= N <= 8 and type(r) is int and 1 <= r <= 3
        and type(count) is int and 2 <= count <= 16):
    raise ValueError("Use N=2..8, r=1..3, and count=2..16 for this experiment.")
a = reciprocal_coefficients(N, count, power=r)
ns = list(range(count))
scale = [factorial(N*n) for n in ns]
normalized = [Fraction(a[n], scale[n]) for n in ns]
if any(value <= 0 for value in a):
    raise ValueError("This logarithmic view requires positive coefficients.")

show_plot([
    {"x": ns, "y": [log10(value) for value in a], "mode": "lines+markers",
     "name": "Sequence A(n)", "line": {"color": "#0067a5"}, "marker": {"symbol": "circle"},
     "hovertemplate": "n = %{x}<br>log10 A(n) = %{y:.3f}<extra>Sequence</extra>"},
    {"x": ns, "y": [log10(value) for value in scale], "mode": "lines+markers",
     "name": "Factorial (Nn)!", "line": {"color": "#b54b00", "dash": "dash"}, "marker": {"symbol": "diamond"},
     "hovertemplate": "n = %{x}<br>log10 (Nn)! = %{y:.3f}<extra>Factorial</extra>"}],
    {"title": {"text": f"Sequence and factorial growth (N={N}, r={r})"},
     "xaxis": {"title": {"text": "Index n"}, "dtick": 2},
     "yaxis": {"title": {"text": "Size, in powers of 10"}}},
    description="Blue circles show A(n). Orange diamonds show (Nn)!. A height of 20 means 10 to the power 20. Each step in n adds N to the degree. This finite comparison does not establish an asymptotic equivalence.")
show_plot([{"x": ns,
    "y": [log10(v.numerator)-log10(v.denominator) for v in normalized],
    "mode": "lines+markers", "name": "Normalized coefficients",
    "hovertemplate": "n = %{x}<br>log10 normalized value = %{y:.3f}<extra></extra>"}],
    {"title": {"text": f"After division by (Nn)!: N={N}, r={r}"},
     "xaxis": {"title": {"text": "Index n"}, "dtick": 2},
     "yaxis": {"title": {"text": "Normalized size (log10)"}}},
    description="Each value is A(n) divided by (Nn)!. A height of -3 means 0.001. A fall of one unit means a value ten times smaller. Lines connect discrete samples. Exact fractions are in the CSV below.")
csv = "N,r,n,degree,A,factorial,normalized_fraction\\n"
csv += "".join(f"{N},{r},{n},{N*n},{a[n]},{scale[n]},{normalized[n]}\\n" for n in ns)
export_file("reciprocal-growth-exact.csv", csv)
print(f"Reciprocal family: N={N}, r={r}")
print(f"Computed n=0 through {count-1} with exact integers.")
print("A(0..4):", a[:5])
print("Exported exact coefficients and rational normalizations.")
'''),
    'sequence-landscape': dict(
        title='Compare reciprocal families in 2D and 3D', group='Komorebi sequence research',
        packages=['numpy'], works=['paper-iv'], run_label='sequence landscape',
        guide='reciprocal-landscape',
        description='Start with a labelled 2D comparison of N = 2 through 8. A separate 3D view follows. Both show the same factorial-normalized values, with exact fractions available as CSV.',
        expected='Reciprocal landscape: N=2..8, r=1, n=0..15\nExact coefficient samples: 112\nSecant anchor A_2(0..5): (1, 1, 5, 61, 1385, 50521)\nExported exact coefficients. Plot heights are approximate logarithms.\n',
        code='''from fractions import Fraction
from math import factorial, log10
from komorebi_math.sequences import reciprocal_coefficients
from komorebi_browser import show_plot, export_file

r, count = 1, 16
if not (type(r) is int and 1 <= r <= 3 and type(count) is int and 2 <= count <= 16):
    raise ValueError("Use r=1..3 and count=2..16 for this experiment.")
ns = list(range(count))
traces = []
flat_traces = []
colors = ["#0067a5", "#b54b00", "#007d60", "#963f87", "#6b58a3", "#89532d", "#353d46"]
symbols = ["circle", "diamond", "square", "triangle-up", "cross", "x", "triangle-down"]
csv = "N,r,n,degree,A,normalized_fraction\\n"
for N in range(2, 9):
    a = reciprocal_coefficients(N, count, power=r)
    fractions = [Fraction(a[n], factorial(N*n)) for n in ns]
    if any(v <= 0 for v in fractions):
        raise ValueError("This logarithmic view requires positive coefficients.")
    heights = [log10(v.numerator)-log10(v.denominator) for v in fractions]
    flat_traces.append({"mode": "lines+markers+text", "name": f"N={N}", "cliponaxis": False,
                       "x": ns, "y": heights, "text": [""]*(count-1)+[f"N={N}"],
                       "textposition": "middle right", "textfont": {"size": 15, "color": colors[N-2]},
                       "line": {"color": colors[N-2], "dash": "solid" if N % 2 == 0 else "dash"},
                       "marker": {"symbol": symbols[N-2], "size": 8},
                       "hovertemplate": "n = %{x}<br>log10 normalized value = %{y:.3f}<extra>"+f"N={N}"+"</extra>"})
    traces.append({"type": "scatter3d", "mode": "lines+markers", "name": f"N={N}",
                   "x": ns, "y": [N]*count, "z": heights,
                   "line": {"color": colors[N-2]}, "marker": {"size": 5},
                   "hovertemplate": "n = %{x}<br>N = %{y}<br>log10 normalized value = %{z:.3f}<extra></extra>"})
    csv += "".join(f"{N},{r},{n},{N*n},{a[n]},{fractions[n]}\\n" for n in ns)
show_plot(flat_traces,
    {"title": {"text": f"Compare the seven reciprocal families (r={r})"},
     "xaxis": {"title": {"text": "Index n"}, "dtick": 2, "range": [-0.3, count+0.8]},
     "yaxis": {"title": {"text": "Normalized size (log10)"}}},
    description="Read each labelled line from left to right. Its height is log10 of A(n)/(Nn)!. A height of -10 means 10 to the power -10. Each step down is a smaller normalized coefficient. Use the checkboxes to compare fewer families. Equal n at different N means different degrees Nn.")
show_plot(traces,
    {"title": {"text": "The same families in 3D"},
     "scene": {"xaxis": {"title": {"text": "n"}},
               "yaxis": {"title": {"text": "N"}, "dtick": 1},
               "zaxis": {"title": {"text": "log10 value"}}}},
    description="Axes: n is the sequence index, N is the integer spacing, and height is log10 of A(n)/(Nn)!. This is the same data as the 2D chart above. Lines connect samples within a family. There is no interpolation between different N values.")
export_file("reciprocal-landscape-exact.csv", csv)
print(f"Reciprocal landscape: N=2..8, r={r}, n=0..{count-1}")
print("Exact coefficient samples:", 7*count)
print("Secant anchor A_2(0..5):", reciprocal_coefficients(2, 6))
print("Exported exact coefficients. Plot heights are approximate logarithms.")
'''),
    'factorial-weights': dict(
        title='Factorial weights in the sequence atlas', group='Komorebi sequence research',
        packages=['numpy'], works=['monographs-special-functions'], run_label='factorial weights',
        guide='factorial-weights',
        description='Compare a Stirling row with its factorial-weighted row using ordinary counts. Then inspect a 2D map of contributions, with a separate 3D view below it.',
        expected='Stirling row n=5: [0, 1, 15, 25, 10, 1]\nFactorial-weighted row: [0, 1, 30, 150, 240, 120]\nBell row sum: 52\nFubini row sum: 541\nAll 19 weighted row sums match Komorebi Math.\nExported exact contributions through n=18.\n',
        code='''from math import factorial, log10
from komorebi_math.sequences import fubini_sequence
from komorebi_browser import show_plot, export_file

last, row = 18, 5
if not (type(last) is int and 0 <= last <= 18 and type(row) is int and 0 <= row <= last):
    raise ValueError("Use last=0..18 and row=0..last.")
S = [[0]*(last+1) for _ in range(last+1)]
S[0][0] = 1
for n in range(1, last+1):
    for k in range(1, n+1):
        S[n][k] = k*S[n-1][k] + S[n-1][k-1]
weighted = [[factorial(k)*S[n][k] for k in range(n+1)] for n in range(last+1)]
if tuple(map(sum, weighted)) != fubini_sequence().first(last+1):
    raise ArithmeticError("The Stirling sums disagree with the independent library recurrence.")
ks = list(range(row+1))
show_plot([
    {"type": "bar", "x": ks, "y": S[row][:row+1],
     "name": "Unordered S(n,k)", "marker": {"color": "#0067a5"},
     "hovertemplate": "k = %{x}<br>Count = %{y}<extra>Unordered blocks</extra>"},
    {"type": "bar", "x": ks, "y": weighted[row],
     "name": "Ordered k! S(n,k)", "marker": {"color": "#b54b00", "pattern": {"shape": "/"}},
     "hovertemplate": "k = %{x}<br>Count = %{y}<extra>Ordered blocks</extra>"}],
    {"title": {"text": f"What factorial weighting changes (n={row})"}, "barmode": "group",
     "xaxis": {"title": {"text": "Number of blocks k"}, "dtick": 1},
     "yaxis": {"title": {"text": "Count"}, "rangemode": "tozero"}},
    description=f"Blue bars count unordered partitions. Striped orange bars count ordered partitions. These are ordinary counts, not logarithms. For this row the totals are {sum(S[row])} and {sum(weighted[row])}. Exact values are in the CSV below.")
show_plot([{"type": "heatmap", "x": list(range(last+1)), "y": list(range(last+1)),
    "z": [[log10(1+weighted[n][k]) if k <= n else None for n in range(last+1)] for k in range(last+1)],
    "colorscale": "Cividis", "zmin": 0, "hoverongaps": False,
    "colorbar": {"orientation": "h", "y": 1.12, "yanchor": "bottom", "len": 0.95, "thickness": 16, "nticks": 4, "title": {"text": "log10 (1 + count)", "side": "top"}},
    "hovertemplate": "n = %{x}<br>k = %{y}<br>log10 (1 + count) = %{z:.3f}<extra></extra>"}],
    {"title": {"text": "Where the factorial-weighted contributions sit"},
     "xaxis": {"title": {"text": "Set size n"}, "dtick": 3},
     "yaxis": {"title": {"text": "Block count k"}, "dtick": 3}, "margin": {"t": 120}},
    description="Each square is one integer pair (n, k). Read a column to inspect a row of Stirling contributions. Brighter squares mean larger k! S(n,k), using log10(1 + count). The white triangle has k greater than n and is outside the domain. The data table gives the plotted values.")
points = [(n, k, weighted[n][k]) for n in range(last+1) for k in range(n+1) if weighted[n][k]]
show_plot([{"type": "scatter3d", "mode": "markers", "name": "Nonzero contributions",
    "x": [n for n,k,v in points], "y": [k for n,k,v in points],
    "z": [log10(1+v) for n,k,v in points],
    "hovertemplate": "n = %{x}<br>k = %{y}<br>log10 (1 + count) = %{z:.3f}<extra></extra>",
    "marker": {"size": 5, "color": [log10(1+v) for n,k,v in points], "colorscale": "Cividis", "cmin": 0}}],
    {"title": {"text": "The contributions in 3D"},
     "scene": {"xaxis": {"title": {"text": "n"}},
               "yaxis": {"title": {"text": "k"}},
               "zaxis": {"title": {"text": "Log size"}}}},
    description="Axes: n is set size, k is block count, and height is log10(1 + k! S(n,k)). This shows the nonzero entries from the 2D map above. Each exact row sum is a Fubini number. The CSV also includes zero contributions.")
csv = "n,k,stirling,k_factorial,weighted_contribution\\n"
csv += "".join(f"{n},{k},{S[n][k]},{factorial(k)},{weighted[n][k]}\\n" for n in range(last+1) for k in range(n+1))
export_file("factorial-stirling-exact.csv", csv)
print(f"Stirling row n={row}:", S[row][:row+1])
print("Factorial-weighted row:", weighted[row])
print("Bell row sum:", sum(S[row]))
print("Fubini row sum:", sum(weighted[row]))
print(f"All {last+1} weighted row sums match Komorebi Math.")
print(f"Exported exact contributions through n={last}.")
'''),
}
