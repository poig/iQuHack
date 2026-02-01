import pyzx as zx
from qiskit import QuantumCircuit, transpile, qasm2
import numpy as np

def analyze_reduced_layers():
    path = "challenge/P9_grand_summit.qasm"
    print("PyZX Reduction & Layer Analysis...")
    
    # PyZX Reduction
    qc_orig = QuantumCircuit.from_qasm_file(path)
    g = zx.Circuit.from_qasm(qasm2.dumps(qc_orig)).to_graph()
    zx.full_reduce(g)
    circ_reduced = zx.extract_circuit(g)
    qc_zx = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())
    
    # Transpile to see structure
    qc_trans = transpile(qc_zx, basis_gates=['u3', 'cx'], optimization_level=3)
    
    print(f"Reduced Depth: {qc_trans.depth()}")
    
    # Count gates per layer (time slice)
    # Using Qiskit's depth-based scheduling logic approximation
    
    n = qc_trans.num_qubits
    qubit_depth = [0] * n
    layer_counts = {}
    
    gate_locations = []
    
    for inst in qc_trans.data:
        qargs = [qc_trans.find_bit(q).index for q in inst.qubits]
        start_time = max(qubit_depth[i] for i in qargs)
        
        # Log gate at this depth
        layer_counts[start_time] = layer_counts.get(start_time, 0) + 1
        gate_locations.append((start_time, inst.operation.name))
        
        for i in qargs:
            qubit_depth[i] = start_time + 1
            
    max_depth = max(qubit_depth)
    print(f"Computed Depth: {max_depth}")
    
    # Print density profile
    print("\nGate Density by Layer (Bin size 5):")
    for bin_start in range(0, max_depth, 5):
        count = 0
        for t in range(bin_start, bin_start+5):
            count += layer_counts.get(t, 0)
        print(f"Layers {bin_start}-{bin_start+4}: {count} gates")
        
    # Check if gates are concentrated?
    
if __name__ == "__main__":
    analyze_reduced_layers()
