from qiskit import QuantumCircuit
import numpy as np
from collections import defaultdict

def check_param_mirror():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc.num_qubits
    
    q_t = [0] * n
    layer_params = defaultdict(dict) # time -> qubit -> params
    
    for instruction in qc.data:
        qargs = [qc.find_bit(q).index for q in instruction.qubits]
        start_time = max(q_t[i] for i in qargs)
        for i in qargs:
            q_t[i] = start_time + 1
            
        if instruction.name == 'u3':
            q = qargs[0]
            layer_params[start_time][q] = np.array(instruction.params)
            
    # Scrambling Map S from L39 -> L53
    S = {
        0: 12, 1: 23, 2: 34, 3: 21, 4: 3, 5: 10, 6: 5, 7: 7, 8: 13, 9: 9, 
        10: 14, 11: 45, 12: 2, 13: 46, 14: 15, 15: 8, 16: 31, 17: 28, 18: 42, 19: 17, 
        20: 41, 21: 48, 22: 22, 23: 1, 24: 38, 25: 32, 26: 29, 27: 49, 28: 0, 29: 19, 
        30: 51, 31: 16, 32: 20, 33: 27, 34: 36, 35: 40, 36: 39, 37: 4, 38: 6, 39: 52, 
        40: 24, 41: 54, 42: 26, 43: 11, 44: 30, 45: 55, 46: 53, 47: 33, 48: 18, 49: 25, 
        50: 35, 51: 37, 52: 43, 53: 47, 54: 50, 55: 44
    }
    
    pivot = 46
    for k in range(0, 45):
        t1 = pivot - k
        t2 = pivot + k
        if t1 in layer_params and t2 in layer_params:
            p1_dict = layer_params[t1]
            p2_dict = layer_params[t2]
            
            matches = 0
            adjs = 0
            total = 0
            for q, p1 in p1_dict.items():
                sq = S.get(q)
                if sq is not None and sq in p2_dict:
                    p2 = p2_dict[sq]
                    total += 1
                    # Identity
                    if np.allclose(p1, p2, atol=1e-2):
                        matches += 1
                    # Adjoint: U3(th, ph, lam)^dag = U3(-th, -lam, -ph)
                    # We check if p2 approximates [-th, -lam, -ph]
                    p1_dag = np.array([-p1[0], -p1[2], -p1[1]])
                    if np.allclose(p1_dag, p2, atol=1e-2):
                        adjs += 1
            
            if matches > 0 or adjs > 0:
                print(f"Dist {k} (Layers {t1}, {t2}): {matches} matches, {adjs} adjoints / {total} pairs.")

if __name__ == "__main__":
    check_param_mirror()
