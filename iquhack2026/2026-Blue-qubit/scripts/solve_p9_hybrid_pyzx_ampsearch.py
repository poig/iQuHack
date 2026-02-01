import argparse
import json
import re
import time
from pathlib import Path

import pyzx as zx
from qiskit import QuantumCircuit, qasm2
from qiskit_aer import AerSimulator


P9_QASM_PATH = "challenge/P9_grand_summit.qasm"


def load_marginal_candidate(results_json_path: str) -> tuple[str, list[float]]:
    """Return (q0_first_bitstring, vals_by_qubit)."""
    obj = json.loads(Path(results_json_path).read_text())
    n = max(int(k) for k in obj.keys()) + 1
    bits = ["?"] * n
    vals = [0.0] * n
    for k, v in obj.items():
        i = int(k)
        bits[i] = str(v["bit"])
        vals[i] = float(v.get("val", 0.0))
    bitstring = "".join(bits)
    if any(b not in "01" for b in bitstring):
        raise ValueError(f"Invalid marginal bitstring in {results_json_path}")
    return bitstring, vals


def extract_bitstrings_from_files(paths: list[str], n_bits: int) -> set[str]:
    out: set[str] = set()
    pattern = re.compile(rf"[01]{{{n_bits}}}")
    for p in paths:
        path = Path(p)
        if not path.exists():
            continue
        text = path.read_text(errors="ignore")
        for match in pattern.findall(text):
            out.add(match)
    return out


def build_pyzx_reduced_circuit(qc_orig: QuantumCircuit) -> QuantumCircuit:
    qasm_str = qasm2.dumps(qc_orig)

    circ = zx.Circuit.from_qasm(qasm_str)
    g = circ.to_graph()

    t0 = time.time()
    zx.full_reduce(g)
    dt = time.time() - t0
    print(f"  PyZX full_reduce done in {dt:.1f}s")

    circ_reduced = zx.extract_circuit(g)
    qc_zx = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())

    if qc_zx.num_qubits != qc_orig.num_qubits:
        raise ValueError(
            f"PyZX changed qubit count: {qc_orig.num_qubits} -> {qc_zx.num_qubits}. "
            "This script assumes qubit order/size is preserved."
        )

    return qc_zx


def amp2_for_bitstrings(qc: QuantumCircuit, bitstrings: list[str], bond: int) -> dict[str, float]:
    n = qc.num_qubits
    for s in bitstrings:
        if len(s) != n or any(c not in "01" for c in s):
            raise ValueError(f"Bad bitstring length/content: {s}")

    # In Qiskit/Aer basis indexing, q[0] is the least-significant bit.
    # The typical measurement/counts string produced by measure_all is q[n-1]...q[0],
    # which matches int(bitstring, 2) directly.
    uniq = list(dict.fromkeys(bitstrings))
    states = [int(s, 2) for s in uniq]

    qc_eval = qc.copy()
    qc_eval.save_amplitudes_squared(states, label="amp2")

    sim = AerSimulator(method="matrix_product_state")
    sim.set_options(matrix_product_state_max_bond_dimension=bond)

    res = sim.run(qc_eval).result()
    amp2 = res.data(0)["amp2"]

    return {s: float(v) for s, v in zip(uniq, amp2)}


def greedy_flip_search(
    qc: QuantumCircuit,
    seed: str,
    candidate_indices: list[int],
    bond: int,
    max_iters: int,
) -> tuple[str, float]:
    best = seed
    best_p = amp2_for_bitstrings(qc, [best], bond=bond)[best]
    print(f"  Seed amp^2: {best_p:.6e}")

    for it in range(max_iters):
        neighbors: list[str] = []
        for i in candidate_indices:
            flipped = list(best)
            flipped[i] = "1" if flipped[i] == "0" else "0"
            neighbors.append("".join(flipped))

        scores = amp2_for_bitstrings(qc, neighbors + [best], bond=bond)
        # pick the best among neighbors + current
        new_best = max(scores.items(), key=lambda kv: kv[1])
        if new_best[0] == best:
            print(f"  Iter {it+1}: no improvement")
            break

        best, best_p = new_best
        print(f"  Iter {it+1}: improved amp^2 -> {best_p:.6e}")

    return best, best_p


