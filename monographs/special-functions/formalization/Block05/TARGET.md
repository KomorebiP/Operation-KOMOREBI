# SF-LEAN-B05 target contract

Base checkpoint: `ee59ff257a74fc046981e5ca633476148fe2e1a4`.

For labeled positive real tuples s,t with every scale strictly below one and
s.defect nonzero, equality near zero of both canonical complex functions U and V
must imply s=t. This is the analytic-germ implication in Theorem G.2. Equality
of only a fixed tuple's solutions is insufficient. All coefficients are ordinary
power-series coefficients at odd degrees 2n+1, with zero coefficients at even
degrees. No factorial normalization is silently introduced.

Primary route: embed the odd sums as dense scalar formal multilinear series,
use uniqueness of a convergent power series from equality of germs, and invoke
Block01's inverse. First discriminator: a checked HasSum reindexing along
n -> 2n+1 and a HasFPowerSeriesAt bridge. Success means complete kernel-checked
coefficient extraction and the guarded parameter inverse.

Alternative routes: iterated derivatives (first unresolved implication is
locally uniform convergence for each differentiated series), or leading-term
asymptotics (first unresolved implication is a tail estimate isolating the first
different coefficient). Both remain deferred while the scalar-series route is
executable. Falsification checks retain the explicit exceptional-locus jet
collision and test parity, labels, and ordinary-series normalization.

Scope excludes full-monograph analytic coverage, Perron growth, component
rescaling, and an independent review. This block receives a separate self-review.
