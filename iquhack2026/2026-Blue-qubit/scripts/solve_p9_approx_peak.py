import pyzx as zx
from qiskit import QuantumCircuit, transpile, qasm2
from qiskit_aer import AerSimulator
import json
import os

TARGET_QASM = "challenge/P9_grand_summit.qasm"

def solve_approx():
    print("=== Solving P9 via Aggressive Approximation ===")
    
    # 1. Load
    qc = QuantumCircuit.from_qasm_file(TARGET_QASM)
    print(f"Original Depth: {qc.depth()}")
    
    # 2. PyZX Reduction
    print("Simplifying with PyZX...")
    qasm_str = qasm2.dumps(qc)
    g = zx.Circuit.from_qasm(qasm_str).to_graph()
    zx.full_reduce(g)
    circ_reduced = zx.extract_circuit(g)
    qc_zx = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())
    print(f"Post-PyZX Depth: {qc_zx.depth()}")
    
    # 3. Aggressive Approximation
    # We try different levels if needed. 
    # Let's target a depth where statevector is fast.
    deg = 0.98
    print(f"Applying Qiskit Approximation (degree={deg})...")
    qc_approx = transpile(qc_zx, 
                          basis_gates=['u3', 'cx'], 
                          optimization_level=3, 
                          approximation_degree=deg)
    print(f"Approx Depth: {qc_approx.depth()}")
    
    # 4. Local Simulation
    print("Simulating (MPS Bond Dim 32)...")
    sim = AerSimulator(method='matrix_product_state', 
                       matrix_product_state_max_bond_dimension=32)
    qc_approx.measure_all()
    
    result = sim.run(qc_approx, shots=4096).result()
    counts = result.get_counts()
    
    # Sort and pick best
    top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
    print("\nTop Candidates:")
    for s, c in top:
        print(f"  {s}: {c}")
        
    best_str = top[0][0]
    print(f"\nFinal Solution Candidate: {best_str}")
    
    with open("solutions/p9_approx_solution.txt", "w") as f:
        f.write(best_str)

if __name__ == "__main__":
    solve_approx()
