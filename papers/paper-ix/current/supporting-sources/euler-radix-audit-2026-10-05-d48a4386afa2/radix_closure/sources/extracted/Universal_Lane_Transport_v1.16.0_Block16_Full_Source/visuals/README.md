# Supplemental exact phase diagrams

These figures evaluate closed formulas on finite integer grids. They are exact
visualizations, not stochastic simulations.

## Refined figure set

1. prime-power saturation family grid;
2. prime-power visibility landscape;
3. local-channel compression family;
4. Fuss-Catalan gcd compression phase;
5. Fuss-Catalan active-address support family;
6. dominant singularity-orbit size;
7. algebraic packet-degree exponent;
8. rational-collapse obstruction family.

## Large-domain formulas

### Prime-power visibility

For the valuation profile `(0,a,2a,3a)`,

```text
S_a(r) = sum_i max(r - nu_i, 0).
```

### Fuss-Catalan compression

```text
g(N,q) = gcd(N, q-1).
```

The active-address count is `N/g`, and the complete dominant-orbit size is
`(q-1)/g`.

### Algebraic packet degree

For the cyclic-radical family, the exponent governing the degree scale is

```text
e(N,m) = N/gcd(N,m).
```

The high-resolution directory includes both PNG and PDF outputs. Regenerate
with:

```bash
python generate_large_domain_phase_diagrams.py --domain-size 1000 --dpi 500
```
