from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np

def check_middle_fidelity():
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
    
    pivot = 43
    
    # U1: 0 to pivot
    qc1 = QuantumCircuit(n)
    for t, inst in layer_insts:
        if t <= pivot:
            qc1.append(inst.operation, inst.qubits)
            
    # U2_inv: Inverse of [pivot+1 to end]
    qc2 = QuantumCircuit(n)
    for t, inst in layer_insts:
        if t > pivot:
            qc2.append(inst.operation, inst.qubits)
    qc2_inv = qc2.inverse()
    
    print(f"U1 Gates: {len(qc1.data)}, U2_inv Gates: {len(qc2_inv.data)}")
    
    # Simulate both and check marginals as a proxy for fidelity (easier than statevector at 56Q)
    sim = AerSimulator(method='matrix_product_state', matrix_product_state_max_bond_dimension=32)
    
    def get_marginals(qc):
        qc_m = qc.copy()
        qc_m.measure_all()
        job = sim.run(transpile(qc_m, sim), shots=1000)
        counts = job.result().get_counts()
        
        # Calculate <Zi> for each qubit
        z_exps = np.zeros(n)
        for bitstring, count in counts.items():
            for i, bit in enumerate(bitstring[::-1]): # bit 0 is at the end of the string
                z_exps[i] += (1 if bit == '0' else -1) * count
        return z_exps / 1000

    print("Simulating U1 marginals...")
    m1 = get_marginals(qc1)
    print("Simulating U2_inv marginals...")
    m2 = get_marginals(qc2_inv)
    
    # Correlation between marginals
    corr = np.corrcoef(m1, m2)[0, 1]
    mse = np.mean((m1 - m2)**2)
    
    print(f"\nMarginal Correlation: {corr:.4f}")
    print(f"Marginal MSE: {mse:.4f}")
    
    match_count = sum(1 for i in range(n) if np.sign(m1[i]) == np.sign(m2[i]) and abs(m1[i]) > 0.1)
    significant = sum(1 for i in range(n) if abs(m1[i]) > 0.1)
    print(f"Sign Match on Significant Marginals: {match_count}/{significant}")

if __name__ == "__main__":
    check_middle_fidelity()
