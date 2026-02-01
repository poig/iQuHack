import pyzx as zx
from qiskit import QuantumCircuit, transpile, qasm2
from qiskit_aer import AerSimulator
import json
import argparse
import sys

# P9: Grand Summit
TARGET_QASM = "challenge/P9_grand_summit.qasm"
OUTPUT_FILE = "results/final_P9.json"

def solve_p9():
    print(f"\n=== Solving P9 (Hybrid PyZX + Approx + MPO) ===")
    
    # 1. PyZX Reduction
    print("  [1] PyZX Simplification...")
    try:
        qc_orig = QuantumCircuit.from_qasm_file(TARGET_QASM)
        qasm_str = qasm2.dumps(qc_orig)
        g = zx.Circuit.from_qasm(qasm_str).to_graph()
        zx.full_reduce(g)
        circ_reduced = zx.extract_circuit(g)
        qc_zx = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())
        n = qc_zx.num_qubits
        print(f"      Reduced Size: {n} Qubits, {qc_zx.depth()} Depth")
    except Exception as e:
        print(f"      [Error] PyZX failed: {e}")
        return

    # 2. Approximate Transpilation
    # This was the key for P10: Smoothing out the 'knots' (T-gates) slightly allows MPO to converge.
    print("  [2] Approximate Transpilation (degree=0.99)...")
    try:
        # Standard basis for MPO compatibility
        qc_approx = transpile(qc_zx, 
                              basis_gates=['u3', 'cx'], 
                              optimization_level=3, 
                              approximation_degree=0.99)
        print(f"      Transpiled Depth: {qc_approx.depth()}")
    except Exception as e:
        print(f"      [Error] Transpilation failed: {e}")
        return

    # 3. MPO Simulation
    print("  [3] Exact Simulation (MPO) 128bond...")
    sim = AerSimulator(method='matrix_product_state')
    sim.set_options(matrix_product_state_max_bond_dimension=128)
    
    qc_approx.measure_all()
    
    # Analyze top candidates
    job = sim.run(qc_approx, shots=4000)
    result = job.result().get_counts()
    
    # Get top 5 results
    top_results = dict(sorted(result.items(), key=lambda item: item[1], reverse=True)[:5])
    print(f"  [Top Candidates]: {top_results}")
    
    best_str = max(result, key=result.get)
    best_count = result[best_str]
    
    # 4. Save Logic (Assuming correct endianness from PyZX)
    # P10 solution was valid as-is from the output.
    
    print(f"  *** POTENTIAL SOLUTION: {best_str} (Count: {best_count}) ***")
    
    output_data = {
        "bitstring": best_str,
        "counts": top_results,
        "method": "PyZX + Approx(0.99) + MPO"
    }
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output_data, f)
    print(f"      Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    solve_p9()
