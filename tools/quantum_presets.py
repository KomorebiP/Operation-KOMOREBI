"""Exact partial-dephasing experiment accompanying the extended derivation."""

QUANTUM_PRESETS = {
    'physics-arithmetic-phase': dict(
        title='Separate equal histograms with an arithmetic projector', group='Physics', packages=[],
        works=['monographs-quantum-and-circuits'], collection_guide='quantum-phase',
        run_label='arithmetic phase comparison',
        description='Use the book’s modulus-12 Ramanujan projector to distinguish signed, unsigned, and dephased states. Edit a rational unit phase; download exact probabilities.',
        expected='Common coordinate probabilities sum: 1\nSelected probability, edited phase: 1/5\nUnsigned coherent: 0\nSigned coherent: 1\nComplete coordinate dephasing: 1/3\nExported 5 exact phase comparisons.\n',
        code='''from fractions import Fraction as Q
import csv
import io
from komorebi_browser import show_plot, export_file

# Quantum and Circuits, quantum arithmetic QA13-QA14 and QA19-QA20.
c = (4, 0, 2, 0, -2, 0, -4, 0, -2, 0, 2, 0)
phase_real, phase_imag = Q(3, 5), Q(4, 5)
if phase_real**2 + phase_imag**2 != 1:
    raise ValueError("Choose a unit phase: real squared + imaginary squared = 1.")
projector = [[Q(c[(n-m) % 12], 12) for m in range(12)] for n in range(12)]
histogram = [Q(x*x, 48) for x in c]

def selected(real, imag):
    # Unnormalized v_+ + z v_-; divide squared norms by 48.
    vr = [Q(abs(x)) if x >= 0 else abs(x)*real for x in c]
    vi = [Q(0) if x >= 0 else abs(x)*imag for x in c]
    pr = [sum(row[m]*vr[m] for m in range(12)) for row in projector]
    pi = [sum(row[m]*vi[m] for m in range(12)) for row in projector]
    probability = sum(a*a+b*b for a, b in zip(pr, pi))/48
    assert probability == (1-real)/2
    return probability

dephased = sum(projector[n][n]*histogram[n] for n in range(12))
print("Common coordinate probabilities sum:", sum(histogram))
print("Selected probability, edited phase:", selected(phase_real, phase_imag))
print("Unsigned coherent:", selected(Q(1), Q(0)))
print("Signed coherent:", selected(Q(-1), Q(0)))
print("Complete coordinate dephasing:", dephased)
phases = [("1", Q(1), Q(0)), ("i", Q(0), Q(1)), ("-1", Q(-1), Q(0)),
          ("-i", Q(0), Q(-1)), ("edited phase", phase_real, phase_imag)]
rows = [(label, re, im, selected(re, im), dephased) for label, re, im in phases]
show_plot([
    {"type": "bar", "x": [r[0] for r in rows], "y": [float(r[3]) for r in rows], "name": "Coherent state"},
    {"type": "bar", "x": [r[0] for r in rows], "y": [float(r[4]) for r in rows], "name": "After coordinate dephasing"},
], {"title": {"text": "Same coordinate histogram, different arithmetic interference"},
    "barmode": "group", "yaxis": {"title": {"text": "Selected probability"}, "range": [0, 1]}},
    description="The modulus-12 projector selects four coprime Fourier labels. The unsigned coherent state has probability zero, the signed state one, and all fully coordinate-dephased states one third. Other phases interpolate without changing the original coordinate histogram. CSV fractions are exact; bar heights use floating-point conversion.")
stream = io.StringIO(newline="")
writer = csv.writer(stream, lineterminator="\\n")
writer.writerow(["phase", "phase_real", "phase_imag", "coherent_selected_probability", "dephased_selected_probability"])
writer.writerows(rows)
export_file("arithmetic-phase.csv", stream.getvalue())
print("Exported 5 exact phase comparisons.")
'''),
    'physics-dephasing': dict(
        title='Recover a state after partial dephasing', group='Physics', packages=[],
        works=['paper-vii'], collection_guide='quantum-phase',
        run_label='partial dephasing and tomography',
        description='Edit a rational unit phase and retained coherence t. Compare three measurement settings, reconstruct the density matrix, and export exact probabilities and purity.',
        expected='Phase: (3/5) + (4/5)i\nRetained coherence: 1/2\nMeasured X+, Y+, Z+: 161/250, 173/250, 9/25\nOutput purity: 409/625\nRecovered original upper-right entry: (36/125) + (-48/125)i\nExported 9 exact partial-dephasing rows.\n',
        code='''from fractions import Fraction as Q
import csv
import io
from komorebi_browser import show_plot, export_file

# Edit these exact inputs. phase_real**2 + phase_imag**2 must equal 1.
phase_real, phase_imag = Q(3, 5), Q(4, 5)
t = Q(1, 2)  # Retained coherence: 0 means full dephasing; 1 means none.
if phase_real**2 + phase_imag**2 != 1:
    raise ValueError("Choose a unit phase: real squared + imaginary squared = 1.")
if not 0 <= t <= 1:
    raise ValueError("Retained coherence t must lie in [0, 1].")
p, q = Q(9, 25), Q(16, 25)
original_re, original_im = Q(12, 25)*phase_real, -Q(12, 25)*phase_imag

def measure(retained):
    re, im = retained*original_re, retained*original_im
    return Q(1, 2)+re, Q(1, 2)-im, p, p*p+q*q+2*(re*re+im*im)

px, py, pz, purity = measure(t)
# Tomography uses exact ensemble probabilities from three alternative settings.
reconstructed_re, reconstructed_im = px-Q(1, 2), Q(1, 2)-py
assert (reconstructed_re, reconstructed_im) == (t*original_re, t*original_im)
print(f"Phase: ({phase_real}) + ({phase_imag})i")
print("Retained coherence:", t)
print(f"Measured X+, Y+, Z+: {px}, {py}, {pz}")
print("Output purity:", purity)
if t:
    recovered_re, recovered_im = reconstructed_re/t, reconstructed_im/t
    assert (recovered_re, recovered_im) == (original_re, original_im)
    print(f"Recovered original upper-right entry: ({recovered_re}) + ({recovered_im})i")
else:
    print("Full dephasing: the original coherence cannot be recovered from this output.")

retained_values = [Q(j, 8) for j in range(9)]
rows = [(s, *measure(s), Q(288, 625)*(1-s)**2) for s in retained_values]
traces = []
for index, label in ((1, "X-plus"), (2, "Y-plus"), (3, "Z-plus"), (4, "Purity")):
    traces.append({"x": list(map(float, retained_values)),
                   "y": [float(row[index]) for row in rows],
                   "name": label, "mode": "lines+markers"})
show_plot(traces, {"title": {"text": "Partial dephasing: measurement and purity"},
    "xaxis": {"title": {"text": "Retained coherence t"}},
    "yaxis": {"title": {"text": "Probability or purity"}, "range": [0, 1]}},
    description="Nine exact rational coherence fractions from zero to one. Z probability stays at 9/25. X and Y probabilities depend on the chosen phase; purity rises from 337/625 to one. Plot coordinates are floating-point conversions; the CSV preserves exact fractions.")
stream = io.StringIO(newline="")
writer = csv.writer(stream, lineterminator="\\n")
writer.writerow(["retained_coherence", "p_X_plus", "p_Y_plus", "p_Z_plus", "purity", "squared_HS_error"])
writer.writerows(rows)
export_file("partial-dephasing.csv", stream.getvalue())
print("Exported 9 exact partial-dephasing rows.")
'''),
}
