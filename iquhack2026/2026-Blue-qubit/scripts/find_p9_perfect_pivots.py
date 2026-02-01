from qiskit import QuantumCircuit
from collections import defaultdict

def search_pivots():
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
            
    all_times = sorted(layers.keys())
    
    # Try every possible pivot
    for pivot in range(10, len(all_times) - 10):
        # Check if Layers [pivot-k] and [pivot+k] match for k=1, 2, 3...
        # Note: pivot could be a layer or between layers.
        # If it's a layer, then we check pivot-1 vs pivot+1, etc.
        for dist in range(1, min(pivot, len(all_times) - pivot)):
            l1 = pivot - dist
            l2 = pivot + dist
            if l1 >= 0 and l2 < len(all_times):
                e1 = set(tuple(sorted(e)) for e in layers[l1])
                e2 = set(tuple(sorted(e)) for e in layers[l2])
                if e1 == e2 and len(e1) > 10:
                    print(f"Pivot {pivot} (Distance {dist}): Layers {l1} and {l2} MATCH PERFECTLY.")

if __name__ == "__main__":
    search_pivots()
