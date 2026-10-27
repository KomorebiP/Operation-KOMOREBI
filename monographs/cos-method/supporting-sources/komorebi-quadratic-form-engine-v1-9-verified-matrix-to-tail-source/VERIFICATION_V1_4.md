# Komorebi Quadratic-Form Engine v1.4 interval verification

## Directed-rounding controls

Three exact positive central controls were enclosed with:
- K = 128;
- interval precision = 90 decimal digits;
- exact supplied spectrum 0.02 repeated 80 times;
- independent exact even-df chi-square interval reference.

Results:

 target_log10_p  kcos_width_decades  multiplicative_ratio_minus_one  intervals_overlap  target_contained_by_both
           -100        8.952838e-13                    2.061467e-12               True                      True
          -1000        6.934897e-12                    1.596819e-11               True                      True
          -5000        3.365130e-11                    7.748499e-11               True                      True

All three interval K-COS enclosures overlap the independent exact interval
reference and contain the requested target log-probability.

## Precision sweep at 1e-5000

 interval_dps  total_width_decades_decimal  arithmetic_only_width_decades_decimal  exact_reference_width_decades_decimal  kcos_lower_float  kcos_upper_float  contains_minus_5000
           40                 3.342474e-11                           7.523100e-37                           3.761600e-37           -5000.0           -5000.0                 True
           60                 3.342474e-11                           5.097900e-57                           3.823400e-57           -5000.0           -5000.0                 True
           80                 3.342474e-11                           6.909000e-77                           5.181800e-77           -5000.0           -5000.0                 True
          100                 3.342474e-11                           4.681700e-97                           2.926000e-97           -5000.0           -5000.0                 True
          120                 3.342474e-11                          6.344800e-117                          4.758600e-117           -5000.0           -5000.0                 True

The total width is stable while arithmetic-only width shrinks by about 80
orders of magnitude, showing that the bound is dominated by analytic
truncation rather than rounding.

## Tests

`test_interval_kcos.py`: 3/3 PASS.

## Boundary

This is a rigorous numerical enclosure for an exact supplied positive spectrum,
conditional on correctness of the mpmath interval implementation.  It is not
yet a directed-rounding certification of arbitrary floating-point matrix
eigendecomposition or packetized spectrum compression.
