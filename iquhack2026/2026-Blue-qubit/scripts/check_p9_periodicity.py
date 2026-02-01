from qiskit import QuantumCircuit
from collections import defaultdict

def search_periodicity():
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
            
    # Convert layers to canonical form (sorted list of edges)
    layer_list = []
    max_t = max(layers.keys())
    for t in range(max_t + 1):
        edges = tuple(sorted(layers[t]))
        layer_list.append(edges)
        
    print(f"Total layers with CZ: {len(layer_list)}")
    
    # Simple search for periodicity
    for period in range(1, len(layer_list) // 2):
        matches = 0
        for i in range(len(layer_list) - period):
            if layer_list[i] == layer_list[i + period]:
                matches += 1
        if matches > len(layer_list) / 3:
            print(f"Found periodicity! Period={period}, Matches={matches}")
            
    # Check for mirror periodicity (palindrome)
    for pivot in range(len(layer_list) // 4, 3 * len(layer_list) // 4):
        size = min(pivot, len(layer_list) - pivot)
        matches = 0
        for k in range(size):
            if layer_list[pivot - k] == layer_list[pivot + k]:
                matches += 1
        if matches > size * 0.8:
            print(f"Found mirror symmetry! Pivot={pivot}, Matches={matches}/{size}")

if __name__ == "__main__":
    search_periodicity()
