import pyzx as zx
from qiskit import QuantumCircuit, transpile, qasm2
import numpy as np

def check_middle_id():
    qc_full = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc_full.num_qubits
    
    # Track layers
    qubit_time = [0] * n
    layer_insts = []
    
    for instruction in qc_full.data:
        qargs = [qc_full.find_bit(q).index for q in instruction.qubits]
        start_time = max(qubit_time[i] for i in qargs)
        duration = 1
        for i in qargs:
            qubit_time[i] = start_time + duration
        layer_insts.append((start_time, instruction))
    
    max_t = max(t for t, _ in layer_insts)
    print(f"Total layers: {max_t}")
    
    # Test different middle ranges
    # Assume 10 layers for R and 10 for P?
    ranges = [(10, 80), (15, 75), (20, 70), (0, 92)]
    
    for start, end in ranges:
        print(f"\n--- Testing Layers {start} to {end} ---")
        qc_sub = QuantumCircuit(n)
        for t, inst in layer_insts:
            if start <= t <= end:
                qc_sub.append(inst.operation, inst.qubits)
        
        orig_gates = len(qc_sub.data)
        print(f"  Original Gates: {orig_gates}")
        
        # Aggressive transpilation
        qc_tr = transpile(qc_sub, optimization_level=3, approximation_degree=0.99)
        print(f"  Approx Transpile (0.99) Gates: {len(qc_tr.data)}, Depth: {qc_tr.depth()}")
        
        # Check if depth is remarkably small
        if qc_tr.depth() < orig_gates / 10:
             print(f"  [SIGNAL] Significant depth reduction detected at {start}-{end}!")

if __name__ == "__main__":
    check_middle_id()
