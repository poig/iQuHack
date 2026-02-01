import pyzx as zx
from qiskit import QuantumCircuit, transpile, qasm2
from qiskit_aer import AerSimulator
import json
import argparse
import sys

PPS_PATH = "results/pps_P10.json"
QASM_PATH = "challenge/P10_eternal_mountain.qasm"

def verify_candidate(candidate_str):
    print(f"\n=== Verifying Candidate for P10 ===")
    print(f"Candidate: {candidate_str}")
    n = len(candidate_str)
    
    # 1. PPS Check
    print("\n[1] Checking Pre-Processing Constraints (PPS)...")
    try:
        with open(PPS_PATH, "r") as f:
            pps_data = json.load(f)
        
        violations = 0
        for q_idx_str, data in pps_data.items():
            q_int = int(q_idx_str)
            required_val = data["bit"]
            
            # String is q_N-1 ... q_0
            # So q_int is at index (N - 1 - q_int)
            str_idx = n - 1 - q_int
            actual_val = candidate_str[str_idx]
            
            if actual_val != required_val:
                print(f"  [VIOLATION] Q{q_int}: Requires {required_val}, Found {actual_val}")
                violations += 1
            else:
                # print(f"  [OK] Q{q_int} == {actual_val}")
                pass
                
        if violations == 0:
            print("  [SUCCESS] Match! Algorithm matches all PPS constraints.")
        else:
            print(f"  [FAIL] Found {violations} PPS violations.")
            
    except Exception as e:
        print(f"  [Warning] Could not check PPS: {e}")

    # 2. Inverse Circuit Check
    print("\n[2] Inverse Circuit Zero-Check (Inverse MPO)...")
    try:
        # Load circuit
        print("  Loading and Reducing...")
        qc_orig = QuantumCircuit.from_qasm_file(QASM_PATH)
        qasm_str = qasm2.dumps(qc_orig)
        g = zx.Circuit.from_qasm(qasm_str).to_graph()
        zx.full_reduce(g)
        circ_reduced = zx.extract_circuit(g)
        qc_zx = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())
        
        # Invert it
        print("  Inverting Circuit...")
        qc_inverse = qc_zx.inverse()
        
        # Prepare state: Apply X gates where candidate is '1'
        # To make state |candidate>
        qc_verify = QuantumCircuit(n)
        
        # Careful with endianness. 
        # candidate_str[0] is q_N-1
        # candidate_str[k] is q_N-1-k
        
        for k, char in enumerate(candidate_str):
            if char == '1':
                # Apply X to physical qubit N-1-k
                qc_verify.x(n - 1 - k)
                
        # Append Inverse
        qc_verify.compose(qc_inverse, inplace=True)
        qc_verify.measure_all()
        
        # Simulate
        sim = AerSimulator(method='matrix_product_state')
        sim.set_options(matrix_product_state_max_bond_dimension=64)
        
        print("  Simulating Inverse Evolution...")
        job = sim.run(qc_verify, shots=1000)
        counts = job.result().get_counts()
        
        # We want "00...0"
        ideal_str = "0" * n
        zero_count = counts.get(ideal_str, 0)
        
        print(f"  Count of |00...0>: {zero_count} / 1000")
        
        if zero_count > 50: # Threshold for noisy MPO
            print("  [VERIFIED] Inverse evolves significantly to ground state.")
        else:
            print("  [FAIL] Inverse does not return to zero. Candidate is likely wrong.")
            top = max(counts, key=counts.get)
            print(f"  Most common result: {top} ({counts[top]})")

    except Exception as e:
        print(f"  [Error] Verification failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=str)
    args = parser.parse_args()
    verify_candidate(args.candidate)
