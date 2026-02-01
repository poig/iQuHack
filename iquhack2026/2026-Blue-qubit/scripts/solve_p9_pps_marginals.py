import bluequbit
from qiskit import QuantumCircuit
import json
import os
import time
import numpy as np

TOKEN = "API_here"
bq = bluequbit.init(TOKEN)

TARGET_QASM = "challenge/P9_grand_summit.qasm"

def get_marginals():
    print("--- Solving P9 via PPS Marginals ---")
    qc = QuantumCircuit.from_qasm_file(TARGET_QASM)
    n = qc.num_qubits
    
    # Construct Z observables for all qubits
    # Qiskit endianness: q0 is rightmost.
    Z_ops = []
    for i in range(n):
        pauli_str = ['I'] * n
        pauli_str[i] = 'Z'
        pauli_str = "".join(list(reversed(pauli_str))) # Match Qiskit endianness
        Z_ops.append([(pauli_str, 1.0)])

    # Batch submission? The SDK might support a list of pauli_sums.
    # The tutorial used a loop.
    
    bits = ['?'] * n
    exp_vals = {}
    
    pps_options = {
        "pauli_path_truncation_threshold": 5e-3, # Slightly more precision than tutorial
        "pauli_path_circuit_transpilation_level": 3,
    }
    
    print(f"Submitting {n} PPS jobs...")
    
    jobs = []
    for i in range(n):
        # Use asynchronous=True to submit quickly
        job = bq.run(qc, device="pauli-path", pauli_sum=Z_ops[i], options=pps_options, asynchronous=True)
        jobs.append((i, job))
        print(f"  Submitted Q{i} (ID={job.job_id[-4:]})")
    
    print("\nAll jobs submitted. Polling...")
    
    results_map = {}
    while len(results_map) < n:
        for i, job in jobs:
            if i in results_map:
                continue
            
            # Since asynchronous=True, the job object has job_id
            # We can use bq.get_job_status or bq.wait
            # Note: The search in previous step said bq.get_job_status might not exist on BQClient?
            # Let's try to access job.status if possible, or use search.
            try:
                # Assuming the job object itself might have status if we poll result?
                # Let's check the SDK logic from search: "Initially JobResult contains job_id"
                # Actually, let's use search(job_id=job.job_id) or just try bq.wait(job.job_id, timeout=0)
                # Let's try a safer way:
                job_info = bq.search(job_id=job.job_id)[0]
                status = job_info.run_status
            except:
                continue

            if status == "COMPLETED":
                res = bq.wait(job.job_id)
                val = res.expectation_value
                bit = '1' if val < 0 else '0'
                results_map[i] = {"bit": bit, "val": val}
                print(f"  Q{i}: {bit} (val={val:.4f})")
            elif status == "FAILED":
                print(f"  Q{i} FAILED!")
                results_map[i] = {"bit": "?", "val": 0.0}
        
        if len(results_map) < n:
            time.sleep(10)

    # Reconstruct
    final_bits = [results_map[i]['bit'] for i in range(n)]
    final_str = "".join(list(reversed(final_bits)))
    print(f"\n[PPS SOLUTION]: {final_str}")
    
    with open("solutions/p9_pps_solution.txt", "w") as f:
        f.write(final_str)

if __name__ == "__main__":
    get_marginals()
