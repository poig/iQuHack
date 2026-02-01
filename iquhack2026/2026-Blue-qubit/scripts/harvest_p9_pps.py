import bluequbit
import json
import os

TOKEN = "API_here"
bq = bluequbit.init(TOKEN)

def harvest():
    print("--- Harvesting P9 PPS Marginals ---")
    
    # Search for all pauli-path jobs
    jobs = bq.search(device="pauli-path")
    print(f"Total PPS jobs found: {len(jobs)}")
    
    results = {}
    for job in jobs:
        # P9 jobs should have 56 qubits and mention Z in their sum?
        # Actually, let's filter by number of qubits and recent timing.
        # The SDK job objects have metadata or qubit_count?
        
        # We can look at the Pauli sum to determine which qubit it was for.
        if job.run_status != "COMPLETED":
            continue
            
        pauli_sum = job.pauli_sum # List of (pauli_str, coeff)
        if not pauli_sum:
            continue
            
        p_str = pauli_sum[0][0]
        if len(p_str) != 56:
            continue
            
        # Check index of 'Z' in p_str
        # Qiskit endianness: q0 is rightmost in p_str if we reversed it.
        # In my script: pauli_str[i] = 'Z' and then reversed.
        # So 'Z' is at index (55 - i).
        # i = 55 - z_index
        
        z_index = p_str.find('Z')
        if z_index == -1:
            continue
            
        qubit_idx = 55 - z_index
        val = job.expectation_value
        bit = '1' if val < 0 else '0'
        
        # Keep the most recent one if duplicates? 
        # For now just store.
        results[qubit_idx] = (bit, val)
        
    print(f"Captured {len(results)}/56 marginals.")
    
    if len(results) == 56:
        bits = [results[i][0] for i in range(56)]
        # Endianness: my results[i] is for q[i].
        # String should be q55 q54 ... q0
        final_str = "".join(list(reversed(bits)))
        print(f"\nRECONSTRUCTED BITSTRING: {final_str}")
        return final_str
    else:
        # Show missing
        missing = [i for i in range(56) if i not in results]
        print(f"Missing Qubits: {missing}")
        return None

if __name__ == "__main__":
    harvest()
