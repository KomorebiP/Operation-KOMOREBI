#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <unordered_set>
#include <vector>

using U128 = __uint128_t;

struct Hash128 {
    std::size_t operator()(U128 x) const noexcept {
        std::uint64_t a = static_cast<std::uint64_t>(x);
        std::uint64_t b = static_cast<std::uint64_t>(x >> 64);
        a ^= b + 0x9e3779b97f4a7c15ULL + (a << 6) + (a >> 2);
        a ^= a >> 30;
        a *= 0xbf58476d1ce4e5b9ULL;
        a ^= a >> 27;
        a *= 0x94d049bb133111ebULL;
        a ^= a >> 31;
        return static_cast<std::size_t>(a);
    }
};

static U128 identity(int n) {
    U128 x = 0;
    for (int i = 0; i < n; ++i) x |= (U128(1) << i) << (i * n);
    return x;
}

static U128 add_row(U128 x, int n, int source, int target) {
    const U128 mask = (U128(1) << n) - 1;
    const U128 row = (x >> (source * n)) & mask;
    return x ^ (row << (target * n));
}

static U128 snapshot_target(int n, int u, const std::vector<int>& phases) {
    const int p = u;
    const int q = u + 1;
    const int first_t = u + 2;
    std::vector<U128> rows(n);
    for (int i = 0; i < n; ++i) rows[i] = U128(1) << i;
    for (int i = 0; i < u; ++i) rows[p] |= U128(1) << i;
    for (std::size_t j = 0; j < phases.size(); ++j) {
        const int t = first_t + static_cast<int>(j);
        rows[t] |= (U128(1) << p) | (U128(1) << q);
        for (int i = 0; i < phases[j]; ++i) rows[t] |= U128(1) << i;
    }
    U128 x = 0;
    for (int i = 0; i < n; ++i) x |= rows[i] << (i * n);
    return x;
}

static std::vector<U128> ball(U128 start, int n, int depth) {
    std::unordered_set<U128, Hash128> visited;
    visited.reserve(8'000'000);
    std::vector<U128> frontier{start};
    std::vector<U128> next;
    visited.insert(start);
    for (int d = 0; d < depth; ++d) {
        next.clear();
        next.reserve(frontier.size() * 30);
        for (U128 x : frontier) {
            for (int s = 0; s < n; ++s) {
                for (int t = 0; t < n; ++t) {
                    if (s == t) continue;
                    U128 y = add_row(x, n, s, t);
                    if (visited.insert(y).second) next.push_back(y);
                }
            }
        }
        frontier.swap(next);
    }
    std::vector<U128> out;
    out.reserve(visited.size());
    for (U128 x : visited) out.push_back(x);
    std::sort(out.begin(), out.end());
    return out;
}

static std::size_t intersection_size(const std::vector<U128>& a, const std::vector<U128>& b) {
    std::size_t i = 0, j = 0, count = 0;
    while (i < a.size() && j < b.size()) {
        if (a[i] < b[j]) ++i;
        else if (b[j] < a[i]) ++j;
        else { ++count; ++i; ++j; }
    }
    return count;
}

static void check_case(int n, int u, const std::vector<int>& phases,
                       int left_depth, int right_depth, int explicit_length) {
    U128 target = snapshot_target(n, u, phases);
    auto left = ball(identity(n), n, left_depth);
    auto right = ball(target, n, right_depth);
    std::size_t meet = intersection_size(left, right);
    std::cout << "n=" << n
              << " left_radius=" << left_depth
              << " left_ball=" << left.size()
              << " right_radius=" << right_depth
              << " right_ball=" << right.size()
              << " intersection=" << meet
              << " explicit_length=" << explicit_length
              << " exact_ambient=" << explicit_length
              << '\n';
    if (meet != 0) std::exit(1);
}

int main() {
    check_case(7, 2, {0, 1, 2}, 3, 3, 7);
    check_case(8, 3, {0, 1, 2}, 3, 4, 8);
    check_case(9, 3, {0, 1, 2, 3}, 4, 4, 9);
    return 0;
}
