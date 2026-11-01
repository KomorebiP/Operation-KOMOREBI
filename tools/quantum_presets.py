"""Exact partial-dephasing experiment accompanying the extended derivation."""

QUANTUM_PRESETS = {
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
