from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np

def profile_bond_dimension():
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
    
    max_t = max(t for t, _ in layer_insts)
    
    # We want to check bond dim at different t.
    # Qiskit Aer doesn't give us the bond dim during simulation easily.
    # We will simulate prefixes of length T.
    
    sim = AerSimulator(method='matrix_product_state', matrix_product_state_max_bond_dimension=256)
    
    print(f"{'Layer':<6} {'BondDim':<10}")
    for t_step in range(0, max_t + 1, 10):
        qc_t = QuantumCircuit(n)
        for t, inst in layer_insts:
            if t <= t_step:
                qc_t.append(inst.operation, inst.qubits)
        
        # We need a way to extract bond dimension. 
        # One way is to check the size of the result metadata if available.
        # Another is to check if it converges or fails.
        
        # Actually, let's just use the 'val' of a marginal as a proxy for 'Simulability'.
        # If BondDim is too low, val will be 0 or garbage.
        
        # Better: use a local library or just trust the 'Identiy' hypothesis for now if we see a 
        # bitstring that is 000... or similar.
        
        print(f"Layer {t_step:2d}: [Simulating...]")
        # (Simulation code here)

if __name__ == "__main__":
    profile_bond_dimension()
