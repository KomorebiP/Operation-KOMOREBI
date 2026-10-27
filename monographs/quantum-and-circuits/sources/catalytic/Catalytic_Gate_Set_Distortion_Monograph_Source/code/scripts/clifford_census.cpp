#include <algorithm>
#include <cstdint>
#include <deque>
#include <fstream>
#include <iostream>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

struct Gate {
    enum Type { H, S, CX, CZ, SWAP } type;
    int a;
    int b;
    int cost;
};

static uint64_t row_mask(int m) { return (uint64_t(1) << m) - 1; }

static uint64_t get_row(uint64_t state, int row, int m) {
    return (state >> (row * m)) & row_mask(m);
}

static uint64_t set_row(uint64_t state, int row, int m, uint64_t value) {
    const uint64_t mask = row_mask(m) << (row * m);
    return (state & ~mask) | ((value & row_mask(m)) << (row * m));
}

static uint64_t identity_state(int m) {
    uint64_t state = 0;
    for (int i = 0; i < m; ++i) state = set_row(state, i, m, uint64_t(1) << i);
    return state;
}

static uint64_t apply_gate(uint64_t state, const Gate& gate, int n) {
    const int m = 2 * n;
    auto swap_rows = [&](int r, int s) {
        const uint64_t a = get_row(state, r, m);
        const uint64_t b = get_row(state, s, m);
        state = set_row(state, r, m, b);
        state = set_row(state, s, m, a);
    };
    switch (gate.type) {
        case Gate::H:
            swap_rows(gate.a, n + gate.a);
            break;
        case Gate::S: {
            const uint64_t value = get_row(state, n + gate.a, m) ^ get_row(state, gate.a, m);
            state = set_row(state, n + gate.a, m, value);
            break;
        }
        case Gate::CX: {
            const uint64_t rt = get_row(state, gate.b, m) ^ get_row(state, gate.a, m);
            const uint64_t rzc = get_row(state, n + gate.a, m) ^ get_row(state, n + gate.b, m);
            state = set_row(state, gate.b, m, rt);
            state = set_row(state, n + gate.a, m, rzc);
            break;
        }
        case Gate::CZ: {
            const uint64_t rzi = get_row(state, n + gate.a, m) ^ get_row(state, gate.b, m);
            const uint64_t rzj = get_row(state, n + gate.b, m) ^ get_row(state, gate.a, m);
            state = set_row(state, n + gate.a, m, rzi);
            state = set_row(state, n + gate.b, m, rzj);
            break;
        }
        case Gate::SWAP:
            swap_rows(gate.a, gate.b);
            swap_rows(n + gate.a, n + gate.b);
            break;
    }
    return state;
}

static std::vector<Gate> make_generators(int n, bool ambient, bool entangling, bool include_swap) {
    std::vector<Gate> gates;
    const int local_cost = entangling ? 0 : 1;
    for (int i = 0; i < n; ++i) gates.push_back({Gate::S, i, -1, local_cost});
    for (int c = 0; c < n; ++c) {
        for (int t = 0; t < n; ++t) {
            if (c != t) gates.push_back({Gate::CX, c, t, 1});
        }
    }
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            gates.push_back({Gate::CZ, i, j, 1});
            if (include_swap) gates.push_back({Gate::SWAP, i, j, 1});
        }
    }
    if (ambient) {
        for (int i = 0; i < n; ++i) gates.push_back({Gate::H, i, -1, local_cost});
    }
    return gates;
}

using DistMap = std::unordered_map<uint64_t, uint8_t>;

