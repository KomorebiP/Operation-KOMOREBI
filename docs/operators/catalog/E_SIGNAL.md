# Signal, wavelet, and polyphase operators

[Operator guide](../../OPERATOR_AUDIT.md) · [Catalog](README.md) · [Composition laws](RELATIONS.md) · [Worked calculations](../COMPOSITION.md) · [Finite checks](CHECKS.md)

Analyze and synthesize signals, route filter phases, preserve continuation state, and recover finite features.

The 24 entries below retain their stable catalog identifiers. A finite check may concern a single example or a failure of an omitted hypothesis. Use each entry’s scope when interpreting its formula.

## In this family

- [OP-079 · Phase analysis operator](#op-079)
- [OP-080 · Phase synthesis operator](#op-080)
- [OP-081 · Causal FIR convolution](#op-081)
- [OP-082 · Polyphase convolution matrix](#op-082)
- [OP-083 · Filter cascade operator](#op-083)
- [OP-084 · Haar average and detail](#op-084)
- [OP-085 · Haar synthesis](#op-085)
- [OP-086 · Multilevel Haar packet tree](#op-086)
- [OP-087 · Lifting predict update](#op-087)
- [OP-088 · Packet retention projector](#op-088)
- [OP-089 · Signal residual operator](#op-089)
- [OP-090 · Discrete Fourier transform](#op-090)
- [OP-091 · Discrete cosine transform](#op-091)
- [OP-092 · Walsh–Hadamard transform](#op-092)
- [OP-093 · Short-time Fourier analysis](#op-093)
- [OP-094 · Short-time Fourier synthesis](#op-094)
- [OP-095 · Canonical dual window](#op-095)
- [OP-096 · FFT overlap-add convolution](#op-096)
- [OP-097 · Rational polyphase resampling](#op-097)
- [OP-098 · Adaptive filter weight update](#op-098)
- [OP-099 · Wavelet coefficient shrinkage](#op-099)
- [OP-100 · Truncated-power packet realization](#op-100)
- [OP-101 · Finite jump recovery](#op-101)
- [OP-205 · Causal recursive filter](#op-205)

<a id="op-079"></a>

## OP-079. Phase analysis operator

**Kind:** linear.

```math
(\mathcal A_Nx)_r[k]=x[Nk+r]
```

**Scope.** Finite discrete signals, explicitly indexed length

**Sources:** [S: Production finite signal processing](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/PRODUCTION_SIGNAL_PROCESSING.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [WP: Wavelet polyphase worked derivation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/WAVELET_POLYPHASE.md).

**Finite checks linked:** [L12](CHECKS.md#l12).

**Related entries:** [OP-080](E_SIGNAL.md#op-080) · [OP-097](E_SIGNAL.md#op-097).


<a id="op-080"></a>

## OP-080. Phase synthesis operator

**Kind:** linear.

```math
(\mathcal S_N(x^{(r)}))_{Nk+r}=x^{(r)}_k
```

**Scope.** Compatible phase lengths; inverse interleaving

**Sources:** [S: Production finite signal processing](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/PRODUCTION_SIGNAL_PROCESSING.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [WP: Wavelet polyphase worked derivation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/WAVELET_POLYPHASE.md).

**Finite checks linked:** [L12](CHECKS.md#l12).

**Related entries:** [OP-079](E_SIGNAL.md#op-079) · [OP-097](E_SIGNAL.md#op-097).


<a id="op-081"></a>

## OP-081. Causal FIR convolution

**Kind:** linear.

```math
(H_hx)_n=\sum_{\ell\ge0}h_\ell x_{n-\ell}
```

**Scope.** Finite causal taps with zero-extension boundary convention

**Sources:** [S: Production finite signal processing](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/PRODUCTION_SIGNAL_PROCESSING.md) · [P: Polyphase route packets](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/POLYPHASE_ROUTE_PACKETS.md).

**Finite checks linked:** [A34](CHECKS.md#a34), [L12](CHECKS.md#l12).

**Related entries:** [OP-082](E_SIGNAL.md#op-082) · [OP-083](E_SIGNAL.md#op-083) · [OP-097](E_SIGNAL.md#op-097) · [OP-152](I_COMPUTATIONAL.md#op-152) · [OP-205](E_SIGNAL.md#op-205).


<a id="op-082"></a>

## OP-082. Polyphase convolution matrix

**Kind:** linear.

```math
E_h[i,j][q]=h[Nq+i-j]
```

**Scope.** Finite FIR, additive carrier, fixed phase ordering

**Sources:** [P: Polyphase route packets](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/POLYPHASE_ROUTE_PACKETS.md) · [WP: Wavelet polyphase worked derivation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/WAVELET_POLYPHASE.md).

**Finite checks linked:** [A34](CHECKS.md#a34), [L12](CHECKS.md#l12).

**Related entries:** [OP-081](E_SIGNAL.md#op-081) · [OP-083](E_SIGNAL.md#op-083).


<a id="op-083"></a>

## OP-083. Filter cascade operator

**Kind:** linear signal action; bilinear filter cascade.

```math
E_{g*h}=E_gE_h
```

**Scope.** Matrix multiplication with lag-kernel convolution entries

**Keep in view.** The represented cascade is linear on input signals, but bilinear in the two filters.

**Sources:** [P: Polyphase route packets](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/POLYPHASE_ROUTE_PACKETS.md).

**Finite checks linked:** [A34](CHECKS.md#a34).

**Related entries:** [OP-012](A_STRUCTURAL.md#op-012) · [OP-081](E_SIGNAL.md#op-081) · [OP-082](E_SIGNAL.md#op-082).


<a id="op-084"></a>

## OP-084. Haar average and detail

**Kind:** linear.

```math
(a,d)=((x_0+x_1)/2,(x_0-x_1)/2)
```

**Scope.** One finite pair with defined normalization

**Sources:** [WP: Wavelet polyphase worked derivation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/WAVELET_POLYPHASE.md) · [S: Production finite signal processing](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/PRODUCTION_SIGNAL_PROCESSING.md).

**Finite checks linked:** [A37](CHECKS.md#a37), [L16](CHECKS.md#l16).

**Related entries:** [OP-085](E_SIGNAL.md#op-085) · [OP-086](E_SIGNAL.md#op-086) · [OP-087](E_SIGNAL.md#op-087).


<a id="op-085"></a>

## OP-085. Haar synthesis

**Kind:** linear.

```math
(x_0,x_1)=(a+d,a-d)
```

**Scope.** Inverse of preceding pair analysis

**Sources:** [WP: Wavelet polyphase worked derivation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/WAVELET_POLYPHASE.md) · [S: Production finite signal processing](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/PRODUCTION_SIGNAL_PROCESSING.md).

**Finite checks linked:** [A37](CHECKS.md#a37), [L16](CHECKS.md#l16).

**Related entries:** [OP-084](E_SIGNAL.md#op-084) · [OP-087](E_SIGNAL.md#op-087).


<a id="op-086"></a>

## OP-086. Multilevel Haar packet tree

**Kind:** linear.

```math
W_{\mathcal F}x=(\text{packet coefficients at the fixed frontier }\mathcal F)
```

**Scope.** Finite dyadic signal with a fixed complete leaf frontier, or declared nonredundant wavelet coordinates. All-node storage is a redundant analysis map, not a square invertible transform.

**Keep in view.** A complete fixed leaf frontier gives square reconstruction coordinates. Storing every internal node as well produces redundant coordinates and requires a declared synthesis map.

**Sources:** [S: Production finite signal processing](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/PRODUCTION_SIGNAL_PROCESSING.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-084](E_SIGNAL.md#op-084) · [OP-088](E_SIGNAL.md#op-088).


<a id="op-087"></a>

## OP-087. Lifting predict update

**Kind:** linear.

```math
(e,o)\mapsto(e,o-Pe)\mapsto(e+U(o-Pe),o-Pe)
```

**Scope.** Fixed linear finite prediction P and update U with compatible dimensions and declared boundary policy.

**Keep in view.** The lifting steps remain invertible for some nonlinear predictors, but the linear label here requires linear fixed P and U.

**Sources:** [S: Production finite signal processing](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/PRODUCTION_SIGNAL_PROCESSING.md) · [WP: Wavelet polyphase worked derivation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/WAVELET_POLYPHASE.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-084](E_SIGNAL.md#op-084) · [OP-085](E_SIGNAL.md#op-085).


<a id="op-088"></a>

## OP-088. Packet retention projector

**Kind:** linear.

```math
R_K(c)_j=\mathbf1_{j\in K}c_j
```

**Scope.** Fixed retained coefficient set K. Any data-dependent rule for choosing K is separate.

**Keep in view.** A fixed mask is linear. Selecting the retained set from the signal, as in thresholding or best-basis search, is generally nonlinear.

**Sources:** [S: Production finite signal processing](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/PRODUCTION_SIGNAL_PROCESSING.md) · [WP: Wavelet polyphase worked derivation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/WAVELET_POLYPHASE.md).

**Finite checks linked:** [A36](CHECKS.md#a36).

**Related entries:** [OP-086](E_SIGNAL.md#op-086) · [OP-089](E_SIGNAL.md#op-089).


<a id="op-089"></a>

## OP-089. Signal residual operator

**Kind:** linear.

```math
x\mapsto x-W^{-1}R_KWx
```

**Scope.** Fixed invertible finite transform W and fixed K. For a redundant frame use I-S R_K A instead.

**Keep in view.** A square invertible W and fixed retention set are required. Redundant analysis uses synthesis maps instead of W inverse.

**Sources:** [WP: Wavelet polyphase worked derivation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/f49e00d6088bbc8dca4f8a3a70b232db1eea085b/docs/demonstrations/WAVELET_POLYPHASE.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-021](A_STRUCTURAL.md#op-021) · [OP-088](E_SIGNAL.md#op-088).


<a id="op-090"></a>

## OP-090. Discrete Fourier transform

**Kind:** linear.

```math
\widehat x_k=\sum_{n=0}^{N-1}x_ne^{-2\pi i kn/N}
```

**Scope.** Complex vectors of fixed length N>=1. The inverse uses the opposite Fourier sign and divides by N.

**Keep in view.** The inverse carries 1/N in this unnormalized forward convention.

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-040](C_COORDINATES.md#op-040) · [OP-153](I_COMPUTATIONAL.md#op-153).


<a id="op-091"></a>

## OP-091. Discrete cosine transform

**Kind:** linear.

```math
y_k=\alpha_k\sum_{n=0}^{N-1}x_n\cos\!\left(\frac{\pi}{N}(n+\tfrac12)k\right)
```

**Scope.** Real length N vectors. alpha_0=1/sqrt(N), alpha_k=sqrt(2/N) for k>0. Other library normalizations must be translated explicitly.

**Keep in view.** The former name-only formula is replaced by one declared orthonormal DCT-II convention.

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-040](C_COORDINATES.md#op-040) · [OP-166](I_COMPUTATIONAL.md#op-166).


<a id="op-092"></a>

## OP-092. Walsh–Hadamard transform

**Kind:** linear.

```math
x\mapsto H_{2^m}x
```

**Scope.** Finite length N=2^m with H_N H_N^T=N I. Divide by N for the inverse, or use H_N/sqrt(N) for orthonormal coordinates.

**Keep in view.** An unnormalized Hadamard matrix is not its own inverse without division by dimension.

**Sources:** [C: General coordinate atlas](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/GENERAL_COORDINATE_ATLAS.md) · [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-040](C_COORDINATES.md#op-040).


<a id="op-093"></a>

## OP-093. Short-time Fourier analysis

**Kind:** linear.

```math
(V_gx)_{m,k}=\sum_{n=0}^{L-1}x[mh+n]\overline{g[n]}\,e^{-2\pi i kn/N}
```

**Scope.** Fixed window, hop h, frame length L, FFT length N>=L and extension rule. Real-window implementations are a specialization.

**Keep in view.** This displayed convention conjugates g. An implementation that multiplies by w has the same action when w=conj(g); window and Fourier conventions must be matched explicitly.

**Sources:** [S: Production finite signal processing](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/PRODUCTION_SIGNAL_PROCESSING.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-094](E_SIGNAL.md#op-094).


<a id="op-094"></a>

## OP-094. Short-time Fourier synthesis

**Kind:** linear.

```math
S=(A^*A)^{-1}A^*,\qquad SA=I
```

**Scope.** Finite full-column-rank analysis map $A$ on retained samples. For a full-bin STFT, $A^*A$ is diagonal with overlap weights times the chosen FFT scale. One-sided coordinates need the corresponding real-space weighting.

**Keep in view.** Perfect-reconstruction synthesis is not generally the raw adjoint. Overlap normalization is an operator inverse on covered coordinates.

**Sources:** [S: Production finite signal processing](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/PRODUCTION_SIGNAL_PROCESSING.md).

**Finite checks linked:** [A35](CHECKS.md#a35), [R71](CHECKS.md#r71).

**Related entries:** [OP-016](A_STRUCTURAL.md#op-016) · [OP-017](A_STRUCTURAL.md#op-017) · [OP-093](E_SIGNAL.md#op-093) · [OP-095](E_SIGNAL.md#op-095) · [OP-202](A_STRUCTURAL.md#op-202).


<a id="op-095"></a>

## OP-095. Canonical dual window

**Kind:** nonlinear.

```math
g\mapsto g_{\mathrm{dual}}
```

**Scope.** Fixed finite frame geometry and strictly positive overlap weights on reconstructed samples. Zero overlap must be rejected or the reconstruction domain restricted.

**Keep in view.** Window dualization depends nonlinearly on its input window and may fail at an uncovered sample.

**Sources:** [S: Production finite signal processing](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/PRODUCTION_SIGNAL_PROCESSING.md).

**Finite checks linked:** [A35](CHECKS.md#a35).

**Related entries:** [OP-094](E_SIGNAL.md#op-094).


<a id="op-096"></a>

## OP-096. FFT overlap-add convolution

**Kind:** linear.

```math
x\mapsto\sum_j\operatorname{shift}_{jH}(x_j*h)
```

**Scope.** Finite blocks with declared overlap and padding

**Sources:** [S: Production finite signal processing](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/PRODUCTION_SIGNAL_PROCESSING.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-205](E_SIGNAL.md#op-205).


<a id="op-097"></a>

## OP-097. Rational polyphase resampling

**Kind:** linear.

```math
R_{u,d}=\downarrow_d H\uparrow_u
```

**Scope.** Fixed integer factors u,d and fixed FIR. The implementation also declares delay compensation, crop and boundary extension. Data-adaptive filter design is not included in the linear map.

**Keep in view.** The algebraic core is linear for a fixed filter. Exact output length, delay correction and cropping belong to the contract.

**Sources:** [S: Production finite signal processing](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/PRODUCTION_SIGNAL_PROCESSING.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.

**Related entries:** [OP-079](E_SIGNAL.md#op-079) · [OP-080](E_SIGNAL.md#op-080) · [OP-081](E_SIGNAL.md#op-081).


<a id="op-098"></a>

## OP-098. Adaptive filter weight update

**Kind:** nonlinear.

```math
w_{n+1}=w_n+\mu e_nx_n
```

**Scope.** Real input x_n and real error e_n with fixed step size mu. Numerical stability is not implied by the formula.

**Keep in view.** This representative is the real LMS update. Complex LMS requires a conjugation convention.

**Sources:** [S: Production finite signal processing](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/PRODUCTION_SIGNAL_PROCESSING.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.


<a id="op-099"></a>

## OP-099. Wavelet coefficient shrinkage

**Kind:** nonlinear.

```math
c\mapsto\operatorname{sgn}(c)\max(|c|-\tau,0)
```

**Scope.** Real coefficient c and fixed tau>=0. Complex coefficients require the separately specified radial formula.

**Keep in view.** The scalar sign formula is for real coefficients. Complex soft thresholding uses a radial extension.

**Sources:** [S: Production finite signal processing](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/PRODUCTION_SIGNAL_PROCESSING.md).

**Finite checks linked:** [A36](CHECKS.md#a36).


<a id="op-100"></a>

## OP-100. Truncated-power packet realization

**Kind:** linear.

```math
\sum_jc_j(x-\tau_j)_+^k
```

**Scope.** Fixed finite knots tau_j and degree k, linear synthesis in coefficients c_j. A positive-part convention is required at k=0.

**Keep in view.** Linearity holds in amplitudes for fixed knots and degrees, not jointly in knot locations.

**Sources:** [A: Komorebi Math API inventory](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/API_INVENTORY.md) · [S: Production finite signal processing](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/PRODUCTION_SIGNAL_PROCESSING.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.


<a id="op-101"></a>

## OP-101. Finite jump recovery

**Kind:** algorithmic.

```math
\text{samples}\mapsto\text{estimated jumps and residuals}
```

**Scope.** Separation/noise assumptions must be declared for recovery guarantees

**Sources:** [S: Production finite signal processing](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/PRODUCTION_SIGNAL_PROCESSING.md) · [U: Unified executable language](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/UNIFIED_LANGUAGE.md).

**Evidence:** Source entry. No finite fixture is assigned in this catalog.


<a id="op-205"></a>

## OP-205. Causal recursive filter

**Kind:** linear with zero initial state.

```math
y_n=\frac{\sum_{k=0}^{M}b_kx_{n-k}-\sum_{k=1}^{L}a_ky_{n-k}}{a_0}
```

**Scope.** Fixed finite coefficients with $a_0$ invertible and a declared input/output prehistory. Finite output is computed recursively.

**Keep in view.** Nonzero fixed continuation state makes the input-to-output map affine. Carrying that state is necessary for chunk equivalence. A finite run does not prove stability.

**Source relationship.** Explicit source construction.

**Sources:** [S: Production finite signal processing](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/PRODUCTION_SIGNAL_PROCESSING.md).

**Finite checks linked:** [R73](CHECKS.md#r73), [R74](CHECKS.md#r74), [R75](CHECKS.md#r75), [R76](CHECKS.md#r76), [R77](CHECKS.md#r77), [R85](CHECKS.md#r85).

**Related entries:** [OP-063](C_COORDINATES.md#op-063) · [OP-081](E_SIGNAL.md#op-081) · [OP-096](E_SIGNAL.md#op-096) · [OP-133](G_DYNAMICS.md#op-133) · [OP-178](C_COORDINATES.md#op-178).

**Composition laws:** [Recursive filter continuation](RELATIONS.md#rel-28).

**Worked calculation:** [Continue a recursive filter across chunks](../COMPOSITION.md#filter-state).

[All operator families](README.md) · [Operator guide](../../OPERATOR_AUDIT.md)
