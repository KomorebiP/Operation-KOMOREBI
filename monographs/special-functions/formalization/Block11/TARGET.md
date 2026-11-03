# SF-LEAN-B11 target contract

Base: `1c7814ef551709f44547561fe9b04ff7f9faa505` (SF-LEAN-B10).
Authority: Theorem F.2 and the stated type convention in
`monograph/sections_v11/coupled_growth_full.tex`, lines 159-197 and 348-350.

For the actual canonical pair with 0<q,r,a,b<1, define real lower and upper
types as the atTop liminf/limsup of log(F_i(R))/R^rho, where rho is the
positive characteristic exponent. Prove the explicit positive lower bound,
lower-type <= upper-type, and the finite explicit upper bound, using the
actual constants from Blocks09-10. Supply all eventual boundedness and
coboundedness premises. Prove
Tendsto (fun R => log(log(F_i(R)))/log(R)) atTop (nhds rho), and identify
its real limsup with rho. Transport to the norm profile already proved to
be the attained spherical maximum in Block08. This completes the registered
canonical F.2 growth contract; it does not close F.3 or the monograph.

Primary route: eventual two-sided ratio bounds -> real filter type bounds;
take logarithms of positive comparisons and squeeze the radial exponent
between rho+log(c_lower)/log(R) and rho+log(c_upper)/log(R).
First discriminator: the generic real liminf/limsup sandwich with explicit
bounded/cobounded premises. Success requires exact functions, all real
contraction parameters, valid logarithm domains and atTop limits.

Alternative extended-real route: prove bounds in EReal then convert back;
first uncertainty is excluding infinities and reconciling real definitions.
Defer if the real route works; resume for more general unbounded profiles.
Alternative asymptotic route: use logarithmic little-o equivalence directly;
first uncertainty is its positivity/nonzero-domain transport. Defer if the
elementary squeeze works; resume for sharper asymptotic errors.

Controls distinguish a radial exponent limit from convergence of the type
ratio, retain positive comparison/logarithm domains, and reject placeholders.
Record a source-based inventory of what remains, update actual I/O and the
catalogue, and preserve earlier blocks, manuscripts, guides and reading PDFs.
Review provenance is self-review; no delegation is authorized.
