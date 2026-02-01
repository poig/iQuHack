from qiskit import QuantumCircuit
import numpy as np

def compare_outer_params():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc.num_qubits
    
    # Scrambling Map S from L39 -> L53
    S = {
        0: 12, 1: 23, 2: 34, 3: 21, 4: 3, 5: 10, 6: 5, 7: 7, 8: 13, 9: 9, 
        10: 14, 11: 45, 12: 2, 13: 46, 14: 15, 15: 8, 16: 31, 17: 28, 18: 42, 19: 17, 
        20: 41, 21: 48, 22: 22, 23: 1, 24: 38, 25: 32, 26: 29, 27: 49, 28: 0, 29: 19, 
        30: 51, 31: 16, 32: 20, 33: 27, 34: 36, 35: 40, 36: 39, 37: 4, 38: 6, 39: 52, 
        40: 24, 41: 54, 42: 26, 43: 11, 44: 30, 45: 55, 46: 53, 47: 33, 48: 18, 49: 25, 
        50: 35, 51: 37, 52: 43, 53: 47, 54: 50, 55: 44
    }
    
    q_t = [0] * n
    layers = {} # time -> qubit -> params
    
    for instruction in qc.data:
        qargs = [qc.find_bit(q).index for q in instruction.qubits]
        start_time = max(q_t[i] for i in qargs)
        for i in qargs:
            q_t[i] = start_time + 1
            
        if instruction.name == 'u3':
            if start_time not in layers: layers[start_time] = {}
            # Assume 1Q gate
            q = qargs[0]
            layers[start_time][q] = np.array(instruction.params)
            
    # Compare L38 and L54
    # Hypothesis: U3(L54, S[q]) is related to U3(L38, q)
    # E.g. Inverse: theta' = -theta, etc.
    
    t1 = 38
    t2 = 54
    
    print(f"Comparing Layer {t1} and {t2} using Permutation S...")
    
    matches = 0
    inverses = 0
    total = 0
    
    for q in range(n):
        if q not in layers.get(t1, {}) or S[q] not in layers.get(t2, {}):
            continue
            
        p1 = layers[t1][q]
        p2 = layers[t2][S[q]]
        total += 1
        
        # Check Identity
        if np.allclose(p1, p2, atol=1e-4):
            matches += 1
            
        # Check Inverse (Basic U3 inverse check: theta -> -theta, phi -> -lam, lam -> -phi?)
        # U3(th, ph, lam)^dag = U3(-th, -lam, -ph) -- up to global phase.
        # But U3 params are magnitudes? No, angles.
        # Let's check magnitude match.
        if np.allclose(np.abs(p1), np.abs(p2), atol=1e-4):
            inverses += 1
        
    print(f"Total U3 pairs checked: {total}")
    print(f"Exact Matches: {matches}")
    print(f"Magnitude Matches: {inverses}")
    
    if total > 0:
        print(f"Correlation: {matches/total:.2%}")

if __name__ == "__main__":
    compare_outer_params()
