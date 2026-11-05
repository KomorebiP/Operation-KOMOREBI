# Composition and compatibility laws

[Operator guide](../../OPERATOR_AUDIT.md) · [Catalog](README.md) · [Composition laws](RELATIONS.md) · [Finite checks](CHECKS.md)

These 28 relations connect entries in the catalog. Their assumptions are part of each statement. A linked fixture checks the named finite example, not every admissible instance. The relations include classical identities and explicit consequences of the source constructions.

- [REL-01 · Typed packet composition](#rel-01)
- [REL-02 · Presentation bridge](#rel-02)
- [REL-03 · Coordinate transport](#rel-03)
- [REL-04 · Integration constant](#rel-04)
- [REL-05 · Transported differentiation](#rel-05)
- [REL-06 · Transported product](#rel-06)
- [REL-07 · Gauge complement](#rel-07)
- [REL-08 · Covector pullback](#rel-08)
- [REL-09 · Coarse descent](#rel-09)
- [REL-10 · Coarse defect composition](#rel-10)
- [REL-11 · Metric adjoint](#rel-11)
- [REL-12 · Metric whitening](#rel-12)
- [REL-13 · Metric distortion](#rel-13)
- [REL-14 · Quadratic metric defect](#rel-14)
- [REL-15 · Metric propagation](#rel-15)
- [REL-16 · Holonomy covariance](#rel-16)
- [REL-17 · Raising and lowering](#rel-17)
- [REL-18 · Degree realization](#rel-18)
- [REL-19 · Compositional inversion](#rel-19)
- [REL-20 · Exponential and logarithm](#rel-20)
- [REL-21 · Recurrence coordinates](#rel-21)
- [REL-22 · Finite trace recovery](#rel-22)
- [REL-23 · Pushforward duality](#rel-23)
- [REL-24 · Moment exactness](#rel-24)
- [REL-25 · Fixed-weight derivatives](#rel-25)
- [REL-26 · Integration by parts](#rel-26)
- [REL-27 · Finite Fubini](#rel-27)
- [REL-28 · Recursive filter continuation](#rel-28)

<a id="rel-01"></a>

## REL-01. Typed packet composition

```math
(UT)_{ki}=\sum_j U_{kj}T_{ji}
```

**Assumptions.** One complete aligned intermediate packet system.

**Operators:** [OP-009 Complete algebraic packet projectors](A_STRUCTURAL.md#op-009) · [OP-010 Packet block](A_STRUCTURAL.md#op-010) · [OP-012 Transfer block composition](A_STRUCTURAL.md#op-012).

**Finite checks linked:** [L04](CHECKS.md#l04).

<a id="rel-02"></a>

## REL-02. Presentation bridge

```math
\widehat{UT}=\widehat U R\widehat T
```

**Assumptions.** Exact analysis-synthesis left inverses and the declared middle bridge.

**Operators:** [OP-019 Canonical coefficient lift](A_STRUCTURAL.md#op-019) · [OP-020 Presentation bridge](A_STRUCTURAL.md#op-020).

**Finite checks linked:** [L08](CHECKS.md#l08).

<a id="rel-03"></a>

## REL-03. Coordinate transport

```math
(C_ZUC_Y^{-1})(C_YTC_X^{-1})=C_ZUTC_X^{-1}
```

**Assumptions.** Linear maps $T:X\to Y$ and $U:Y\to Z$, with three invertible coordinate charts $C_X,C_Y,C_Z$. Both factors use the same chart $C_Y$ on the intermediate space.

**Operators:** [OP-008 Similarity transport](A_STRUCTURAL.md#op-008) · [OP-040 Coordinate change](C_COORDINATES.md#op-040) · [OP-171 Two-endpoint coordinate transport](A_STRUCTURAL.md#op-171).

**Finite checks linked:** [R03](CHECKS.md#r03), [R04](CHECKS.md#r04).

<a id="rel-04"></a>

## REL-04. Integration constant

```math
J_aD=I-\mathbf 1 e_a
```

**Assumptions.** Degree-changing derivative and basepoint-zero primitive on polynomial spaces over a $\mathbf Q$-algebra, or where all required integration denominators are units.

**Operators:** [OP-053 Formal derivative](C_COORDINATES.md#op-053) · [OP-054 Basepoint antiderivative](C_COORDINATES.md#op-054) · [OP-057 Integration-constant defect projector](C_COORDINATES.md#op-057).

**Finite checks linked:** [L10](CHECKS.md#l10), [L11](CHECKS.md#l11).

<a id="rel-05"></a>

## REL-05. Transported differentiation

```math
\Delta Q_r=Q_{r-1}\Delta
```

**Assumptions.** Falling-factorial packets with $m\ge1$ and $0\le r<m$. The shifted subscript $r-1$ is read modulo $m$.

**Operators:** [OP-041 Monomial to falling-factorial transport](C_COORDINATES.md#op-041) · [OP-047 Forward finite difference](C_COORDINATES.md#op-047) · [OP-173 Falling-factorial residue projector](C_COORDINATES.md#op-173).

**Finite checks linked:** [R10](CHECKS.md#r10).

<a id="rel-06"></a>

## REL-06. Transported product

```math
\Delta(f\star g)=(\Delta f)\star g+f\star\Delta g
```

**Assumptions.** The transported product, not ordinary pointwise multiplication.

**Operators:** [OP-041 Monomial to falling-factorial transport](C_COORDINATES.md#op-041) · [OP-047 Forward finite difference](C_COORDINATES.md#op-047) · [OP-174 Transported polynomial product](C_COORDINATES.md#op-174).

**Finite checks linked:** [R11](CHECKS.md#r11), [R12](CHECKS.md#r12), [R13](CHECKS.md#r13).

<a id="rel-07"></a>

## REL-07. Gauge complement

```math
G=I-AS,\quad G^2=G,\quad SG=0
```

**Assumptions.** SA=I on physical space.

**Operators:** [OP-018 Canonical coefficient projection](A_STRUCTURAL.md#op-018) · [OP-170 Synthesis-kernel projector](A_STRUCTURAL.md#op-170).

**Finite checks linked:** [R01](CHECKS.md#r01), [R02](CHECKS.md#r02).

<a id="rel-08"></a>

## REL-08. Covector pullback

```math
(\ell A)x=\ell(Ax)
```

**Assumptions.** Typed finite maps.

**Operators:** [OP-172 Covector pullback](C_COORDINATES.md#op-172) · [OP-055 Point evaluation](C_COORDINATES.md#op-055) · [OP-194 Moment integration covector](L_INTEGRATION.md#op-194).

**Finite checks linked:** [R05](CHECKS.md#r05), [R06](CHECKS.md#r06), [R57](CHECKS.md#r57).

<a id="rel-09"></a>

## REL-09. Coarse descent

```math
(\exists!\,\overline T:Y\to Y\text{ linear}:\overline Tq=qT)\iff T(\ker q)\subseteq\ker q
```

**Assumptions.** The map $T:X\to X$ is linear and $q:X\to Y$ is a surjective linear map. Kernel preservation guarantees existence and uniqueness of the induced map; it does not certify an arbitrarily supplied candidate $\overline T$.

**Operators:** [OP-162 Carrier factorization](I_COMPUTATIONAL.md#op-162) · [OP-184 Descended coarse operator](I_COMPUTATIONAL.md#op-184).

**Finite checks linked:** [R37](CHECKS.md#r37), [R38](CHECKS.md#r38).

<a id="rel-10"></a>

## REL-10. Coarse defect composition

```math
E_{UT}=(E_U)T+\overline U E_T
```

**Assumptions.** Use typed maps $T:X\to Y$ and $U:Y\to Z$, observations $q_X,q_Y,q_Z$, and proposed coarse maps $\overline T,\overline U$. Define $E_T=q_YT-\overline Tq_X$, $E_U=q_ZU-\overline Uq_Y$, and $E_{UT}=q_ZUT-(\overline U\overline T)q_X$. The displayed law uses the composed coarse candidate $\overline U\overline T$. An independently proposed $\overline{UT}$ contributes the extra term $(\overline U\overline T-\overline{UT})q_X$.

**Operators:** [OP-121 Semigroup refinement defect](G_DYNAMICS.md#op-121) · [OP-184 Descended coarse operator](I_COMPUTATIONAL.md#op-184).

**Finite checks linked:** [R83](CHECKS.md#r83), [R84](CHECKS.md#r84).

<a id="rel-11"></a>

## REL-11. Metric adjoint

```math
(UT)^\sharp=T^\sharp U^\sharp
```

**Assumptions.** Fixed positive metrics with a common middle metric.

**Operators:** [OP-005 Adjoint operator](A_STRUCTURAL.md#op-005) · [OP-185 Metric adjoint](K_METRICS.md#op-185).

**Finite checks linked:** [R39](CHECKS.md#r39), [R40](CHECKS.md#r40), [R41](CHECKS.md#r41).

<a id="rel-12"></a>

## REL-12. Metric whitening

```math
B_Q(UT)=B_Q(U)B_Q(T)
```

**Assumptions.** Aligned metric factors.

**Operators:** [OP-171 Two-endpoint coordinate transport](A_STRUCTURAL.md#op-171) · [OP-186 Metric-whitened representation](K_METRICS.md#op-186).

**Finite checks linked:** [R42](CHECKS.md#r42), [R43](CHECKS.md#r43).

<a id="rel-13"></a>

## REL-13. Metric distortion

```math
D_Q(UT)\le D_Q(U)D_Q(T)
```

**Assumptions.** Invertible maps between metric spaces of a common finite dimension $n\ge1$, with positive-definite Hermitian metrics and the same metric on the shared intermediate space.

**Operators:** [OP-186 Metric-whitened representation](K_METRICS.md#op-186) · [OP-187 Intrinsic distortion functional](K_METRICS.md#op-187).

**Finite checks linked:** [R44](CHECKS.md#r44), [R45](CHECKS.md#r45), [R46](CHECKS.md#r46).

<a id="rel-14"></a>

## REL-14. Quadratic metric defect

```math
\mathcal E(UT)=\mathcal E(T)+T^*\mathcal E(U)T
```

**Assumptions.** Typed maps and a single intermediate metric.

**Operators:** [OP-189 Conformal metric residual](K_METRICS.md#op-189) · [OP-192 Quadratic metric-defect composition](K_METRICS.md#op-192).

**Finite checks linked:** [R53](CHECKS.md#r53), [R54](CHECKS.md#r54).

<a id="rel-15"></a>

## REL-15. Metric propagation

```math
Q_Z=(UT)^{-*}Q_X(UT)^{-1}
```

**Assumptions.** Invertible edges.

**Operators:** [OP-024 Transported bilinear form](A_STRUCTURAL.md#op-024) · [OP-191 Metric propagation along an edge](K_METRICS.md#op-191).

**Finite checks linked:** [R48](CHECKS.md#r48), [R49](CHECKS.md#r49).

<a id="rel-16"></a>

## REL-16. Holonomy covariance

```math
\mathcal H_{g^{-*}Qg^{-1}}(gHg^{-1})=\mathcal H_Q(H)
```

**Assumptions.** Both metric and holonomy are transported.

**Operators:** [OP-024 Transported bilinear form](A_STRUCTURAL.md#op-024) · [OP-190 Metric holonomy residual](K_METRICS.md#op-190).

**Finite checks linked:** [R50](CHECKS.md#r50), [R51](CHECKS.md#r51).

<a id="rel-17"></a>

## REL-17. Raising and lowering

```math
[\Delta,R]=I
```

**Assumptions.** Polynomial ring. In the degree-$d$ square truncation in the falling-factorial basis, $[\Delta_d,R_d]=I-(d+1)E_d$, where $E_d$ projects onto the top basis vector. The boundary term can vanish in characteristic dividing $d+1$.

**Operators:** [OP-047 Forward finite difference](C_COORDINATES.md#op-047) · [OP-175 Falling-factorial raising operator](C_COORDINATES.md#op-175).

**Finite checks linked:** [R14](CHECKS.md#r14), [R15](CHECKS.md#r15), [R16](CHECKS.md#r16).

<a id="rel-18"></a>

## REL-18. Degree realization

```math
\mathcal N x^{\underline k}=k x^{\underline k}
```

**Assumptions.** Interpolation additionally needs unit eigenvalue differences.

**Operators:** [OP-173 Falling-factorial residue projector](C_COORDINATES.md#op-173) · [OP-176 Falling-factorial degree operator](C_COORDINATES.md#op-176).

**Finite checks linked:** [R17](CHECKS.md#r17), [R18](CHECKS.md#r18).

<a id="rel-19"></a>

## REL-19. Compositional inversion

```math
\phi\circ\psi=\psi\circ\phi=z\pmod {z^{N+1}}
```

**Assumptions.** Zero constant coefficient and unit linear term.

**Operators:** [OP-060 Formal composition operator](C_COORDINATES.md#op-060) · [OP-177 Formal compositional inversion](C_COORDINATES.md#op-177).

**Finite checks linked:** [R19](CHECKS.md#r19), [R20](CHECKS.md#r20).

<a id="rel-20"></a>

## REL-20. Exponential and logarithm

```math
\operatorname{Log}(\operatorname{Exp}u)=u
```

**Assumptions.** Commutative Q-algebra with zero-constant u, or guarded finite analog.

**Operators:** [OP-066 Formal logarithm operator](C_COORDINATES.md#op-066) · [OP-203 Formal exponential](C_COORDINATES.md#op-203).

**Finite checks linked:** [R21](CHECKS.md#r21), [R22](CHECKS.md#r22), [R23](CHECKS.md#r23).

<a id="rel-21"></a>

## REL-21. Recurrence coordinates

```math
\operatorname{synth}(a_0,\ldots,a_{d-1},\delta)=a
```

**Assumptions.** Every required defect is retained.

**Operators:** [OP-063 Recurrence companion transfer](C_COORDINATES.md#op-063) · [OP-064 Recurrence defect extraction](C_COORDINATES.md#op-064) · [OP-178 Recurrence reconstruction](C_COORDINATES.md#op-178).

**Finite checks linked:** [R26](CHECKS.md#r26), [R27](CHECKS.md#r27).

<a id="rel-22"></a>

## REL-22. Finite trace recovery

```math
R_AAm=m
```

**Assumptions.** Full column rank and compatible finite trace data.

**Operators:** [OP-181 Finite trace observation](J_REPRESENTATIONS.md#op-181) · [OP-182 Trace-table reconstruction](J_REPRESENTATIONS.md#op-182).

**Finite checks linked:** [R32](CHECKS.md#r32), [R33](CHECKS.md#r33), [R34](CHECKS.md#r34), [R35](CHECKS.md#r35).

<a id="rel-23"></a>

## REL-23. Pushforward duality

```math
I_{\phi_*\mu}f=I_\mu(f\circ\phi)
```

**Assumptions.** Finite atomic or stated exact affine setting.

**Operators:** [OP-172 Covector pullback](C_COORDINATES.md#op-172) · [OP-193 Atomic integration functional](L_INTEGRATION.md#op-193) · [OP-195 Finite measure pushforward](L_INTEGRATION.md#op-195).

**Finite checks linked:** [R58](CHECKS.md#r58), [R59](CHECKS.md#r59), [R69](CHECKS.md#r69), [R70](CHECKS.md#r70).

<a id="rel-24"></a>

## REL-24. Moment exactness

```math
\mathcal E(p)=\sum_\alpha c_\alpha r_\alpha
```

**Assumptions.** Every basis moment in the selected polynomial space.

**Operators:** [OP-194 Moment integration covector](L_INTEGRATION.md#op-194) · [OP-197 Signed quadrature functional](L_INTEGRATION.md#op-197) · [OP-198 Moment discrepancy functional](L_INTEGRATION.md#op-198).

**Finite checks linked:** [R62](CHECKS.md#r62), [R63](CHECKS.md#r63), [R65](CHECKS.md#r65).

<a id="rel-25"></a>

## REL-25. Fixed-weight derivatives

```math
D^r\sum_jw_jF_j=\sum_jw_jD^rF_j
```

**Assumptions.** Weights and integration data independent of the differentiated variable.

**Operators:** [OP-102 Directional derivative](F_NONLINEAR.md#op-102) · [OP-199 Fixed-weight derivative averaging](L_INTEGRATION.md#op-199).

**Finite checks linked:** [R66](CHECKS.md#r66), [R67](CHECKS.md#r67).

<a id="rel-26"></a>

## REL-26. Integration by parts

```math
I(fg')+I(f'g)=\rho[fg]_a^b
```

**Assumptions.** Polynomials and constant density.

**Operators:** [OP-053 Formal derivative](C_COORDINATES.md#op-053) · [OP-056 Interval integration functional](C_COORDINATES.md#op-056) · [OP-200 Integration-by-parts boundary functional](L_INTEGRATION.md#op-200).

**Finite checks linked:** [R68](CHECKS.md#r68).

<a id="rel-27"></a>

## REL-27. Finite Fubini

```math
I_\mu^{(x)}I_\nu^{(y)}p=I_{\mu\otimes\nu}p
```

**Assumptions.** Declared product measure.

**Operators:** [OP-194 Moment integration covector](L_INTEGRATION.md#op-194) · [OP-196 Partial integration on a product](L_INTEGRATION.md#op-196).

**Finite checks linked:** [R60](CHECKS.md#r60), [R61](CHECKS.md#r61).

<a id="rel-28"></a>

## REL-28. Recursive filter continuation

```math
\operatorname{run}(x_1x_2,s_0)=(y_1y_2,s_2),\quad \operatorname{run}(x_i,s_{i-1})=(y_i,s_i)
```

**Assumptions.** Outputs are concatenated and full continuation state retained.

**Operators:** [OP-063 Recurrence companion transfer](C_COORDINATES.md#op-063) · [OP-205 Causal recursive filter](E_SIGNAL.md#op-205).

**Finite checks linked:** [R73](CHECKS.md#r73), [R74](CHECKS.md#r74), [R75](CHECKS.md#r75), [R76](CHECKS.md#r76), [R77](CHECKS.md#r77), [R85](CHECKS.md#r85).