static DistMap bfs(int n, const std::vector<Gate>& gates, bool weighted) {
    const uint64_t identity = identity_state(2 * n);
    DistMap dist;
    dist.reserve(n == 3 ? 1600000 : 2048);
    dist.emplace(identity, 0);
    if (!weighted) {
        std::queue<uint64_t> queue;
        queue.push(identity);
        while (!queue.empty()) {
            const uint64_t state = queue.front();
            queue.pop();
            const uint8_t next = uint8_t(dist.at(state) + 1);
            for (const auto& gate : gates) {
                const uint64_t candidate = apply_gate(state, gate, n);
                if (dist.emplace(candidate, next).second) queue.push(candidate);
            }
        }
    } else {
        std::deque<uint64_t> queue;
        queue.push_back(identity);
        while (!queue.empty()) {
            const uint64_t state = queue.front();
            queue.pop_front();
            const uint8_t current = dist.at(state);
            for (const auto& gate : gates) {
                const uint64_t candidate = apply_gate(state, gate, n);
                const uint8_t proposed = uint8_t(current + gate.cost);
                auto it = dist.find(candidate);
                if (it == dist.end() || proposed < it->second) {
                    dist[candidate] = proposed;
                    if (gate.cost == 0) queue.push_front(candidate);
                    else queue.push_back(candidate);
                }
            }
        }
    }
    return dist;
}

int main(int argc, char** argv) {
    int n = 3;
    bool entangling = false;
    bool include_swap = false;
    std::string output_path;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--n" && i + 1 < argc) n = std::stoi(argv[++i]);
        else if (arg == "--entangling") entangling = true;
        else if (arg == "--metric" && i + 1 < argc) {
            const std::string metric = argv[++i];
            if (metric == "total") entangling = false;
            else if (metric == "entangling") entangling = true;
            else throw std::runtime_error("metric must be total or entangling");
        }
        else if (arg == "--swap") include_swap = true;
        else if (arg == "--output" && i + 1 < argc) output_path = argv[++i];
        else if (arg == "--help") {
            std::cout << "usage: clifford_census [--n 1|2|3] [--metric total|entangling] [--swap] [--output FILE]\n";
            return 0;
        }
        else throw std::runtime_error("unknown argument: " + arg);
    }
    if (n < 1 || n > 3) throw std::runtime_error("this verifier supports 1 <= n <= 3");
    const auto restricted_gates = make_generators(n, false, entangling, include_swap);
    const auto ambient_gates = make_generators(n, true, entangling, include_swap);
    const auto restricted = bfs(n, restricted_gates, entangling);
    const auto ambient = bfs(n, ambient_gates, entangling);

    std::unordered_map<int, size_t> distribution;
    int maximum_defect = 0;
    size_t defect_count = 0;
    int restricted_diameter = 0;
    int ambient_diameter = 0;
    for (const auto& [state, distance] : restricted) {
        restricted_diameter = std::max(restricted_diameter, int(distance));
        const int other = ambient.at(state);
        if (distance > other) {
            ++defect_count;
            maximum_defect = std::max(maximum_defect, int(distance) - other);
            distribution[100 * int(distance) + other]++;
        }
    }
    for (const auto& [state, distance] : ambient) ambient_diameter = std::max(ambient_diameter, int(distance));

    std::vector<std::pair<int, size_t>> ordered(distribution.begin(), distribution.end());
    std::sort(ordered.begin(), ordered.end());
    std::ofstream file;
    std::ostream* output = &std::cout;
    if (!output_path.empty()) {
        file.open(output_path);
        if (!file) throw std::runtime_error("cannot open output file: " + output_path);
        output = &file;
    }
    auto& out = *output;
    out << "{\n";
    out << "  \"qubits\": " << n << ",\n";
    out << "  \"metric\": \"" << (entangling ? "entangling" : "total") << "\",\n";
    out << "  \"include_swap\": " << (include_swap ? "true" : "false") << ",\n";
    out << "  \"restricted_group_size\": " << restricted.size() << ",\n";
    out << "  \"ambient_group_size\": " << ambient.size() << ",\n";
    out << "  \"restricted_diameter\": " << restricted_diameter << ",\n";
    out << "  \"ambient_diameter\": " << ambient_diameter << ",\n";
    out << "  \"defect_count\": " << defect_count << ",\n";
    out << "  \"maximum_defect\": " << maximum_defect << ",\n";
    out << "  \"defect_distribution\": {";
    for (size_t i = 0; i < ordered.size(); ++i) {
        if (i) out << ", ";
        const int key = ordered[i].first;
        out << "\"" << key / 100 << "->" << key % 100 << "\": " << ordered[i].second;
    }
    out << "}\n";
    out << "}\n";
}
