import json
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import numpy as np

def inverse_peeling():
    # Load candidate from results/final_P9.json
    try:
        with open("results/final_P9.json", "r") as f:
            data = json.load(f)
        
        # Reconstruct bitstring (q55...q0)
        bits = ['?'] * 56
        for k, v in data.items():
            if k.isdigit():
                bits[int(k)] = v['bit']
        cand_str = "".join(list(reversed(bits)))
    except Exception as e:
        print(f"Error loading candidate: {e}")
        return
    
    print(f"Current Candidate: {cand_str}")
    n = len(cand_str)
    
    # Original circuit
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    
    # Construct inverse circuit with state initialization
    # Note: Applying U^dagger to |x> and checking if it reaches |0>
    # is equivalent to checking if U|0> matches |x>.
    
    # To check U|0> matches |x>, we can just run U and measure expectation of |x><x|.
    # But since we want to know WHICH bits are wrong, we can:
    # 1. Transform |x> to |0> using a layer of X gates: X^x |x> = |0>
    # 2. Check if (X^x U) |0> = |0>
    # 3. This is equivalent to U|0> bits being measured.
    
    # Actually, the simplest way is to simulate U and get marginals.
    # But MPS might be better if we start from a state?
    
    # Let's just run U with MPS (higher bond dim) and see the marginals.
    # If the candidate bit i is correct, then <Zi> should have the same sign.
    
    sim = AerSimulator(method='matrix_product_state', 
                       matrix_product_state_max_bond_dimension=64)
    
    # Copy circuit and add measures
    qc_sim = qc.copy()
    qc_sim.measure_all()
    
    print("Running MPS simulation (bond_dim=64)...")
    job = sim.run(qc_sim, shots=1024)
    result = job.result()
    counts = result.get_counts()
    
    # Calculate marginals
    z_exp = [0.0] * n
    total = sum(counts.values())
    for b_str, count in counts.items():
        # b_str is q55...q0
        for i in range(n):
            bit = b_str[n-1-i]
            z_exp[i] += (1 if bit == '0' else -1) * count
    
    z_exp = [v/total for v in z_exp]
    
    # Compare with candidate
    new_bits = []
    diffs = []
    for i in range(n):
        bit = '1' if z_exp[i] < 0 else '0'
        new_bits.append(bit)
        if bit != cand_str[n-1-i]:
            diffs.append(i)
            
    new_str = "".join(list(reversed(new_bits)))
    print(f"\nNew Candidate: {new_str}")
    print(f"Flipped Bits: {diffs}")
    
    import os
    os.makedirs("solutions", exist_ok=True)
    with open("solutions/p9_mps_improved.txt", "w") as f:
        f.write(new_str)

if __name__ == "__main__":
    inverse_peeling()
