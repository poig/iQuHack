import bluequbit
from qiskit import QuantumCircuit
import json
import os
import time

TOKEN = "API_here"
bq = bluequbit.init(TOKEN)

TARGET_QASM = "challenge/P9_grand_summit.qasm"

def run_on_cloud():
    print(f"--- Running P9 on BlueQubit Cloud ---")
    qc = QuantumCircuit.from_qasm_file(TARGET_QASM)
    qc.measure_all()
    
    print("Submitting to BlueQubit (Standard Simulator)...")
    # Using 'cpu' or 'gpu' for general simulation.
    # P9 has 56 qubits, so MPS is better. 
    # BlueQubit has 32-qubit statevector, but for >32 we need MPS or similar.
    # Let's try their device-selection or default.
    
    start_t = time.time()
    # Note: bluequbit.run(qc) might default to statevector which fails for 56q.
    # We should specify a backend that handles 56q.
    # Try their managed simulators.
    
    try:
        # Using MPS on Cloud for 56 qubits
        print("Submitting MPS job (Bond Dim 128)...")
        result = bq.run(qc, 
                        device="mps.cpu", 
                        shots=4096, 
                        options={"mps_bond_dimension": 128})
        print(f"Job ID: {result.job_id}")
        
        # Poll
        while True:
            status = bq.get_job_status(result.job_id)
            print(f"Status: {status}")
            if status == "COMPLETED":
                break
            if status == "FAILED":
                print("Job Failed!")
                return
            time.sleep(10)
            
        counts = bq.get_job_results(result.job_id).get_counts()
        best_str = max(counts, key=counts.get)
        print(f"Best: {best_str} (Counts: {counts[best_str]})")
        
        with open("solutions/p9_cloud_result.txt", "w") as f:
            f.write(best_str)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_on_cloud()
