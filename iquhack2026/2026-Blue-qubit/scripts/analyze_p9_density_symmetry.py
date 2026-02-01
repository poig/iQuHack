from qiskit import QuantumCircuit
import sys

def analyze_density_symmetry():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    qubit_time = [0] * qc.num_qubits
    layer_counts = {}
    
    for instruction in qc.data:
        qargs = [qc.find_bit(q).index for q in instruction.qubits]
        start_time = max(qubit_time[i] for i in qargs)
        duration = 1
        for i in qargs:
            qubit_time[i] = start_time + duration
        
        if len(qargs) == 2:
            layer_counts[start_time] = layer_counts.get(start_time, 0) + 1
            
    times = sorted(layer_counts.keys())
    max_t = max(times)
    
    # Try different pivots
    for pivot in range(max_t // 4, 3 * max_t // 4):
        size = min(pivot, max_t - pivot)
        diff = 0
        for k in range(1, size + 1):
            c1 = layer_counts.get(pivot - k, 0)
            c2 = layer_counts.get(pivot + k, 0)
            diff += abs(c1 - c2)
        
        # print(f"Pivot {pivot}: cumulative diff {diff}")
        if diff == 0:
            print(f"PERFECT Density Symmetry found at Pivot Layer: {pivot} (Size: {size})")
        elif diff < 10:
             print(f"High Density Symmetry found at Pivot Layer: {pivot} (Diff: {diff}, Size: {size})")

if __name__ == "__main__":
    analyze_density_symmetry()
