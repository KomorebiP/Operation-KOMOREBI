# B78.4. The true remaining Selmer problem is ramification-restricted and geometric

Block 77 proposed computing an affine localization image. B78.2 shows that the
unrestricted finite localization maps for both tangent modules are already
surjective. Therefore a finite collection of local cohomology classes cannot be
the source of a contradiction.

The remaining object must remember at least one of the following pieces of
information that unrestricted H^1 forgets:

1. **ramification support**: the correction must be unramified away from places
   where the actual Frey representation/reference can differ;
2. **Frey conductor coupling**: new ramification must arise from an actual prime
   divisor of the Diophantine data and satisfy the corresponding toric/period
   geometry;
3. **global integral frame**: local representatives cannot be independently
   changed if a condition is genuinely frame-sensitive rather than a strict
   equivalence invariant;
4. **higher integral precision**: the mod-343 tame lifting equations can reject
   trace-invisible corrections after the mod-49 cohomology class has been
   matched.

For a fixed finite set Sigma, the correct replacement is therefore a restricted
Selmer localization

    H^1(G_(K,Sigma),A) -> direct-sum_(v in Sigma)
                           H^1(K_v,A)/L_v,

not the unrestricted H^1(K,A) map. Its cokernel is controlled by a dual Selmer
group through Poitou-Tate duality. But the present bounded beta patterns do not
bound every prime where the p or q corrections may ramify: additional divisors
of C at which beta is unramified have always been permitted.

Thus an actual closure needs either

- a proved bound/control on the full Frey ramification set,
- a support-uniform geometric condition on beta-unramified bad primes, or
- a global integral relation that couples all such places without introducing
  free auxiliary ramification.

This is the precise point where the cohomological flexibility theorem stops.
