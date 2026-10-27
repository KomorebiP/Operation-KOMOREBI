"""Causal streaming at irregular chunk boundaries, including the finite tail."""
import json
import numpy as np
from komorebi_pr_lasm import StreamingFIR


def main() -> None:
    x = np.sin(np.arange(257) * 0.13)
    taps = np.asarray([0.1, 0.2, 0.4, 0.2, 0.1])
    stream = StreamingFIR(taps)
    cuts = [0, 1, 31, 32, 100, 257]
    outputs = [stream.process(x[left:right]) for left, right in zip(cuts, cuts[1:])]
    tail = stream.flush()
    full = np.concatenate(outputs + [tail])
    error = float(np.max(np.abs(full-np.convolve(x, taps))))
    assert error < 1e-12
    assert tail.size == len(taps)-1
    assert stream.flush().size == 0
    print(json.dumps({"input_length": len(x), "chunk_boundaries": cuts,
                      "causal_output_length": sum(len(y) for y in outputs),
                      "tail_length": len(tail), "max_error": error}, indent=2))


if __name__ == '__main__':
    main()
