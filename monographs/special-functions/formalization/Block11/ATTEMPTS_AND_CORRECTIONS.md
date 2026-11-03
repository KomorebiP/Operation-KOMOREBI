# Route and implementation record

Target/base: TARGET.md; 1c7814ef551709f44547561fe9b04ff7f9faa505.
Primary route: explicit eventual ratio bounds, real bounded-filter sandwich,
then elementary logarithmic squeeze and actual maximum transport.
Discriminator: a real liminf/limsup sandwich with both boundedness witnesses.
Outcome: proved, including type positivity, the maximum-modulus radial limit
and exact limsup order for both canonical components.

The initial implementation attempted field notation for eventual-equality
liminf/limsup congruence. The pinned API instead uses Filter.liminf_congr
and Filter.limsup_congr; those names were substituted. No hypothesis or
mathematical claim changed. The proof also explicitly constructs the real
spherical supremum and proves nonemptiness before applying csSup equality.
The production module compiled before controls and before the separate
fresh public replay. The first replay stopped at the older CoupledRescaling
audit with std::bad_alloc while available system commit memory was low.
The resource state improved before a new-directory retry. The failed receipt,
all raw logs and a retry memory observation are retained under attempts/;
no failed execution is counted among the accepted run's passing steps.

Four controls reject a missing eventual upper bound, a zero lower
coefficient, confusion between radial and type profiles, and a placeholder.
The positive fixtures include exact radial exponent examples at rho=1 and
rho=1/2, canonical type inequalities and the actual maximum at zero. These
are interface checks; no numerical experiment supports the universal theorem.

Deferred extended-real route: infinity exclusion/conversion remains untried;
resume for unbounded profiles. Deferred little-o route: positivity/nonzero
transport remains untried; resume for sharper asymptotic errors. Neither is
refuted or exhausted. Prior reports retain older alternatives. No delegated
or delayed runs remain. Remaining chapter coverage is assessed separately
in REMAINING_WORK.md with hashed manuscript inputs.
