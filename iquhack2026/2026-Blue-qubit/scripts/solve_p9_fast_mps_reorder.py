import argparse
import time
from collections import defaultdict

import networkx as nx
import pyzx as zx
from qiskit import QuantumCircuit, qasm2, transpile
from qiskit_aer import AerSimulator


def build_interaction_graph_from_qiskit(qc: QuantumCircuit) -> nx.Graph:
    g = nx.Graph()
    g.add_nodes_from(range(qc.num_qubits))
    for inst in qc.data:
        if len(inst.qubits) == 2:
            u = qc.find_bit(inst.qubits[0]).index
            v = qc.find_bit(inst.qubits[1]).index
            if u != v:
                g.add_edge(u, v)
    return g


def build_interaction_graph_zx_simplified(qc: QuantumCircuit) -> nx.Graph:
    qasm_str = qasm2.dumps(qc)
    zg = zx.Circuit.from_qasm(qasm_str).to_graph()
    zx.full_reduce(zg)
    circ_reduced = zx.extract_circuit(zg)
    qc_zx = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())

    g = nx.Graph()
    g.add_nodes_from(range(qc_zx.num_qubits))
    for inst in qc_zx.data:
        if len(inst.qubits) == 2:
            u = qc_zx.find_bit(inst.qubits[0]).index
            v = qc_zx.find_bit(inst.qubits[1]).index
            if u != v:
                g.add_edge(u, v)
    return g


def rcm_ordering(g: nx.Graph) -> list[int]:
    # networkx returns nodes in RCM order; we ensure it includes all nodes.
    order = list(nx.utils.reverse_cuthill_mckee_ordering(g))
    if len(order) != g.number_of_nodes():
        # disconnected graphs return partial ordering; fill in the rest
        remaining = [n for n in g.nodes if n not in set(order)]
        order.extend(remaining)
    return order


def permute_circuit(qc: QuantumCircuit, old_to_new: dict[int, int]) -> QuantumCircuit:
    n = qc.num_qubits
    out = QuantumCircuit(n)
    for inst in qc.data:
        new_qubits = [out.qubits[old_to_new[qc.find_bit(q).index]] for q in inst.qubits]
        out.append(inst.operation, new_qubits)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Fast P9 attempt: reorder qubits to reduce MPS bond")
    parser.add_argument("--qasm", default="challenge/P9_grand_summit.qasm")
    parser.add_argument("--bond", type=int, default=128)
    parser.add_argument("--shots", type=int, default=4000)
    parser.add_argument("--use-zx-graph", action="store_true", help="Use PyZX-full-reduced graph for ordering")
    args = parser.parse_args()

    qc = QuantumCircuit.from_qasm_file(args.qasm)
    print(f"Loaded: qubits={qc.num_qubits}, depth={qc.depth()}, ops={len(qc.data)}")

    print("Building interaction graph...")
    t0 = time.time()
    if args.use_zx_graph:
        g = build_interaction_graph_zx_simplified(qc)
        print(f"Graph (zx-simplified) nodes={g.number_of_nodes()} edges={g.number_of_edges()} in {time.time()-t0:.2f}s")
    else:
        g = build_interaction_graph_from_qiskit(qc)
        print(f"Graph nodes={g.number_of_nodes()} edges={g.number_of_edges()} in {time.time()-t0:.2f}s")

    order = rcm_ordering(g)
    new_to_old = {new: old for new, old in enumerate(order)}
    old_to_new = {old: new for new, old in new_to_old.items()}

    qc_perm = permute_circuit(qc, old_to_new)
    print(f"Permuted circuit: depth={qc_perm.depth()} ops={len(qc_perm.data)}")

    qc_perm_meas = qc_perm.copy()
    qc_perm_meas.measure_all()

    sim = AerSimulator(method="matrix_product_state")
    sim.set_options(matrix_product_state_max_bond_dimension=args.bond)

    t0 = time.time()
    tqc = transpile(qc_perm_meas, sim, optimization_level=1)
    result = sim.run(tqc, shots=args.shots).result()
    counts = result.get_counts()
    print(f"Simulation done in {time.time()-t0:.2f}s. Unique outcomes={len(counts)}")

    top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:10]
    print("Top outcomes in PERMUTED basis (q[n-1]..q[0] of permuted circuit):")
    for s, c in top:
        print(f"  {c:5d}  {s}")

    # Map top outcome back to original qubit order.
    best_s_perm = top[0][0]
    n = qc.num_qubits
    # best_s_perm is big-endian string: char idx 0 is qubit n-1
    perm_bits = list(best_s_perm)
    orig_bits = ["?"] * n
    for str_idx, bit in enumerate(perm_bits):
        new_q = n - 1 - str_idx
        old_q = new_to_old[new_q]
        orig_bits[old_q] = bit

    best_s_orig = "".join(orig_bits)
    print("Best mapped back to ORIGINAL qubit labels:")
    print(f"  submit:  {best_s_orig}")
    print(f"  reverse: {best_s_orig[::-1]}")


if __name__ == "__main__":
    main()
