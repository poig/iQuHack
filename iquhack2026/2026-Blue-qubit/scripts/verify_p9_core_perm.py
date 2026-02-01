from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np

def verify_core_reversal():
    qc_full = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc_full.num_qubits
    
    # Track layers
    qubit_time = [0] * n
    layer_insts = []
    
    for instruction in qc_full.data:
        qargs = [qc_full.find_bit(q).index for q in instruction.qubits]
        start_time = max(qubit_time[i] for i in qargs)
        duration = 1
        for i in qargs:
            qubit_time[i] = start_time + duration
        layer_insts.append((start_time, instruction))
    
    S = {
        0: 12, 1: 23, 2: 34, 3: 21, 4: 3, 5: 10, 6: 5, 7: 7, 8: 13, 9: 9, 
        10: 14, 11: 45, 12: 2, 13: 46, 14: 15, 15: 8, 16: 31, 17: 28, 18: 42, 19: 17, 
        20: 41, 21: 48, 22: 22, 23: 1, 24: 38, 25: 32, 26: 29, 27: 49, 28: 0, 29: 19, 
        30: 51, 31: 16, 32: 20, 33: 27, 34: 36, 35: 40, 36: 39, 37: 4, 38: 6, 39: 52, 
        40: 24, 41: 54, 42: 26, 43: 11, 44: 30, 45: 55, 46: 53, 47: 33, 48: 18, 49: 25, 
        50: 35, 51: 37, 52: 43, 53: 47, 54: 50, 55: 44
    }
    
    # Core block: 40 to 52
    qc_core = QuantumCircuit(n)
    for t, inst in layer_insts:
        if 40 <= t <= 52:
            qc_core.append(inst.operation, inst.qubits)
            
    print(f"Core Block Gates: {len(qc_core.data)}")
    
    # Simulating core block on random input
    sim = AerSimulator(method='matrix_product_state', matrix_product_state_max_bond_dimension=32)
    
    # 1. Random Input |psi>
    # 2. Apply Core
    # 3. Apply S_inverse (or S?)
    # 4. Measure
    
    # S maps FROM 39 TO 53.
    # So Output Qubit q came from Input Qubit S_inv[q] ?
    # Let's assume Output[S[i]] should match Input[i]
    
    successes = 0
    trials = 10
    for _ in range(trials):
        input_bits = np.random.randint(0, 2, n)
        input_str = "".join(map(str, input_bits)) # Big-endian for comparison? careful
        
        qc = QuantumCircuit(n)
        for i, b in enumerate(input_bits):
            if b: qc.x(i)
            
        qc.append(qc_core, range(n))
        qc.measure_all()
        
        qc = transpile(qc, sim)
        result = sim.run(qc, shots=1).result().get_counts()
        out_str = list(result.keys())[0][::-1] # Little-endian now
        
        # Check permutation
        permuted_out = ['?'] * n
        for i in range(n):
            # If S maps input i to output S[i]
            # Then permuted_out[S[i]] should be out_str[S[i]]
            # We want to check if out_str[S[i]] == input_str[i]
            if out_str[S[i]] == str(input_bits[i]):
                pass
            
        exact = True
        for i in range(n):
            if out_str[S[i]] != str(input_bits[i]):
                exact = False
                break
        if exact:
            successes += 1
            
    print(f"Core Block acts as P(S) on {successes}/{trials} random states.")

if __name__ == "__main__":
    verify_core_reversal()
