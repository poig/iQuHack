from qiskit import QuantumCircuit
import numpy as np

def check_outer_inverse():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    
    # Outer 1: 0-39. Outer 2: 53-92.
    # Check if L(53) relates to L(39)?
    # Or L(53) relates to L(0)?
    # "Palindrome" means L(53) ~ L(39), L(54) ~ L(38)...
    # "Shift" means L(53) ~ L(0), L(54) ~ L(1)...
    
    # We checked L38 vs L54 earlier (Palindrome). It failed.
    # Let's check Shift: L53 vs L0. Or L53 vs L1 (since Period 2).
    
    # Extract params
    layer_params = {}
    q_t = [0] * qc.num_qubits
    for inst in qc.data:
        qargs = [qc.find_bit(q).index for q in inst.qubits]
        start_time = max(q_t[i] for i in qargs)
        for i in qargs: q_t[i] = start_time + 1
        if inst.name == 'u3':
            if start_time not in layer_params: layer_params[start_time] = []
            layer_params[start_time].append(np.array(inst.params))
            
    # Check correlation between Layer t and Layer t+53?
    # No, check block vs block.
    # Block 1: 0..39. Block 2: 53..92.
    # Let's compare sets of parameters.
    
    params1 = []
    for t in range(40):
        if t in layer_params: 
            for p in layer_params[t]: params1.append(p)
            
    params2 = []
    for t in range(53, 93):
        if t in layer_params:
            for p in layer_params[t]: params2.append(p)
            
    # Are they the same set?
    p1_flat = np.concatenate(params1) if params1 else []
    p2_flat = np.concatenate(params2) if params2 else []
    
    print(f"Block 1 Params Mean: {np.mean(p1_flat):.4f}, Std: {np.std(p1_flat):.4f}")
    print(f"Block 2 Params Mean: {np.mean(p2_flat):.4f}, Std: {np.std(p2_flat):.4f}")
    
    # Check reverse?
    
if __name__ == "__main__":
    check_outer_inverse()
