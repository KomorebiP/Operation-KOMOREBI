from projector_seed_residuals.transport import (
    DirectedGraph,
    brute_force_minimum_seed_count,
    minimum_seed_representatives,
    source_components,
    strongly_connected_components,
    transport_closure,
)


def graph_fixture() -> DirectedGraph:
    graph = DirectedGraph()
    for vertex in "ABCDEFG":
        graph.add_vertex(vertex)
    for source, target in [("A", "B"), ("B", "A"), ("B", "C"), ("D", "E"), ("E", "D"), ("E", "F")]:
        graph.add_edge(source, target)
    return graph


def test_scc_partition() -> None:
    components = [frozenset(component) for component in strongly_connected_components(graph_fixture())]
    assert set(components) == {frozenset("AB"), frozenset("C"), frozenset("DE"), frozenset("F"), frozenset("G")}


def test_source_components() -> None:
    sources = {frozenset(component) for component in source_components(graph_fixture())}
    assert sources == {frozenset("AB"), frozenset("DE"), frozenset("G")}


def test_directed_minimum_seed_theorem() -> None:
    graph = graph_fixture()
    representatives = minimum_seed_representatives(graph)
    assert len(representatives) == 3
    assert brute_force_minimum_seed_count(graph) == 3
    assert transport_closure(graph, representatives) == set(graph.vertices)
