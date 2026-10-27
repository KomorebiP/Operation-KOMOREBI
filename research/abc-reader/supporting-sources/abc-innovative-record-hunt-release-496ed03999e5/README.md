# Innovative ABC Record Hunt

This release contains three searches designed to avoid rescanning ordinary integer intervals or merely reproducing the known leading triples.

## Benchmark

The target quality is `1.6299116841270482`, from `2 + 3^10*109 = 23^5`.

## Engine A: hybrid real and p-adic approximation

For a degree `d`, cores `B,C`, a prime power `q^e`, and a Hensel root

`C r^d = B (mod q^e)`,

set `x = r y + q^e t`. Then `t/y` is chosen from continued fractions of

`((B/C)^(1/d)-r)/q^e`.

This simultaneously makes `C x^d-B y^d` small in the real metric and deeply divisible in the `q`-adic metric. The run searched degrees 3 through 8, 48,396 lifted branches, and 1,105,273 convergent states. It formed 505,917 primitive candidates beyond `2^63`.

## Engine B: second-level semiconvergent-ray lifting

A continued-fraction ray is parameterized by

`x(k)=x0+k x1`, `y(k)=y0+k y1`.

CRT conditions force `x(k)` and `y(k)` to contain prescribed prime powers. This searches the arithmetic structure along the ray instead of accepting generic numerator and denominator radicals. The run tested 1,234,978 forced states and formed 488,656 primitive candidates.

## Engine C: triple-forced ray

After forcing prime powers into both endpoints, a third Hensel lift is performed on the residual polynomial

`G(k)=(C x(k)^d-B y(k)^d)/q^e`.

This forces a second deep prime packet into the difference. The pilot processed 115,576 third-level lifts and formed 44,875 primitive candidates.

## Result

No candidate beat the benchmark.

The strongest exact candidate was

`5128164608583279223309 + 552983334912 = 5128164609136262558221`

with quality `1.227458276026612`.

Factorizations:

- `a = 17^13 53^1 9769^1`
- `b = 2^12 3^9 19^3`
- `c = 7^3 149^1 464687^3`

This result is not competitive with the benchmark, but it is structurally informative: adding simultaneous real approximation and several engineered p-adic depth packets still loses when the remaining endpoint or residual support is not closed.

## Main conclusion

The next engine should not add another generic lifting layer. It should solve the residual support polynomial on each promising ray as a Thue–Mahler or polynomial S-unit problem. That is the first step that can turn a large residual from an uncontrolled integer into a finite prescribed-prime support object.

## Claim boundary

The searches are bounded by their documented core, prime, degree, depth, and denominator ranges. No historical novelty is claimed for the displayed candidates, and the absence of a beat is not a global optimality result.
