# Source and dependency check

Primary source inspected: Bergeron, Charollois, Garcia, *Elliptic units for
complex cubic fields*, arXiv:2311.04110v2, 30 November 2023.
https://arxiv.org/html/2311.04110v2

Used implication: the additive gamma product with positive periods, the
negative-first-period continuation, and its logarithmic product expansion in
an absolute convergence strip. The continued fifth-smoothed quantity here is
F(z)=1/S_5(z+t;t,s). The new seven-point norm is derived explicitly from those
products, not imported as a theorem without checked hypotheses.

Also inspected the FHRZ primary gamma-gerbe text,
https://arxiv.org/html/math/0601337v1 . No extra-Eisenstein descent theorem or
arithmetic equality is imported from it. The current work avoids claiming
that arbitrary period translations are scalar automorphy data on the real torus.

Project-local inputs: predecessor v0.11.0 proof/source ZIP and the guarded
Conductor Adapted Taps gamma evaluator, preserved with hashes. They supply
conventions and the previously proved endpoint criterion, not the principal
comparison required to solve the special-value problem.

No novelty search or priority claim was performed.
