from qiskit import QuantumCircuit
from collections import defaultdict

def compare_central_layers():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    q_t = [0] * qc.num_qubits
    layers = defaultdict(list)
    
    for instruction in qc.data:
        qargs = [qc.find_bit(q).index for q in instruction.qubits]
        start_time = max(q_t[i] for i in qargs)
        for i in qargs:
            q_t[i] = start_time + 1
        if len(qargs) == 2:
            layers[start_time].append(tuple(sorted(qargs)))
            
    for t in range(35, 55):
        edges = tuple(sorted(layers[t]))
        if not edges:
            print(f"Layer {t:2d}: [Single-Qubit Only]")
            continue
        # Use simple hash or just string representation of edges
        fp = hash(edges) % 10000
        print(f"Layer {t:2d}: {len(edges):2d} edges, Fingerprint: {fp:04d}")

if __name__ == "__main__":
    compare_central_layers()
