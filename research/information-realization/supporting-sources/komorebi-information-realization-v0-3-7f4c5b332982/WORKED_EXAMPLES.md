# Worked examples
## From a real packet implementation to an information-repair certificate

**Version 0.3.0 · 15 October 2026**

Run `python examples/worked_examples_v03.py` from the extracted package. It uses the retained Komorebi Math wheel, checks the formulas, and writes `reports/worked_examples_v03.json`. The original seven examples remain in `prior_v0_2/WORKED_EXAMPLES.md`.

## 1. Predicting shifted coarse packets without reconstructing the source

### The actual packet transform

For a four-coordinate source, the existing unnormalized Haar code returns two leaves. Leaf `0` contains the two sums, and leaf `1` contains the two details:

\[
s_0=x_0+x_1,\quad s_1=x_2+x_3,\quad
d_0=x_0-x_1,\quad d_1=x_2-x_3.
\]

We export this integer transform to F_5. All divisions below are field divisions, so 1/2=3. The underlying shift is

\[
T(x_0,x_1,x_2,x_3)=(x_1,x_2,x_3,x_0).
\]

The decoder sees only (s_0,s_1). It does not see the original source or a full packet-tree object. The task is to determine the *next* coarse output, not the entire source.

Substituting the inverse sum/difference formulas gives

\[
s'_0=\frac{s_0+s_1-d_0+d_1}{2},\qquad
s'_1=\frac{s_0+s_1+d_0-d_1}{2}.
\]

The hidden details enter through the rank-one block

\[
B_{oz}=\frac12\begin{bmatrix}-1&1\\1&-1\end{bmatrix}.
\]

The decoder therefore lacks just one independent field coordinate for this task. Under a uniform source:

\[
K=5,\quad H=\log_2 5,\quad E=4/5.
\]

One five-symbol supplement is necessary and sufficient. It can be encoded in three fixed-width binary bits. Recovering the entire source from the sums instead leaves 25 possibilities and requires five joint fixed-width bits.

### An encoder that sees only the detail leaf

Let the encoder receive (d_0,d_1), without the sums. It sends

\[
\boxed{c=d_1-d_0.}
\]

The decoder computes

