# B72.4. Explicit unit coordinate at level49

Use Q_A=(A^6-1)/7 mod49, determined by A mod343. Use q0=(C0^6-1)/7 mod7,
determined by C0 mod49. These two precision levels are different.

The logarithm series gives

    log(A^6)/7 = Q_A-(7/2)Q_A^2 mod49.

Terms of order at least3 vanish here. The denominator log(3^6)/7 is27 modulo49,
with inverse20. It follows that

    ell_2(A)=20Q_A+28Q_A^2 mod49.

Also ell_2(5)=29 and d_2=ell_2(5)/2=39 mod49. Substitution in B72.1 yields

    Lambda_2=7ell_2(C0)-3ell_2(A)-3-5*39
            =47+38Q_A+14Q_A^2-7q0 mod49.                 (10)

Thus the actual local period scalar has class

    2epsilon*w[phi]+(47+38Q_A+14Q_A^2-7q0)[3]+7c[7]
                         in H1(F,O_E/49(chi)).          (11)

The formula is exact modulo49 in the Kummer group under the inherited actual period
comparison, not an approximation that drops unknown units of insufficient depth.
In particular C0, which disappeared from the residual formula, returns here.

Two finite methods check(10): a truncated logarithm in an omega basis and a
multiplicative digit-coordinate construction in a phi basis. No coefficient-field
w is substituted for base-field omega. Every rational unit A mod343 and every
rational unit C0 mod49 is covered:294*42=12348 pairs.

The first six values of d_j are

    4,39,284,284,7487,91522    modulo7,49,343,2401,16807,117649.

The finite tables do not extend the analytic precision window beyond7c-1.
