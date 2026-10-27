"""Exact bounded check of the Chapter 3 continuant normalization."""
from pathlib import Path
from fractions import Fraction
import argparse
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("packet", ROOT / "historical/catalan_packet_audit.py")
packet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packet)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    u, v = packet.zudilin_sequences(13)
    alpha, beta = {}, {}
    for n in range(1, 13):
        a = (2*n+1)**2 * (2*n+2)**2 * packet.p(n)
        c = (2*n-1)**2 * (2*n)**2 * packet.p(n+1)
        alpha[n], beta[n] = Fraction(packet.q(n), a), Fraction(c, a)
    def continuant(start, end):
        if end == start - 1:
            return Fraction(1)
        previous, current = Fraction(1), alpha[start]
        for j in range(start+1, end+1):
            previous, current = current, alpha[j]*current + beta[j]*previous
        return current
    families = [("historical u", u), ("historical v", v)]
    for w0, w1 in [(Fraction(0), Fraction(1)), (Fraction(1), Fraction(0)), (Fraction(-3,7), Fraction(5,11))]:
        w = [w0, w1]
        for n in range(1,13):
            w.append(alpha[n]*w[n] + beta[n]*w[n-1])
        families.append((f"initial ({w0},{w1})", w))
    failures = []
    for name, w in families:
        for n in range(2,14):
            observed = continuant(1,n-1)*w[1] + beta[1]*continuant(2,n-1)*w[0]
            if observed != w[n]:
                failures.append({"family":name, "n":n, "observed":str(observed), "expected":str(w[n])})
    result = {
        "scope":"Finite continuant implementation check, separate from universal written induction",
        "n_range":[2,13], "coefficient_domain":"fractions.Fraction exact rationals",
        "families":[name for name,_ in families], "instances":60,
        "failures":failures, "passed":not failures,
        "input_sha256":hashlib.sha256((ROOT / "historical/catalan_packet_audit.py").read_bytes()).hexdigest(),
        "written_claim":"paper/chapter03.tex cb_prop_continuant",
        "non_claims":["No new irrationality result", "Finite checks do not establish the all-index identity", "Shared recurrence formulas remain externally sourced"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    if failures:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
