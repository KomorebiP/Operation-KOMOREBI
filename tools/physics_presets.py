"""Small physics illustrations; formal and experimental scope stays in the sources."""
from quantum_presets import QUANTUM_PRESETS

PHYSICS_PRESETS = {
    **QUANTUM_PRESETS,
    'physics-current': dict(
        title='Watch probability move between packets', group='Physics', packages=[],
        works=['monographs-physics'], collection_guide='packet-current',
        run_label='packet current',
        description='Rotate a two-component state, follow its packet squared norms, and check the receiving-first current signs. This is a finite mathematical example.',
        expected='Initial packet squared norms: 1, 1\nInitial incoming currents: -2, 2\nTotal squared norm: 2\nPlotted 161 times on [0, 2 pi].\n',
        code='''from fractions import Fraction as Q
from math import cos, sin, pi
from komorebi_browser import show_plot

# A = [[0, -1], [1, 0]], psi(0) = (1, 1).
# psi is intentionally unnormalized. The conserved squared norm is 2.
x, y = Q(1), Q(1)
incoming = (2*x*(-y), 2*y*x)
assert incoming == (-2, 2) and sum(incoming) == 0
print(f"Initial packet squared norms: {x*x}, {y*y}")
print(f"Initial incoming currents: {incoming[0]}, {incoming[1]}")
print("Total squared norm:", x*x+y*y)

times = [2*pi*j/160 for j in range(161)]
e0 = [(cos(t)-sin(t))**2 for t in times]
e1 = [(sin(t)+cos(t))**2 for t in times]
show_plot([
    {"x": times, "y": e0, "name": "Packet 0", "mode": "lines"},
    {"x": times, "y": e1, "name": "Packet 1", "mode": "lines", "line": {"dash": "dash"}},
    {"x": times, "y": [a+b for a,b in zip(e0,e1)], "name": "Total", "mode": "lines", "line": {"dash": "dot"}},
], {"title": {"text": "Exchange between two orthogonal packets"},
    "xaxis": {"title": {"text": "Time t"}},
    "yaxis": {"title": {"text": "Squared norm"}}},
    description="The two packet squared norms exchange between zero and two. Their sum stays at two. Divide each by two to get normalized probabilities. The initial incoming currents are minus two and plus two.")
print("Plotted 161 times on [0, 2 pi].")
'''),
    'physics-phase': dict(
        title='See quantum phase change a measurement', group='Physics', packages=[],
        works=['paper-vii'], collection_guide='quantum-phase', run_label='quantum phase',
        description='Compare (3/5, 4i/5) and (3/5, 4/5). Exact rational probabilities agree in the coordinate basis and differ after a Hadamard change of basis.',
        expected='Coordinate probabilities: 9/25, 16/25\nHadamard probabilities with phase i: 1/2, 1/2\nHadamard probabilities with phase 1: 49/50, 1/50\nPurity after coordinate dephasing: 337/625\n',
        code='''from fractions import Fraction as Q
from komorebi_browser import show_plot

a, b = Q(3, 5), Q(4, 5)
if a*a+b*b != 1:
    raise ValueError("Choose real a and b with a*a+b*b = 1.")
coordinate = (a*a, b*b)
# H(a, ib) = ((a+ib)/sqrt(2), (a-ib)/sqrt(2)).
phase_i = ((a*a+b*b)/2, (a*a+b*b)/2)
phase_1 = ((a+b)**2/2, (a-b)**2/2)
purity = sum(p*p for p in coordinate)
print(f"Coordinate probabilities: {coordinate[0]}, {coordinate[1]}")
print(f"Hadamard probabilities with phase i: {phase_i[0]}, {phase_i[1]}")
print(f"Hadamard probabilities with phase 1: {phase_1[0]}, {phase_1[1]}")
print("Purity after coordinate dephasing:", purity)
show_plot([
    {"type": "bar", "x": ["Outcome 0", "Outcome 1"], "y": list(map(float, coordinate)), "name": "Coordinate basis, either state"},
    {"type": "bar", "x": ["Outcome 0", "Outcome 1"], "y": list(map(float, phase_i)), "name": "Hadamard basis, phase i"},
    {"type": "bar", "x": ["Outcome 0", "Outcome 1"], "y": list(map(float, phase_1)), "name": "Hadamard basis, phase 1"},
], {"title": {"text": "Relative phase changes interference"}, "barmode": "group",
    "yaxis": {"title": {"text": "Probability"}, "range": [0, 1]}},
    description="Both states have coordinate probabilities 9/25 and 16/25. After a Hadamard transformation, the phase-i state has probabilities one half and one half; the real state has probabilities 49/50 and 1/50. Printed fractions are exact; bar heights use floating-point conversion.")
'''),
    'physics-centered': dict(
        title='Compare a centered symbol with its continuum limit', group='Physics', packages=[],
        works=['monographs-physics'], collection_guide='continuum-limit',
        run_label='centered symbol',
        description='Plot sin(h k)/h beside k, then compare a fixed three-momentum modal error with the quadratic envelope. Floating-point samples illustrate the source theorem.',
        expected='Fixed momentum: (1, 2, -1)\nSpacings: 0.5, 0.25, 0.125, 0.0625\nExported 4 modal error comparisons.\nThese floating-point samples illustrate the bound; the Lean source supplies the general theorem.\n',
        code='''import csv
import io
from math import sin, sqrt
from komorebi_browser import show_plot, export_file

momentum = (1, 2, -1)
spacings = [0.5, 0.25, 0.125, 0.0625]
if any(h == 0 for h in spacings):
    raise ValueError("Use nonzero spacings; the bounded global operator has a separate zero-spacing convention.")
ks = [-4+j/20 for j in range(161)]
traces = [{"x": ks, "y": ks, "name": "Continuum k", "mode": "lines", "line": {"dash": "dash"}}]
for h in spacings[:2]:
    traces.append({"x": ks, "y": [sin(h*k)/h for k in ks], "name": f"Centered, h={h}", "mode": "lines"})
show_plot(traces, {"title": {"text": "Centered spatial symbol"},
    "xaxis": {"title": {"text": "Momentum coordinate k"}},
    "yaxis": {"title": {"text": "Symbol"}}},
    description="The continuum symbol is the line k. Centered symbols sin(h k)/h approach that line at each fixed k as the nonzero spacing tends to zero. This plot uses a fixed momentum window.")

moment = sqrt(sum(k**6 for k in momentum))
rows = [(h, sqrt(sum((sin(h*k)/h-k)**2 for k in momentum)), h*h*moment/6) for h in spacings]
show_plot([
    {"x": spacings, "y": [row[1] for row in rows], "name": "Modal symbol error", "mode": "lines+markers"},
    {"x": spacings, "y": [row[2] for row in rows], "name": "h squared times sqrt(66) / 6", "mode": "lines+markers", "line": {"dash": "dash"}},
], {"title": {"text": "Quadratic error at fixed momentum (1, 2, -1)"},
    "xaxis": {"title": {"text": "Nonzero spacing h"}, "type": "log"},
    "yaxis": {"title": {"text": "Error or envelope"}, "type": "log"}},
    description="Four fixed-momentum symbol errors lie below the h-squared envelope. This is a finite floating-point illustration, with values available as CSV. It does not test arbitrary infinite Fourier series or a changing finite lattice.")
stream = io.StringIO(newline="")
writer = csv.writer(stream, lineterminator="\\n")
writer.writerow(["h", "modal_symbol_error", "quadratic_envelope"])
writer.writerows(rows)
export_file("centered-modal-errors.csv", stream.getvalue())
print("Fixed momentum:", momentum)
print("Spacings:", ", ".join(map(str, spacings)))
print("Exported 4 modal error comparisons.")
print("These floating-point samples illustrate the bound; the Lean source supplies the general theorem.")
'''),
}
