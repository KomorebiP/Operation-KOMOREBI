# SF-LEAN-B06 target contract

Base: `433fecf0b21011af7774fa41fde336e788949411` (SF-LEAN-B05).
Authoritative statement: Theorem G.1 in
`monograph/sections_v11/coupled_inverse_full.tex`.

For real labeled scales 0<q,r,a,b<1 and the canonical normalized entire pair,
prove that existence of nonzero complex A,B with V(z)=A U(Bz) for all complex
z is equivalent to D=0, hence to q=b or qb=ar. Complex witnesses must not be
silently restricted to real witnesses in the necessity direction. Also prove
the displayed scalar representation with S=sqrt(k/p)>0 and c=sqrt(S):
U(z)=c T(q,Sr)(z/c), V(z)=c^-1 T(q,Sr)(cz), where the effective scalar
scales are positive strict contractions. Ordinary coefficients are used.

Primary route: extract complex rescaling coefficients through degree five;
construct the displayed pair from the canonical scalar solution, verify its
two equations, and use the existing entire uniqueness theorem. First
discriminators: complex coefficient uniqueness and the scalar rescaling
chain-rule identities. Success requires both directions and the explicit
representation, with all root and contraction premises checked.

Alternatives: prove the scaled coefficient recurrence directly on both
surfaces, or exploit separate equation symmetries on the two surfaces and
derive the scalar representation afterwards. Their first uncertainties are
respectively convolution reindexing and global derivative-comparison APIs.
They remain available if the direct construction stalls. Falsification:
retain the generic nonzero-defect example, distinguish ordinary coefficients
from derivatives, check both surfaces, and try the normalized nonreal candidate
A=-i, B=i against the positive cubic coefficient.

Scope excludes Perron growth, operator decoupling, a stable inverse, full
monograph coverage, and independent review. Update actual source files,
input/output receipts, claim maps, status and continuation files at closeout.
