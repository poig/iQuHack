
from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag
import matplotlib.pyplot as plt
import numpy as np

def profile_layers():
    print("Loading Bitcoin P1...")
    qc = QuantumCircuit.from_qasm_file("bitcoin_problem/P1_little_dimple.qasm")
    dag = circuit_to_dag(qc)
    
    layers = list(dag.layers())
    gate_counts = []
    qubit_counts = []
    
    for i, layer in enumerate(layers):
        nodes = layer['graph'].op_nodes()
        n_2q = sum(1 for n in nodes if len(n.qargs) == 2)
        gate_counts.append(n_2q)
        
    print(f"Total Layers: {len(gate_counts)}")
    print(f"Avg 2Q gates/layer: {np.mean(gate_counts):.2f}")
    
    # Print suspicious "Low Density" zones
    low_zones = []
    current_low = []
    for i, count in enumerate(gate_counts):
        if count <= 2:
            current_low.append(i)
        else:
            if len(current_low) > 5:
                low_zones.append((current_low[0], current_low[-1]))
            current_low = []
            
    if low_zones:
        print("\nLow Density Zones (Potential Pinch Points):")
        for start, end in low_zones:
            print(f"  Layers {start}-{end} (Len {end-start+1})")
    else:
        print("\nNo obvious pinch points (count <= 2) found.")

    # Check for symmetry in 2Q gate counts
    mid = len(gate_counts) // 2
    first_half = gate_counts[:mid]
    second_half = gate_counts[mid+1:][::-1]
    
    min_len = min(len(first_half), len(second_half))
    match_score = sum(1 for i in range(min_len) if first_half[i] == second_half[i])
    print(f"\nSymmetry Match Score: {match_score}/{min_len} ({100*match_score/min_len:.1f}%)")

if __name__ == "__main__":
    profile_layers()
