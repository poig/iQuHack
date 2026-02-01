import pyzx as zx
from qiskit import QuantumCircuit, transpile, qasm2
import numpy as np

def analyze_hybrid_steps():
    path = "challenge/P9_grand_summit.qasm"
    print("Analyzing Hybrid Pipeline Steps...")
    
    # 1. Original
    qc = QuantumCircuit.from_qasm_file(path)
    print(f"Original: Depth {qc.depth()}, 2Q Gates {qc.num_nonlocal_gates()}")
    
    # 2. PyZX
    qasm_str = qasm2.dumps(qc)
    g = zx.Circuit.from_qasm(qasm_str).to_graph()
    zx.full_reduce(g)
    circ_reduced = zx.extract_circuit(g)
    qc_zx = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())
    print(f"After PyZX: Depth {qc_zx.depth()}, 2Q Gates {qc_zx.num_nonlocal_gates()}")
    
    # 3. Transpile L3
    qc_final = transpile(qc_zx, basis_gates=['u3', 'cx'], optimization_level=3)
    print(f"After Transpile L3: Depth {qc_final.depth()}, 2Q Gates {qc_final.num_nonlocal_gates()}")
    
    # 4. Check Entanglement Structure
    # If 2Q gates > ~400, MPS(128) will struggle
    if qc_final.num_nonlocal_gates() > 400:
        print("[WARNING] High 2Q gate count makes MPS difficult.")
        
    # Check if gates are local (1D chain?)
    # ...

if __name__ == "__main__":
    analyze_hybrid_steps()
