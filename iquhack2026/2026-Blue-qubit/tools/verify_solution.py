import pyzx as zx
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import json
import argparse
import sys

def verify_candidate(candidate_str, qasm_path, pps_path=None):
    print(f"\n=== Verifying Candidate for {qasm_path} ===")
    print(f"Candidate: {candidate_str}")
    n = len(candidate_str)
    
    # 1. PPS Check (Optional)
    if pps_path:
        print("\n[1] Checking PPS Constraints...")
        try:
            with open(pps_path, "r") as f:
                pps_data = json.load(f)
            
            violations = 0
            for q_idx_str, data in pps_data.items():
                q_int = int(q_idx_str)
                required_val = data["bit"]
                str_idx = n - 1 - q_int
                actual_val = candidate_str[str_idx]
                
                if actual_val != required_val:
                    print(f"  [VIOLATION] Q{q_int}: Requires {required_val}, Found {actual_val}")
                    violations += 1
            if violations == 0:
                print("  [SUCCESS] PPS constraints satisfied.")
            else:
                print(f"  [FAIL] {violations} violations found.")
        except Exception as e:
            print(f"  [Warning] PPS check skipped: {e}")

    # 2. Inverse Check
    print("\n[2] Inverse Circuit Ground-State Check...")
    try:
        qc_orig = QuantumCircuit.from_qasm_file(qasm_path)
        # Simplify before inverting to handle large circuits
        print("  Simplifying with PyZX...")
        g = zx.Circuit.from_qasm_file(qasm_path).to_graph()
        zx.full_reduce(g)
        qc_zx = QuantumCircuit.from_qasm_str(zx.extract_circuit(g).to_qasm())
        
        qc_inverse = qc_zx.inverse()
        qc_verify = QuantumCircuit(n)
        for k, char in enumerate(candidate_str):
            if char == '1':
                qc_verify.x(n - 1 - k)
        
        qc_verify.compose(qc_inverse, inplace=True)
        qc_verify.measure_all()
        
        sim = AerSimulator(method='matrix_product_state')
        print("  Simulating (BD=64)...")
        job = sim.run(qc_verify, shots=1000)
        counts = job.result().get_counts()
        
        zero_str = "0" * n
        score = counts.get(zero_str, 0)
        print(f"  Result 0...0 count: {score}/1000")
        if score > 50:
            print("  [VERIFIED] Candidate correctly returns to ground state.")
        else:
            print("  [FAIL] Low ground-state overlap.")
            top = max(counts, key=counts.get)
            print(f"  Top result: {top} ({counts[top]})")
            
    except Exception as e:
        print(f"  [Error] Verification failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", help="Bitstring to verify")
    parser.add_argument("--qasm", required=True, help="Path to QASM file")
    parser.add_argument("--pps", help="Optional path to PPS results JSON")
    args = parser.parse_args()
    verify_candidate(args.candidate, args.qasm, args.pps)
