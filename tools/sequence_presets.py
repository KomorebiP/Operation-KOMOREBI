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
     "name": "log10 A(n)", "text": [str(value) for value in a]},
    {"x": ns, "y": [log10(value) for value in scale], "mode": "lines+markers",
     "name": "log10 (Nn)!"}],
    {"title": {"text": f"Reciprocal coefficients and factorial scale: N={N}, r={r}"},
     "xaxis": {"title": {"text": "Compressed index n (degree = Nn)"}},
     "yaxis": {"title": {"text": "Base-10 logarithm"}}},
    description="Two finite sequences on a logarithmic scale: exact reciprocal coefficients and their factorial scale. Similar growth in this window does not establish an asymptotic equivalence.")
show_plot([{"x": ns,
    "y": [log10(v.numerator)-log10(v.denominator) for v in normalized],
    "mode": "lines+markers", "name": "Normalized coefficients",
    "text": [str(v) for v in normalized]}],
    {"title": {"text": f"After division by (Nn)!: N={N}, r={r}"},
     "xaxis": {"title": {"text": "Compressed index n"}},
     "yaxis": {"title": {"text": "log10 [A(n) / (Nn)!]"}}},
    description="The factorial-normalized coefficients on a logarithmic scale. Points are discrete terms. Connecting lines are a visual guide. The exact CSV keeps the rational values.")
csv = "N,r,n,degree,A,factorial,normalized_fraction\\n"
csv += "".join(f"{N},{r},{n},{N*n},{a[n]},{scale[n]},{normalized[n]}\\n" for n in ns)
export_file("reciprocal-growth-exact.csv", csv)
print(f"Reciprocal family: N={N}, r={r}")
print(f"Computed n=0 through {count-1} with exact integers.")
print("A(0..4):", a[:5])
print("Exported exact coefficients and rational normalizations.")
'''),
    'sequence-landscape': dict(
        title='Reciprocal family in 3D', group='Komorebi sequence research',
        packages=['numpy'], works=['paper-iv'], run_label='sequence landscape',
        guide='reciprocal-landscape',
        description='Compare N = 2 through 8 at the same compressed indices. Height is log10 of A(n)/(Nn)!. Each row is a discrete sequence, with exact values available as CSV.',
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
csv = "N,r,n,degree,A,normalized_fraction\\n"
for N in range(2, 9):
    a = reciprocal_coefficients(N, count, power=r)
    fractions = [Fraction(a[n], factorial(N*n)) for n in ns]
    if any(v <= 0 for v in fractions):
        raise ValueError("This logarithmic view requires positive coefficients.")
    heights = [log10(v.numerator)-log10(v.denominator) for v in fractions]
    traces.append({"type": "scatter3d", "mode": "lines+markers", "name": f"N={N}",
                   "x": ns, "y": [N]*count, "z": heights,
                   "marker": {"size": 3}, "text": [str(v) for v in fractions]})
    csv += "".join(f"{N},{r},{n},{N*n},{a[n]},{fractions[n]}\\n" for n in ns)
show_plot(traces,
    {"title": {"text": f"Reciprocal family after factorial normalization, r={r}"},
     "scene": {"xaxis": {"title": {"text": "Compressed index n"}},
               "yaxis": {"title": {"text": "Integer spacing N"}, "dtick": 1},
               "zaxis": {"title": {"text": "log10 [A(n)/(Nn)!]"}}}},
    description="Seven discrete reciprocal sequences, one for each integer N from two through eight. Height is the logarithm after factorial normalization. There is no interpolation between different N values and no assertion of a continuous parameter surface.")
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
        description='Explore the atlas calculation A(n) = sum k! S(n,k). Compare a Stirling row with its factorial-weighted row, then inspect the contributions across n and k in 3D.',
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
    {"type": "bar", "x": ks, "y": [log10(1+v) for v in S[row][:row+1]],
     "name": "S(n,k)", "text": [str(v) for v in S[row][:row+1]]},
    {"type": "bar", "x": ks, "y": [log10(1+v) for v in weighted[row]],
     "name": "k! S(n,k)", "text": [str(v) for v in weighted[row]]}],
    {"title": {"text": f"Factorial weights order the blocks: n={row}"}, "barmode": "group",
     "xaxis": {"title": {"text": "Number of blocks k"}, "dtick": 1},
     "yaxis": {"title": {"text": "log10 (1 + contribution)"}}},
    description="Each pair of bars compares S(n,k) with k! times S(n,k). The logarithm includes one so that zero terms remain visible. Summation uses the exact contributions, not the heights of these bars.")
points = [(n, k, weighted[n][k]) for n in range(last+1) for k in range(n+1) if weighted[n][k]]
show_plot([{"type": "scatter3d", "mode": "markers", "name": "Nonzero contributions",
    "x": [n for n,k,v in points], "y": [k for n,k,v in points],
    "z": [log10(1+v) for n,k,v in points], "text": [str(v) for n,k,v in points],
    "marker": {"size": 3, "color": [k for n,k,v in points], "colorscale": "Viridis"}}],
    {"title": {"text": "Factorial-weighted Stirling contributions"},
     "scene": {"xaxis": {"title": {"text": "Set size n"}},
               "yaxis": {"title": {"text": "Block count k"}},
               "zaxis": {"title": {"text": "log10 (1 + k! S(n,k))"}}}},
    description="Discrete points over the triangular integer domain zero through the selected maximum n. Only nonzero contributions are plotted. Each exact row sum is a Fubini number. The CSV also includes zero contributions.")
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
