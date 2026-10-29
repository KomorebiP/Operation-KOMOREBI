"""Komorebi research presets followed by general plotting tutorials."""
from sequence_presets import SEQUENCE_PRESETS

PRESETS = {
    **SEQUENCE_PRESETS,
    'plot-2d': dict(title='Plot a signal in 2D', group='Graphs', packages=['numpy'],
        description='Two sine waves and their sum. Zoom or inspect individual samples. This is a plotting tutorial, not a claim about a paper.',
        expected='Plotted 201 samples of two waves and their sum.\n',
        code='''import numpy as np
from komorebi_browser import show_plot

x = np.linspace(0, 2*np.pi, 201)
a, b = np.sin(x), 0.5*np.sin(3*x)
show_plot([
    {"x": x, "y": a, "name": "sin(x)", "mode": "lines"},
    {"x": x, "y": b, "name": "0.5 sin(3x)", "mode": "lines"},
    {"x": x, "y": a+b, "name": "Sum", "mode": "lines"},
], {"title": {"text": "Two waves and their sum"},
    "xaxis": {"title": {"text": "x (radians)"}},
    "yaxis": {"title": {"text": "Amplitude"}}},
    description="Two periodic sine waves and their pointwise sum on 0 to 2 pi.")
print("Plotted 201 samples of two waves and their sum.")
'''),
    'surface-3d': dict(title='Explore a 3D surface', group='Graphs', packages=['numpy'],
        description='Rotate the saddle surface z = x squared minus y squared. Keyboard view buttons and a data table provide other ways to inspect it.',
        expected='Surface grid: 41 x 41\nCenter height: 0.0\n',
        code='''import numpy as np
from komorebi_browser import show_plot

x = np.linspace(-2, 2, 41)
y = np.linspace(-2, 2, 41)
X, Y = np.meshgrid(x, y)
Z = X**2 - Y**2
show_plot([{"type": "surface", "x": x, "y": y, "z": Z,
            "colorscale": "Viridis", "name": "Saddle"}],
          {"title": {"text": "Saddle surface: z = x² − y²"},
           "scene": {"xaxis": {"title": {"text": "x"}},
                     "yaxis": {"title": {"text": "y"}},
                     "zaxis": {"title": {"text": "z"}}}},
          description="A saddle rises along the x direction and falls along the y direction. The origin has height zero.")
print("Surface grid: 41 x 41")
print("Center height:", Z[20, 20])
'''),
    'curve-3d': dict(title='Explore a 3D curve', group='Graphs', packages=['numpy'],
        description='A sampled helix with labelled axes, rotation, zoom and downloadable coordinates.',
        expected='Helix samples: 201\n',
        code='''import numpy as np
from komorebi_browser import show_plot

t = np.linspace(0, 4*np.pi, 201)
show_plot([{"type": "scatter3d", "mode": "lines", "name": "Helix",
            "x": np.cos(t), "y": np.sin(t), "z": t/(2*np.pi),
            "line": {"width": 6, "color": "#18563d"}}],
          {"title": {"text": "Two turns of a helix"},
           "scene": {"xaxis": {"title": {"text": "cos(t)"}},
                     "yaxis": {"title": {"text": "sin(t)"}},
                     "zaxis": {"title": {"text": "t / (2π)"}}}},
          description="A helix makes two turns around the vertical axis while rising from height zero to two.")
print("Helix samples:", len(t))
'''),
    'matplotlib': dict(title='Make a Matplotlib figure', group='Graphs', packages=['matplotlib'],
        description='Use ordinary Matplotlib commands to produce a PNG. This preset also exports the plotted numbers as CSV.',
        expected='Created a Matplotlib figure and parabola.csv.\n',
        code='''import numpy as np
import matplotlib.pyplot as plt
from komorebi_browser import show_matplotlib, export_file

x = np.linspace(-2, 2, 81)
y = x**2
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(x, y, color="#18563d", label="y = x²")
ax.set(xlabel="x", ylabel="y", title="A parabola")
ax.grid(True, alpha=0.3)
ax.legend()
show_matplotlib(fig, description="A parabola with its minimum at the origin. Values rise to four at x = minus two and two.")
export_file("parabola.csv", "x,y\\n" + "".join(f"{a},{b}\\n" for a,b in zip(x,y)))
print("Created a Matplotlib figure and parabola.csv.")
'''),
    'symbolic': dict(title='Calculate with SymPy', group='Calculations', packages=['sympy'],
        description='Differentiate, integrate and factor a polynomial using exact symbolic expressions.',
        expected='Polynomial: x**3 - 3*x + 2\nDerivative: 3*x**2 - 3\nIntegral on [0, 1]: 3/4\nFactorization: (x - 1)**2*(x + 2)\n',
        code='''import sympy as sp

x = sp.symbols("x")
f = x**3 - 3*x + 2
print("Polynomial:", f)
print("Derivative:", sp.diff(f, x))
print("Integral on [0, 1]:", sp.integrate(f, (x, 0, 1)))
print("Factorization:", sp.factor(f))
assert sp.expand(sp.factor(f)) == f
'''),
    'scientific': dict(title='Calculate with SciPy', group='Calculations', packages=['scipy'],
        description='Numerically integrate x squared on [0, 1] and compare with the known value one third. The printed value is rounded.',
        expected='Integral of x squared on [0, 1]: 0.333333\nWithin 1e-12 of one third: True\n',
        code='''from scipy.integrate import quad

value, estimated_error = quad(lambda x: x*x, 0, 1)
print(f"Integral of x squared on [0, 1]: {value:.6f}")
print("Within 1e-12 of one third:", abs(value - 1/3) < 1e-12)
assert abs(value - 1/3) < 1e-12
'''),
    'data': dict(title='Plot CSV or JSON data', group='Data', packages=[],
        description='Upload a CSV with x,y columns or a JSON array of objects with x and y fields. With no upload, this uses the supplied sample. When several files are loaded, the first filename in alphabetical order is used.',
        expected='Using sample data.\nPlotted 4 rows.\n',
        code='''import csv
import io
import json
from komorebi_browser import show_plot, export_file

if uploaded_files:
    name = sorted(uploaded_files)[0]
    text = uploaded_files[name]
    rows = json.loads(text) if name.lower().endswith(".json") else list(csv.DictReader(io.StringIO(text)))
    print("Using:", name)
else:
    rows = [{"x": 0, "y": 1}, {"x": 1, "y": 3}, {"x": 2, "y": 5}, {"x": 3, "y": 7}]
    print("Using sample data.")
x, y = [float(r["x"]) for r in rows], [float(r["y"]) for r in rows]
show_plot([{"x": x, "y": y, "mode": "lines+markers", "name": "Data"}],
          {"title": {"text": "Your x,y data"},
           "xaxis": {"title": {"text": "x"}}, "yaxis": {"title": {"text": "y"}}},
          description=f"A plot of {len(rows)} supplied x,y pairs. Inspect the data table for the numbers.")
export_file("processed-data.json", json.dumps([{"x": a, "y": b} for a,b in zip(x,y)], indent=2))
print(f"Plotted {len(rows)} rows.")
'''),
}
