from qiskit import QuantumCircuit
from collections import defaultdict

def check_mirror_connectivity():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc.num_qubits
    
    qubit_time = [0] * n
    layers = defaultdict(list)
    
    for instruction in qc.data:
        qargs = [qc.find_bit(q).index for q in instruction.qubits]
        start_time = max(qubit_time[i] for i in qargs)
        duration = 1
        for i in qargs:
            qubit_time[i] = start_time + duration
        
        if len(qargs) == 2:
            u, v = sorted(qargs)
            layers[start_time].append((u, v))
            
    pivot = 43
    max_k = min(pivot, max(layers.keys()) - pivot)
    
    for k in range(1, max_k + 1):
        l1 = pivot - k
        l2 = pivot + k
        if l1 in layers or l2 in layers:
            edges1 = set(tuple(sorted(e)) for e in layers[l1])
            edges2 = set(tuple(sorted(e)) for e in layers[l2])
            
            common = edges1 & edges2
            if edges1 == edges2:
                print(f"Distance {k}: Layers {l1} and {l2} MATCH PERFECTLY ({len(edges1)} edges)")
            else:
                print(f"Distance {k}: Layers {l1} and {l2} MISMATCH. Common: {len(common)}/{len(edges1 | edges2)}")

if __name__ == "__main__":
    check_mirror_connectivity()
