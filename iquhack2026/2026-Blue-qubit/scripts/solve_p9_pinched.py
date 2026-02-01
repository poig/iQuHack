from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np
import json
import os

def solve_p9_pinched_core():
    # 1. Load Circuit
    qc_full = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc_full.num_qubits
    
    # 2. Extract Outer Blocks
    # Outer 1: Layers 0-39
    # S Permutation: L39 -> L53
    # Outer 2: Layers 53-91
    
    # We construct a new circuit: 
    #   Outer 1 
    #   Permutation S (Simulated by SWAPs or relabeling)
    #   Outer 2
    
    q_t = [0] * n
    layer_insts = []
    
    for instruction in qc_full.data:
        qargs = [qc_full.find_bit(q).index for q in instruction.qubits]
        start_time = max(q_t[i] for i in qargs)
        duration = 1
        for i in qargs:
            q_t[i] = start_time + duration
        layer_insts.append((start_time, instruction))
        
    qc_reduced = QuantumCircuit(n)
    
    # Add Outer 1
    for t, inst in layer_insts:
        if t <= 39:
            qc_reduced.append(inst.operation, inst.qubits)
            
    # Add Permutation S
    # S maps physical qubit `i` at end of L39 to physical qubit `S[i]` at start of L53.
    # We must apply SWAPs to achieve this.
    # However, since we are building the circuit, we can just relabel the qubits for the next part?
    # No, Qiskit appends gates to wires.
    # We need to append SWAP gates to move state on wire `i` to wire `S[i]`.
    # Actually, S maps graph structure. Does it map state?
    # If Core |0> -> |0>, and Core ~ P(S).
    # Then Core maps state |psi> on wire `i` to state |psi> on wire `S[i]`.
    # Let's verify this hypothesis again.
    # Actually, let's just use simple Identity (no permutation) first?
    # Or assuming S is the identity map for the STATE (since S is just graph isomorphism).
    
    S = {
        0: 12, 1: 23, 2: 34, 3: 21, 4: 3, 5: 10, 6: 5, 7: 7, 8: 13, 9: 9, 
        10: 14, 11: 45, 12: 2, 13: 46, 14: 15, 15: 8, 16: 31, 17: 28, 18: 42, 19: 17, 
        20: 41, 21: 48, 22: 22, 23: 1, 24: 38, 25: 32, 26: 29, 27: 49, 28: 0, 29: 19, 
        30: 51, 31: 16, 32: 20, 33: 27, 34: 36, 35: 40, 36: 39, 37: 4, 38: 6, 39: 52, 
        40: 24, 41: 54, 42: 26, 43: 11, 44: 30, 45: 55, 46: 53, 47: 33, 48: 18, 49: 25, 
        50: 35, 51: 37, 52: 43, 53: 47, 54: 50, 55: 44
    }
    
    # We apply Permutation: Q_i -> Q_{S[i]}
    # This means the state on line i moves to line S[i].
    # But wait, Qiskit doesn't support arbitrary permutation instruction easily without decomposition.
    # We can just permute the qubits we attach to for the next block.
    # i.e., Instead of appending next gate to Q_k, we append to Q_{inv_S[k]}?
    # Let's trace it.
    # Output of Outer 1 is on wires 0..55.
    # S says: wire i maps to wire S[i].
    # So we want state on wire i to be on wire S[i].
    # So subsequent gates (Outer 2) expecting input on wire k should now take input from wire inv_S[k]?
    # Wait, if we physically move i to S[i], then wire S[i] holds state from i.
    # If Outer 2 gate acts on qubit `u`, it expects state from Core output `u`.
    # Core output `u` corresponds to Core Input `inv_S[u]`.
    # So we should rewrite Outer 2 to act on `inv_S[u]`.
    
    inv_S = {v: k for k, v in S.items()}
    
    # Add Outer 2 (Rewired)
    for t, inst in layer_insts:
        if t >= 53:
            new_qubits = [qc_reduced.qubits[inv_S[qc_full.find_bit(q).index]] for q in inst.qubits]
            qc_reduced.append(inst.operation, new_qubits)
            
    print(f"Reduced Circuit Gates: {len(qc_reduced.data)} (Original: {len(qc_full.data)})")
    
    # 3. Simulate
    sim = AerSimulator(method='matrix_product_state', matrix_product_state_max_bond_dimension=64) # Increased BD
    qc_reduced.measure_all()
    job = sim.run(transpile(qc_reduced, sim), shots=2000)
    counts = job.result().get_counts()
    
    # 4. Save Results
    os.makedirs("results", exist_ok=True)
    with open("results/p9_reduced_counts.json", "w") as f:
        json.dump(counts, f, indent=2)
        
    print("Top 5 Results:")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for k, v in sorted_counts[:5]:
        print(f"  {k}: {v}")

if __name__ == "__main__":
    solve_p9_pinched_core()
