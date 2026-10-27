"""Work through E[r,s,m] = h[N*m+r-s] and operator composition."""
import json
import numpy as np
from komorebi_pr_lasm import PolyphaseFIR


def main() -> None:
    x = np.asarray([2., -1., 3., 0., 4., 1., -2.])
    h = np.asarray([1., -2., 1.])
    bank = PolyphaseFIR(h, modulus=3)
    result = bank.apply(x)
    direct = np.convolve(x, h)
    smooth = PolyphaseFIR([0.25, 0.5, 0.25], modulus=3)
    composed = bank.compose(smooth).apply(x)
    sequential = bank.apply(smooth.apply(x))
    assert np.array_equal(result, direct)
    assert np.allclose(composed, sequential, atol=1e-13)
    print(json.dumps({"input": x.tolist(), "taps": h.tolist(),
                      "block_axes": ["output_phase", "input_phase", "coarse_lag"],
                      "blocks": bank.blocks.tolist(), "full_convolution": result.tolist(),
                      "composition_max_error": float(np.max(np.abs(composed-sequential)))}, indent=2))


if __name__ == '__main__':
    main()
