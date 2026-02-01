from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np

def verify_core_zero():
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
    
    qc_core = QuantumCircuit(n)
    for t, inst in layer_insts:
        if 40 <= t <= 52:
            qc_core.append(inst.operation, inst.qubits)
            
    sim = AerSimulator(method='matrix_product_state')
    
    qc = QuantumCircuit(n)
    # Input |00..0>
    qc.append(qc_core, range(n))
    qc.measure_all()
    
    qc = transpile(qc, sim)
    result = sim.run(qc, shots=10).result().get_counts()
    
    print("Core output on |0...0>:")
    for k, v in result.items():
        print(f"  {k}: {v}")
        
    # Check if peak
    if len(result) == 1:
        print("Core is deterministic on |0>!")
    else:
        print(f"Core is entangled/superposition on |0> (Entropy > 0).")

if __name__ == "__main__":
    verify_core_zero()
