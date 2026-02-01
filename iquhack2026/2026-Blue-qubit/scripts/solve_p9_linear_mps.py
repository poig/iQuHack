from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import json
import os
import time

TARGET_QASM = "challenge/P9_grand_summit.qasm"

def solve_linear_mps():
    print(f"--- Solving P9 with Linear MPS (Forced Topology) ---")
    
    # 1. Load
    qc = QuantumCircuit.from_qasm_file(TARGET_QASM)
    qc.remove_final_measurements(inplace=True)
    qc.measure_all()
    
    n = qc.num_qubits
    print(f"Qubits: {n}")
    
    # 2. Define Linear Coupling Map (0-1-2-...-55)
    # MPS simulator is optimized for 1D chains.
    coupling_map = [[i, i+1] for i in range(n-1)] + [[i+1, i] for i in range(n-1)]
    
    print("Transpiling to Linear Chain (Optimization Level 3)...")
    # Using 'approxiation_degree' here? 
    # Maybe 0.99 to help simplify, but let's stick to exact logic 
    # but approximate SIMULATION (bond dim).
    
    qc_trans = transpile(qc, 
                         coupling_map=coupling_map, 
                         optimization_level=3)
                         
    print(f"Transpiled Depth: {qc_trans.depth()}")
    print(f"Transpiled Ops: {qc_trans.count_ops()}")

    # 3. Simulate
    # Try Bond Dim 64 this time? Or Stick to 32?
    # If linear layout is good, 64 is cheaper than 32 on bad layout.
    BOND_DIM = 128 # Reduced to 128 for guaranteed completion
    print(f"Running MPS (Bond Dim={BOND_DIM})...")
    
    sim = AerSimulator(method='matrix_product_state', 
                       matrix_product_state_max_bond_dimension=BOND_DIM)
                       
    start_t = time.time()
    result = sim.run(qc_trans, shots=1000).result()
    print(f"Simulation done in {time.time() - start_t:.2f}s")
    
    counts = result.get_counts()
    
    # 4. Analyze Marginals
    # Same logic as before
    total = sum(counts.values())
    z_exp = {i: 0.0 for i in range(n)}
    
    for bitstr, count in counts.items():
        # bitstr is reversed (q55...q0)
        # char at k is qubit (n-1-k)
        for k, char in enumerate(bitstr):
            idx = n - 1 - k
            val = 1 if char == '0' else -1
            z_exp[idx] += val * count
            
    for i in range(n):
        z_exp[i] /= total
        
    print("\nHigh Confidence Qubits:")
    low_conf_count = 0
    bits = ['?'] * n
    
    for i in range(n):
        val = z_exp[i]
        bit = '1' if val < 0 else '0'
        bits[i] = bit
        if abs(val) > 0.3:
            print(f"  Q{i}: {bit} ({val:.3f})")
        else:
            low_conf_count += 1
            
    print(f"\nLow Confidence Qubits (<0.3): {low_conf_count}")
    
    final_str = "".join(list(reversed(bits)))
    print(f"\nCandidate: {final_str}")
    
    with open("p9_candidate_linear.txt", "w") as f:
        f.write(final_str)

if __name__ == "__main__":
    solve_linear_mps()
