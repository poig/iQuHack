from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np

def check_core_minus_46():
    qc_full = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc_full.num_qubits
    
    q_t = [0] * n
    layer_insts = []
    
    for instruction in qc_full.data:
        qargs = [qc_full.find_bit(q).index for q in instruction.qubits]
        start_time = max(q_t[i] for i in qargs)
        duration = 1
        for i in qargs:
            q_t[i] = start_time + duration
        layer_insts.append((start_time, instruction))
    
    # Scrambling Map S from L39 -> L53
    S = {
        0: 12, 1: 23, 2: 34, 3: 21, 4: 3, 5: 10, 6: 5, 7: 7, 8: 13, 9: 9, 
        10: 14, 11: 45, 12: 2, 13: 46, 14: 15, 15: 8, 16: 31, 17: 28, 18: 42, 19: 17, 
        20: 41, 21: 48, 22: 22, 23: 1, 24: 38, 25: 32, 26: 29, 27: 49, 28: 0, 29: 19, 
        30: 51, 31: 16, 32: 20, 33: 27, 34: 36, 35: 40, 36: 39, 37: 4, 38: 6, 39: 52, 
        40: 24, 41: 54, 42: 26, 43: 11, 44: 30, 45: 55, 46: 53, 47: 33, 48: 18, 49: 25, 
        50: 35, 51: 37, 52: 43, 53: 47, 54: 50, 55: 44
    }
    
    qc_core = QuantumCircuit(n)
    for t, inst in layer_insts:
        if 40 <= t <= 52 and t != 46:
            qc_core.append(inst.operation, inst.qubits)
            
    sim = AerSimulator(method='matrix_product_state', matrix_product_state_max_bond_dimension=32)
    
    print("Checking Core minus L46 against Permutation S...")
    successes = 0
    trials = 10
    
    for _ in range(trials):
        input_bits = np.random.randint(0, 2, n)
        
        qc = QuantumCircuit(n)
        for i, b in enumerate(input_bits):
            if b: qc.x(i)
            
        qc.append(qc_core, range(n))
        qc.measure_all()
        
        qc = transpile(qc, sim)
        result = sim.run(qc, shots=1).result().get_counts()
        out_str = list(result.keys())[0][::-1] # Little-endian
        
        # Check: Is out_str[S[i]] == input_bits[i]?
        exact = True
        for i in range(n):
            if out_str[S[i]] != str(input_bits[i]):
                exact = False
                break
        if exact:
            successes += 1
            
    print(f"Match Rate: {successes}/{trials}")

if __name__ == "__main__":
    check_core_minus_46()
