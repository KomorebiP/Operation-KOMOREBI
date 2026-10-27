from packet_gpu.complexity import (
    amortized_break_even,
    arithmetic_intensity,
    bdlr_apply_flops,
    bdlr_storage,
    block_apply_flops,
    block_storage,
    dense_apply_flops,
    dense_storage,
    equal_block_launch_count,
    equal_packet_sizes,
    graph_break_even,
    ideal_bdlr_speedup,
    sparse_packet_apply_flops,
)


def test_dense_block_bdlr_counts() -> None:
    sizes = equal_packet_sizes(8192, 64)
    assert dense_apply_flops(8192, 32) == 2 * 8192**2 * 32
    assert block_apply_flops(sizes, 32) == 2 * 32 * 8192 * 64
    assert bdlr_apply_flops(sizes, 8, 32) == 2 * 32 * 8192 * (64 + 16)
    assert dense_storage(8192, 4) == 8192**2 * 4
    assert block_storage(sizes, 4) == 8192 * 64 * 4
    assert bdlr_storage(sizes, 8, 4) == 8192 * (64 + 16) * 4


def test_ideal_speedup_formula() -> None:
    assert ideal_bdlr_speedup(8192, 64, 8) == 8192 / 80


def test_sparse_edge_count() -> None:
    sizes = (4, 5, 6)
    edges = [(0, 0), (1, 0), (2, 1)]
    assert sparse_packet_apply_flops(sizes, edges, 3) == 2 * 3 * (16 + 20 + 30)


def test_amortization_threshold() -> None:
    assert amortized_break_even(2.1102, 0.0969, 0.0151) == 26
    assert amortized_break_even(5.2726, 0.1896, 0.0241) == 32
    assert amortized_break_even(1.0, 1.0, 1.0) is None
    assert graph_break_even(2.0, 1.0, 0.5) == 5


def test_intensity_and_launch_grouping() -> None:
    assert arithmetic_intensity(1000, 100) == 10
    assert equal_block_launch_count(4096, 64, True) == 1
    assert equal_block_launch_count(4096, 64, False) == 64
