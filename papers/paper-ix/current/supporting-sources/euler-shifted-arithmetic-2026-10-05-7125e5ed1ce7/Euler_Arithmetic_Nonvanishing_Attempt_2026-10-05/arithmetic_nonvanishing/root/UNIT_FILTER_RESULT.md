# The leading-unit-only exclusion fails on an actual index

Base checkpoint: `Euler-coupled-stationarity-20261005`.

The earlier necessary singularity conditions require

    E=2r-25, v2(Phi_r(0))=E, Phi_r(0)/2^E=15 mod32.

We tested the stronger candidate that actual Bernoulli coefficients forbid
the combination of odd critical-value valuation and leading unit15mod32,
without first enforcing the index-dependent equality of the valuation to E.
That candidate is false.

Take the ordinary integer

    T=22831001499602523078606181325,
    B=17659+2^18 T,
    r=B2^640-161.

The actual carry minimum is mu=-154 with true terminal161. The complete
actual packet reconstruction at320 global bits, on x=10202+2^15Z with
content178 removed, gives

    v2(Phi_r(0))=91,
    Phi_r(0)/2^91=56399 mod65536,

so the leading unit is15mod32. The actual undepleted critical value has the
same result because its difference from the depleted value has exact
valuation2r-25, beyond the142 local value bits retained here.

This is a NONZERO critical value, not a counterexample to Euler simplicity.
It violates the necessary valuation equality91=2r-25 by an enormous margin.
The calculation shows precisely why the link between the cancellation depth
and the ordinary index r cannot be discarded in an arithmetic exclusion.

The parameter was chosen by solving the finite model equations

    H0(Z)+T H1(Z)=B(T)*15*2^91 mod2^96,
    (H0'(Z)+T H1'(Z))/2=0 mod2^96.

All four binary successors were checked at each step and exactly one
survived. A separate reconstruction from the resulting ordinary index then
checked the actual packets, the true terminal and the critical point through
141 bits. It retained83 nonzero packets, with a proved scalar cutoff286.
The normalized second derivative has exact valuation1.

The replayable script is `unit_filter_discriminator.py`. Its contract and
pinned run are `unit_filter_contract.json` and `unit_filter_run/`.
The computation uses the audited inherited packet engine; choosing the
parameter from the affine model and verifying it from the ordinary index are
separate paths, but this is not a wholly new Bernoulli implementation.

Development record: the first runner invocation omitted its explicit
`--input` arguments and was rejected before executing the experiment.
The corrected invocation pinned the script, model, packet code and three
vendor modules; it completed and its manifest validated. No failed or
unexecuted run is counted as evidence.