def main() -> None:
    parser = argparse.ArgumentParser(description="P9 solver: PyZX reduce + MPS amplitude search")
    parser.add_argument("--qasm", default=P9_QASM_PATH)
    parser.add_argument("--bond", type=int, default=128)
    parser.add_argument("--no-zx", action="store_true", help="Skip PyZX reduction")
    parser.add_argument("--search", action="store_true", help="Run greedy local bit-flip search")
    parser.add_argument("--search-iters", type=int, default=6)
    parser.add_argument("--uncertain-k", type=int, default=18, help="How many low-|val| qubits to flip in search")
    args = parser.parse_args()

    qc_orig = QuantumCircuit.from_qasm_file(args.qasm)
    print(f"Loaded P9: qubits={qc_orig.num_qubits}, depth={qc_orig.depth()}, ops={len(qc_orig.data)}")

    if args.no_zx:
        qc = qc_orig
        print("Skipping PyZX; using original circuit")
    else:
        print("Running PyZX reduction (this can take a bit)...")
        qc = build_pyzx_reduced_circuit(qc_orig)
        print(f"Reduced circuit: qubits={qc.num_qubits}, depth={qc.depth()}, ops={len(qc.data)}")

    # Collect candidate strings (all in q[n-1]..q[0] order).
    candidates: set[str] = set()

    # 1) From marginal reconstructions
    for p in [
        "results/final_P9_local.json",
        "results/final_P9.json",
    ]:
        try:
            q0_first, vals = load_marginal_candidate(p)
        except FileNotFoundError:
            continue
        cand = q0_first[::-1]
        candidates.add(cand)

    # 2) From any stored bitstrings in repo files
    candidates |= extract_bitstrings_from_files(
        [
            "solutions/p9_mps_improved.txt",
            "solutions/p9_pyzx_mps.txt",
            "scripts/p9_approx_solution.txt",
            "results/final_P9_ibm_qpu.json",
        ],
        n_bits=qc.num_qubits,
    )

    if not candidates:
        raise RuntimeError("No candidates found")

    # Rank initial candidates by amp^2
    print(f"Scoring {len(candidates)} initial candidates with MPS bond={args.bond}...")
    scored = amp2_for_bitstrings(qc, sorted(candidates), bond=args.bond)
    top = sorted(scored.items(), key=lambda kv: kv[1], reverse=True)[:10]

    print("Top candidates by amp^2:")
    for s, p in top:
        print(f"  {p:.6e}  {s}")

    best_s, best_p = top[0]

    if args.search:
        # Use marginal vals (if available) to pick uncertain qubits.
        try:
            q0_first, vals = load_marginal_candidate("results/final_P9_local.json")
        except FileNotFoundError:
            vals = [0.0] * qc.num_qubits

        # candidate_indices are indices in the *submission-order string* s = q[n-1]..q[0]
        # We have vals indexed by q[0]..q[n-1], so map q_index -> string_index
        # string_index = n-1-q_index
        n = qc.num_qubits
        ranked = sorted(range(n), key=lambda q: abs(vals[q]))
        q_uncertain = ranked[: min(args.uncertain_k, n)]
        s_indices = [n - 1 - q for q in q_uncertain]

        print(f"Running greedy flip search on {len(s_indices)} uncertain qubits...")
        best_s, best_p = greedy_flip_search(
            qc,
            seed=best_s,
            candidate_indices=s_indices,
            bond=args.bond,
            max_iters=args.search_iters,
        )

    print("\nBest candidate:")
    print(f"  amp^2: {best_p:.6e}")
    print(f"  submit: {best_s}")
    print(f"  reverse: {best_s[::-1]}")


if __name__ == "__main__":
    main()
