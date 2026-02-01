from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np

def check_marginal_distribution():
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
    print("Simulating U2_inv marginals...")
    m2 = get_marginals(qc2_inv)
    
    # Sort marginals to check for permutation
    s1 = np.sort(m1)
    s2 = np.sort(m2)
    
    dist_mse = np.mean((s1 - s2)**2)
    print(f"\nSorted Marginal MSE: {dist_mse:.4f}")
    
    print("\nTop 10 Marginals H1 vs H2:")
    for i in range(10):
        print(f"  {s1[-(i+1)]:+.3f} vs {s2[-(i+1)]:+.3f}")

if __name__ == "__main__":
    check_marginal_distribution()
