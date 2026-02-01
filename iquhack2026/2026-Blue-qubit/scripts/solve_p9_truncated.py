from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import json
import time

def solve_truncated():
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
    
    qc_trunc = QuantumCircuit(n)
    for t, inst in layer_insts:
        if t <= 38: # Outer Block 1
            qc_trunc.append(inst.operation, inst.qubits)
            
    qc_trunc.measure_all()
    
    sim = AerSimulator(method='matrix_product_state', matrix_product_state_max_bond_dimension=64)
    print("Running Truncated P9 MPS (Layers 0-38)...")
    start = time.time()
    job = sim.run(transpile(qc_trunc, sim), shots=100)
    counts = job.result().get_counts()
    end = time.time()
    
    print(f"Truncated simulation took {end-start:.2f} seconds.")
    print("Top results:")
    for k, v in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"{k}: {v}")

if __name__ == "__main__":
    solve_truncated()
