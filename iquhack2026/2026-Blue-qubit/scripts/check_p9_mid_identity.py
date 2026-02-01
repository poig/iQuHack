import pyzx as zx
from qiskit import QuantumCircuit, transpile, qasm2
import numpy as np

def simplify_mid_circuit():
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
    
    pivot = 43
    # Try increasing window sizes
    for w in [5, 10, 15, 20]:
        print(f"\n--- Testing Window Radius {w} (Layers {pivot-w} to {pivot+w}) ---")
        qc_mid = QuantumCircuit(n)
        for t, inst in layer_insts:
            if pivot - w <= t <= pivot + w:
                qc_mid.append(inst.operation, inst.qubits)
        
        orig_gates = len(qc_mid.data)
        print(f"  Original Gates: {orig_gates}")
        
        # 1. Qiskit Approx Transpilation
        qc_tr = transpile(qc_mid, optimization_level=3, approximation_degree=0.99)
        print(f"  Approx Transpile (0.99) Gates: {len(qc_tr.data)}, Depth: {qc_tr.depth()}")
        
        # 2. PyZX Reduction
        try:
            qasm_str = qasm2.dumps(qc_mid)
            c_zx = zx.Circuit.from_qasm(qasm_str)
            g = c_zx.to_graph()
            zx.full_reduce(g)
            c_red = zx.extract_circuit(g)
            print(f"  PyZX Reduction Gates: {len(c_red.gates)}")
            
            # Convert back to check depth
            qc_zx = QuantumCircuit.from_qasm_str(c_red.to_qasm())
            print(f"  PyZX Result Depth: {qc_zx.depth()}")
            
            if qc_zx.depth() < 10:
                print(f"  [!!!] Window {w} successfully collapsed!")
        except Exception as e:
            print(f"  PyZX failed: {e}")

if __name__ == "__main__":
    simplify_mid_circuit()
