from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np

def verify_folded_identity():
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
    
    # Scrambling Map S from previous step
    S = {
        0: 12, 1: 23, 2: 34, 3: 21, 4: 3, 5: 10, 6: 5, 7: 7, 8: 13, 9: 9, 
        10: 14, 11: 45, 12: 2, 13: 46, 14: 15, 15: 8, 16: 31, 17: 28, 18: 42, 19: 17, 
        20: 41, 21: 48, 22: 22, 23: 1, 24: 38, 25: 32, 26: 29, 27: 49, 28: 0, 29: 19, 
        30: 51, 31: 16, 32: 20, 33: 27, 34: 36, 35: 40, 36: 39, 37: 4, 38: 6, 39: 52, 
        40: 24, 41: 54, 42: 26, 43: 11, 44: 30, 45: 55, 46: 53, 47: 33, 48: 18, 49: 25, 
        50: 35, 51: 37, 52: 43, 53: 47, 54: 50, 55: 44
    }
    
    # Layers to skip: 40 to 52 (inclusive)
    # The map S takes state at end of L39 (input to 40) to state at start of L53?
    # No, S maps graph of L39 to graph of L53. 
    # This implies U_53 \approx P * U_39 * P^T ? Or U_53 is the time-evolved version.
    
    # Let's test the hypothesis:
    # State_53 = Swap(S) * State_39
    # We evolve to L39, apply Permutation S, then measure overlap with Backward evolution from L92 to L53.
    
    # U1: 0 to 39
    qc1 = QuantumCircuit(n)
    for t, inst in layer_insts:
        if t <= 39:
            qc1.append(inst.operation, inst.qubits)
            
    # U2_inv: Inverse of [53 to end]
    qc2 = QuantumCircuit(n)
    for t, inst in layer_insts:
        if t >= 53:
            qc2.append(inst.operation, inst.qubits)
    qc2_inv = qc2.inverse()
    
    sim = AerSimulator(method='matrix_product_state', matrix_product_state_max_bond_dimension=32)
    
    def get_marginals(qc):
        qc_m = qc.copy()
        qc_m.measure_all()
        job = sim.run(transpile(qc_m, sim), shots=1000)
        counts = job.result().get_counts()
        z_exps = np.zeros(n)
        for bitstring, count in counts.items():
            for i, bit in enumerate(bitstring[::-1]):
                z_exps[i] += (1 if bit == '0' else -1) * count
        return z_exps / 1000

    print("Simulating U1 marginals...")
    m1 = get_marginals(qc1)
    
    # Apply Permutation S to m1
    m1_permuted = np.zeros(n)
    for i in range(n):
        if i in S:
            m1_permuted[S[i]] = m1[i]
        else:
            m1_permuted[i] = 0 # Should not happen
            
    print("Simulating U2_inv marginals...")
    m2 = get_marginals(qc2_inv)
    
    # Check correlation
    corr = np.corrcoef(m1_permuted, m2)[0, 1]
    mse = np.mean((m1_permuted - m2)**2)
    
    print(f"\nPermuted Marginal Correlation: {corr:.4f}")
    print(f"Permuted Marginal MSE: {mse:.4f}")

if __name__ == "__main__":
    verify_folded_identity()
