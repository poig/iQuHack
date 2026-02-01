import pyzx as zx
from qiskit import QuantumCircuit, transpile, qasm2
from qiskit_aer import AerSimulator
import time
import json
import os

def solve_p9_hybrid():
    path = "challenge/P9_grand_summit.qasm"
    name = "P9_grand_summit"
    
    print(f"\n--- Hybrid PyZX + Approx Transpilation for {name} ---")
    
    # 1. PyZX Reduction
    print("  [1] PyZX Simplification...")
    qc_orig = QuantumCircuit.from_qasm_file(path)
    
    # Optional: Approx Transpilation BEFORE PyZX to remove tiny noise
    # qc_approx = transpile(qc_orig, optimization_level=3, approximation_degree=0.99)
    # qasm_str = qasm2.dumps(qc_approx)
    
    qasm_str = qasm2.dumps(qc_orig)
    g = zx.Circuit.from_qasm(qasm_str).to_graph()
    zx.full_reduce(g)
    circ_reduced = zx.extract_circuit(g)
    
    # Convert back to Qiskit
    qc_zx = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())
    print(f"  PyZX Result: Depth {qc_zx.depth()}, Qubits {qc_zx.num_qubits}")
    n = qc_zx.num_qubits

    # 2. Exact Simulation of Reduced Circuit
    print("  [2] Exact Simulation of PyZX Circuit (MPO)...")
    
    sim = AerSimulator(method='matrix_product_state')
    sim.set_options(matrix_product_state_max_bond_dimension=128) 
    
    qc_zx.measure_all()
    trans_qc = transpile(qc_zx, basis_gates=['u3', 'cx'], optimization_level=3)
    
    start = time.time()
    job = sim.run(trans_qc, shots=2000)
    result = job.result().get_counts()
    print(f"  Sim time: {time.time()-start:.2f}s")
    
    print(dict(sorted(result.items(), key=lambda item: item[1], reverse=True)[:5]))
    
    # Save raw counts
    os.makedirs("results", exist_ok=True)
    with open(f"results/p9_hybrid_pyzx.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    solve_p9_hybrid()