\[
\boxed{s'_0=3(s_0+s_1+c),\qquad
s'_1=3(s_0+s_1-c)\pmod5.}
\]

The message is a linear function of the encoder's actual input. No hidden access to the decoder's observation is needed.

For x=(4,1,3,2), the native packet code gives

\[
(s_0,s_1,d_0,d_1)=(0,0,3,1)\pmod5.
\]

The supplement is c=3. The decoder obtains (s'_0,s'_1)=(4,1). Directly shifting the source gives (1,3,2,4), whose sums are indeed (4,1) modulo 5.

The generic repair algorithm may return a nonzero scalar rescaling of c, with a corresponding decoder. The report retains both that algorithmic certificate and the manual code above. Both are checked.

### What “one packet” does and does not mean

| Allowed communication unit | Minimum required for this task |
|---|---:|
| Arbitrary linear field coordinates computed from the details | 1 coordinate |
| Unmodified individual detail coordinates | Both d_0 and d_1 |
| Intact native Haar detail leaf | 1 leaf containing 2 coordinates |
| Joint fixed-width binary encoding of the minimal coded supplement | 3 bits |

A claim that “two native packets were compressed into one” would be inaccurate here. There is one native detail leaf with two coordinates. The improvement is a two-coordinate raw payload versus a one-coordinate task-specific coded payload. This does not reduce the sensing cost of acquiring both coordinates at the encoder.

### An impossible restricted repair

Suppose the encoder sees only d_0. Compare x=0 with

\[
v=(0,0,4,1).
\]

Both give s_0=s_1=0 and d_0=0. But their next coarse outputs are (0,0) and (4,1). No encoder depending only on d_0 can help the decoder distinguish them, regardless of its message alphabet size.

The algorithm produces this witness rather than an empty or misleading success certificate.

## 2. The same supplement closes every future coarse output

Define the augmented state

\[
u=(s_0,s_1,c),\qquad c=d_1-d_0.
\]

The next supplement is

\[
c'=s_1-s_0.
\]

Hence the reduced dynamics is

\[
\boxed{
\begin{bmatrix}s'_0\\s'_1\\c'\end{bmatrix}
=
\begin{bmatrix}
1/2&1/2&1/2\\
1/2&1/2&-1/2\\
-1&1&0
\end{bmatrix}
\begin{bmatrix}s_0\\s_1\\c\end{bmatrix}.
}
\]

This is an exact autonomous three-coordinate state. Once its initial supplement is supplied, no new hidden-detail messages are required to predict future coarse outputs in this noiseless, known-dynamics example.

The row-space closure algorithm independently returns dimensions 2 then 3 and stops. It constructs the matrix identities R=DS and ST=MS. The smallest predictive representation has 5^3=125 states, compared with 5^4=625 underlying source states.

The source is still not reconstructible. The nonzero direction

\[
\delta=(1,-1,1,-1)
\]

has zero sums and zero c. Its shift is -delta. Adding any multiple of delta to a source leaves every future coarse observation unchanged. Each complete predictive state therefore corresponds to five underlying sources.

**Predictive sufficiency is not source completeness.** The program checks all 625 initial states and 12 steps per state, totaling 7,500 trajectory checks. The matrix identity, rather than this finite horizon alone, proves validity for every horizon.

The initial supplement must actually be acquired. This does not infer c from the inadequate initial sums. A future coarse measurement can reveal it, but doing so adds observation delay and constitutes a different acquisition mechanism.

## 3. Why endpoint information deficits can disappear and return

Under two shifts, the two sums simply swap. After four shifts the source returns to its original position. Thus the information needed to predict an endpoint from the initial sums depends on the horizon.

| Horizon h | Extra field coordinates for endpoint RT^h x | Extra coordinates for the entire output trajectory through h |
|---:|---:|---:|
| 0 | 0 | 0 |
| 1 | 1 | 1 |
| 2 | 0 | 1 |
| 3 | 1 | 1 |
| 4 | 0 | 1 |
| 5 | 1 | 1 |
| 6 | 0 | 1 |
| 7 | 1 | 1 |
| 8 | 0 | 1 |

At horizon two, predicting the endpoint does not require reproducing the missing odd-time output. It is a different task. The full underlying state has continued to evolve, and hidden directions can cancel in a composite transfer block.

This is not a violation of data processing, nor a procedure for reconstructing information after it has been irreversibly discarded. The trajectory task retains every intermediate demand and its deficit never decreases.

The general two-stage block identity is

\[
(B_2B_1)_{oz}=B_{2,oo}B_{1,oz}+B_{2,oz}B_{1,zz}.
\]

Exact tests cover all 6,817 pairs of two-by-two transfer matrices over F_2 and F_3. In 1,004 of those pairs, both individual leakage blocks are nonzero but the composed leakage vanishes.

## 4. Restricted access can hurt partial recovery even when exact repair is optimal

Let x=(a,b) range over all F_3^2. The decoder sees a, the task is b, and the helper sees only b. Give the states the full-support weights

\[
\begin{array}{c|ccc}
&b=0&b=1&b=2\\\hline
a=0&2&2&1\\
a=1&2&1&2\\
a=2&1&2&2
\end{array}
\]

divided by 15.

Both the state-aware encoder and the b-only encoder require three symbols for perfect recovery. This agrees with the linear theorem: d=1 and q^d=3.

With two symbols, a state-aware encoder can choose a different pair of favored answers for each a. Each row's two largest weights sum to four, so its optimal success is

\[
\frac{4+4+4}{15}=\frac45.
\]

A helper that sees b alone must use the same labeling for every row. Any nonconstant two-symbol code merges two b values. Whichever pair it merges, the lost weights across the rows are 2,1,1 in some order. Its best success is

\[
1-\frac{2+1+1}{15}=\frac{11}{15}.
\]

| Message alphabet | State-aware optimum | b-only optimum |
|---:|---:|---:|
| 1 | 2/5 | 2/5 |
| 2 | 4/5 | 11/15 |
| 3 | 1 | 1 |

The code enumerates all 8 two-symbol helper encoders and all 27 three-symbol helper encoders. The optimal decoder is evaluated for each code. The two-symbol difference is 1/15, approximately 6.67 percentage points.

The lesson is precise: a theorem identifying the minimum exact-recovery alphabet does not automatically identify the complete probabilistic repair curve under access restrictions.

## 5. Small packet energy can carry a fixed amount of task information

Let a and b be independent fair signs, and set

\[
x=(\varepsilon a,-\varepsilon a,\varepsilon b,-\varepsilon b).
\]

The sums are always zero. The details are (2epsilon a,2epsilon b), with native unnormalized detail energy 8epsilon^2. The task is to identify (a,b).

For every nonzero epsilon, the observation still conceals four equally likely answers. The exact repair requirement is two bits, conditional entropy is two bits, and optimal error without a message is 3/4.

| epsilon | Detail energy | Missing task bits | Optimal error |
|---:|---:|---:|---:|
| 1 | 8 | 2 | 3/4 |
| 2^-4 | 0.03125 | 2 | 3/4 |
| 2^-12 | 4.76837158203125e-7 | 2 | 3/4 |
| 2^-24 | 2.842170943040401e-14 | 2 | 3/4 |

The values are evaluated through the actual Haar code on exactly representable dyadic inputs. They disprove an unconditional identification of residual energy with missing task information. They do not show that arbitrarily weak physical signals can be read reliably under noise. That requires a separately specified observation channel and precision model.

Likewise, the native `entropy_cost` of a singleton coefficient vector is zero whether its value is 1 or 999. This is correct for a concentrated energy distribution. It is not an uncertainty calculation for a random task answer.

## Verification levels

All stated examples are reproduced in normal and optimized Python execution. Native arithmetic, exact modular algebra, exhaustive finite-state comparison, and general proofs are explicitly separated. The original library is unchanged, no repository write occurred, and no Lean theorem was compiled.
