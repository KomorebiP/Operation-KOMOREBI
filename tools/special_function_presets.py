"""Source-linked coupled-series browser example with an explicit local tail envelope."""

SPECIAL_FUNCTION_PRESETS = {
    'special-functions-coupled': dict(
        title='Explore coupled contraction functions', group='Special Functions',
        packages=[], works=['monographs-special-functions'],
        guide_page='SPECIAL_FUNCTIONS', guide_anchor='coupled-lab',
        run_label='coupled special functions',
        description='Compute exact rational coefficients for two coupled series, plot their degree-23 Taylor polynomials, and display the source majorant on the unit disk.',
        expected='Scales (q, r, a, b): 1/3, 2/3, 1/2, 3/4\nCoefficients retained per component: 12 (through degree 23)\nu_1 = 2/27; v_1 = 1/8\nUniform omitted-tail envelope on |z| <= 1: 1/2048\nExported exact rational coefficients for both components.\n',
        code=r'''from fractions import Fraction as Q
from komorebi_browser import show_plot, export_file

# Change these rational scales, retaining 0 < scale < 1.
q, r, a, b = Q(1, 3), Q(2, 3), Q(1, 2), Q(3, 4)
count = 12
if not all(isinstance(s, Q) and Q(0) < s < Q(1) for s in (q, r, a, b)):
    raise ValueError("Use four rational contractions strictly between zero and one.")
if type(count) is not int or not 2 <= count <= 24:
    raise ValueError("Use an integer count between 2 and 24.")

u, v = [Q(1)], [Q(1)]
for n in range(1, count):
    # Only coefficients with index less than n occur in either sum.
    u.append(sum(q**(2*i+1)*r**(2*(n-1-i)+1)*u[i]*v[n-1-i]
                 for i in range(n))/Q(2*n+1))
    v.append(sum(a**(2*i+1)*b**(2*(n-1-i)+1)*u[i]*v[n-1-i]
                 for i in range(n))/Q(2*n+1))

radius = Q(1)
rho = radius**2/2
tail = radius*rho**count/(1-rho)
xs = [j/80 for j in range(-80, 81)]
def polynomial(coefficients, x):
    return sum(float(c)*x**(2*n+1) for n,c in enumerate(coefficients))

show_plot([
    {"x": xs, "y": [polynomial(u,x) for x in xs], "name": "U Taylor polynomial", "mode": "lines"},
    {"x": xs, "y": [polynomial(v,x) for x in xs], "name": "V Taylor polynomial", "mode": "lines", "line": {"dash": "dash"}},
], {"title": {"text": f"Coupled functions: {count} odd coefficients"},
    "xaxis": {"title": {"text": "Real x in [-1, 1]"}},
    "yaxis": {"title": {"text": "Taylor polynomial value"}}},
    description="Two coupled odd Taylor polynomials share initial slope one and separate as x grows. Plotted values are floating-point evaluations. The source geometric majorant bounds the omitted series on the entire complex unit disk; it does not bound plotting roundoff.")

csv = "index,degree,u,v\n"+"".join(
    f"{n},{2*n+1},{u[n]},{v[n]}\n" for n in range(count))
export_file("coupled-special-function-coefficients.csv", csv)
print("Scales (q, r, a, b):", ", ".join(map(str, (q,r,a,b))))
print(f"Coefficients retained per component: {count} (through degree {2*count-1})")
print(f"u_1 = {u[1]}; v_1 = {v[1]}")
print("Uniform omitted-tail envelope on |z| <= 1:", tail)
print("Exported exact rational coefficients for both components.")
'''),
}
