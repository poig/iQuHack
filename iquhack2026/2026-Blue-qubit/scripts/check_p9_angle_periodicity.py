from qiskit import QuantumCircuit
from collections import defaultdict
import numpy as np

def check_angle_periodicity():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc.num_qubits
    
    qubit_time = [0] * n
    layer_params = defaultdict(list)
    
    for instruction in qc.data:
        qargs = [qc.find_bit(q).index for q in instruction.qubits]
        start_time = max(qubit_time[i] for i in qargs)
        duration = 1
        for i in qargs:
            qubit_time[i] = start_time + duration
        
        if instruction.name == 'u3':
            layer_params[start_time].extend(instruction.params)
            
    # Check for period 2 similarity
    times = sorted(layer_params.keys())
    for t in times[:-2]:
        if t in layer_params and (t+2) in layer_params:
            p1 = np.array(layer_params[t])
            p2 = np.array(layer_params[t+2])
            if len(p1) == len(p2):
                diff = np.mean(np.abs(p1 - p2))
                if diff < 1e-5:
                    print(f"Layer {t} and {t+2} have IDENTICAL angles!")
                else:
                    print(f"Layer {t} and {t+2} angles differ by {diff:.4f}")

if __name__ == "__main__":
    check_angle_periodicity()
