import pyzx as zx
from qiskit import QuantumCircuit, transpile, qasm2
import bluequbit
import json
import argparse
import sys
import time

# P9: Grand Summit
TARGET_QASM = "challenge/P9_grand_summit.qasm"
OUTPUT_FILE = "results/final_P9_cloud.json"
TOKEN = "API_here"

def solve_p9_cloud():
    print(f"\n=== Solving P9 (Hybrid PyZX + Approx + Cloud MPS) ===")
    bq = bluequbit.init(TOKEN)
    
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
    print("  [2] Approximate Transpilation (degree=0.99)...")
    try:
        # Standard basis for BlueQubit Cloud (supports u3, cx generally)
        qc_approx = transpile(qc_zx, 
                              basis_gates=['u3', 'cx'], 
                              optimization_level=3, 
                              approximation_degree=0.99)
        print(f"      Transpiled Depth: {qc_approx.depth()}")
    except Exception as e:
        print(f"      [Error] Transpilation failed: {e}")
        return

    # 3. Cloud Submission
    print("  [3] Submitting to REAL Quantum Hardware (device='quantum')...")
    try:
        # Rigetti Ankaa-3 (82 qubits). Cost ~ $0.0009/shot.
        # Depth 83 is noisy, but maybe the peak survives.
        qc_approx.measure_all()
        
        job = bq.run(qc_approx, device="quantum", shots=1000)
        print(f"      Job ID: {job.job_id}")
        print("      Waiting for results...")
        
        result = job.result()
        counts = result.get_counts()
        
        # Get top 5 results
        top_results = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True)[:5])
        print(f"  [Top Candidates]: {top_results}")
        
        best_str = max(counts, key=counts.get)
        best_count = counts[best_str]
        
        print(f"  *** CLOUD SOLUTION: {best_str} (Count: {best_count}) ***")
        
        output_data = {
            "bitstring": best_str,
            "counts": top_results,
            "method": "PyZX + Approx(0.99) + Cloud MPS"
        }
        
        with open(OUTPUT_FILE, "w") as f:
            json.dump(output_data, f)
        print(f"      Saved to {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"      [Error] Cloud Experiment failed: {e}")

if __name__ == "__main__":
    solve_p9_cloud()
