# Projector-Generated Special Functions VII

## Core formula record

### Positive discrete series

$$
K_0|n\rangle=(n+\kappa)|n\rangle
$$

$$
K_+|n\rangle=\sqrt{(n+1)(n+2\kappa)}|n+1\rangle
$$

$$
K_-|n\rangle=\sqrt{n(n+2\kappa-1)}|n-1\rangle
$$

$$
\mathcal C=K_0(K_0-1)-K_+K_-=\kappa(\kappa-1)I
$$

### Fixed-excitation dimensions

$$
\dim\mathcal H_N^{(m)}=\binom{N+m-1}{m-1}
$$

$$
\dim\mathcal M_N^{(m)}=\binom{N+m-2}{m-2}
$$

### Pair-Casimir spectrum

$$
\lambda_j^{ab}=(\kappa_a+\kappa_b+j)(\kappa_a+\kappa_b+j-1)
$$

### Racah packet matrix

$$
\mathcal R_N^{\boldsymbol\kappa}(j,m)=\langle j,(12)3|m,1(23)\rangle
$$

$$
\mathcal R_N\mathcal R_N^{\mathsf T}=I
$$

### One-excitation closed form

$$
\mathcal R_1^{\boldsymbol\kappa}
=
\begin{pmatrix}
\sqrt{\frac{\kappa_1\kappa_3}{(\kappa_1+\kappa_2)(\kappa_2+\kappa_3)}}
&
\sqrt{\frac{\kappa_2(\kappa_1+\kappa_2+\kappa_3)}{(\kappa_1+\kappa_2)(\kappa_2+\kappa_3)}}
\\
\sqrt{\frac{\kappa_2(\kappa_1+\kappa_2+\kappa_3)}{(\kappa_1+\kappa_2)(\kappa_2+\kappa_3)}}
&
-\sqrt{\frac{\kappa_1\kappa_3}{(\kappa_1+\kappa_2)(\kappa_2+\kappa_3)}}
\end{pmatrix}
$$

### Equal-shape, two-excitation example

$$
\mathcal R_2
=
\begin{pmatrix}
\frac13&\frac1{\sqrt3}&\frac{\sqrt5}{3}
\\
\frac1{\sqrt3}&\frac12&-\frac{\sqrt{15}}6
\\
\frac{\sqrt5}{3}&-\frac{\sqrt{15}}6&\frac16
\end{pmatrix}
$$

### Racah recurrence

$$
b_{j-1}\mathcal R_N(j-1,m)+a_j\mathcal R_N(j,m)+b_j\mathcal R_N(j+1,m)
=
\lambda_m^{23}\mathcal R_N(j,m)
$$

### Bistochastic kernel

$$
P_{jm}=|\mathcal R_N(j,m)|^2
$$

$$
\sum_mP_{jm}=\sum_jP_{jm}=1
$$

$$
H(pP)\ge H(p)
$$

### Four-body pentagon

$$
U_{01}U_{12}U_{23}U_{34}U_{40}=I
$$

### Givens compilation

$$
R=G_1^{\mathsf T}\cdots G_L^{\mathsf T}D
$$

$$
L\le\frac{d(d-1)}2
$$
