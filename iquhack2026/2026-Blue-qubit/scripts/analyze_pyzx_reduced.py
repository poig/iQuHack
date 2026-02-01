import pyzx as zx
from qiskit import QuantumCircuit, qasm2
import numpy as np

def analyze_reduced_structure():
    path = "challenge/P9_grand_summit.qasm"
    print("Simplifying P9 with PyZX...")
    
    qc_orig = QuantumCircuit.from_qasm_file(path)
    qasm_str = qasm2.dumps(qc_orig)
    g = zx.Circuit.from_qasm(qasm_str).to_graph()
    zx.full_reduce(g)
    circ_reduced = zx.extract_circuit(g)
    
    qc_zx = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())
    
    print(f"\nOriginal Gates: {len(qc_orig.data)}")
    print(f"Reduced Gates: {len(qc_zx.data)}")
    print(f"Reduced Depth: {qc_zx.depth()}")
    
    # Inspect remaining gates
    print("\nGate Counts in Reduced Circuit:")
    gate_counts = {}
    for inst in qc_zx.data:
        name = inst.operation.name
        gate_counts[name] = gate_counts.get(name, 0) + 1
    print(gate_counts)
    
    # Check for non-Clifford gates (RZ with non-pi/2 angles)
    print("\nAnalyzing non-Clifford rotations:")
    count_irrational = 0
    for inst in qc_zx.data:
        if inst.operation.name in ['rx', 'ry', 'rz', 'u3']:
            params = inst.operation.params
            is_cliff = True
            for p in params:
                 ratio = p / (np.pi/2)
                 if abs(ratio - round(ratio)) > 1e-4:
                     is_cliff = False
            if not is_cliff:
                count_irrational += 1
                q_indices = [q._index for q in inst.qubits]
                print(f"  Non-Clifford {inst.operation.name} on {q_indices}: {np.round(params, 3)}")
                
    print(f"\nTotal Non-Clifford Gates: {count_irrational}")

if __name__ == "__main__":
    analyze_reduced_structure()
