from qiskit import QuantumCircuit
from collections import defaultdict
import numpy as np

def is_rational_pi(val, tol=1e-5):
    # check if val / (pi/2) is close to an integer
    ratio = val / (np.pi / 2)
    return abs(ratio - round(ratio)) < tol

def find_transition():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    qubit_time = [0] * qc.num_qubits
    
    layer_rationality = {} # layer -> float (fraction of rational params)
    
    layer_params = defaultdict(list)
    
    for instruction in qc.data:
        qargs = [qc.find_bit(q).index for q in instruction.qubits]
        start_time = max(qubit_time[i] for i in qargs)
        duration = 1
        for i in qargs:
            qubit_time[i] = start_time + duration
        
        if instruction.name == 'u3':
            layer_params[start_time].extend(instruction.params)
            
    times = sorted(layer_params.keys())
    for t in times:
        params = layer_params[t]
        if not params:
            continue
        rat_count = sum(1 for p in params if is_rational_pi(p))
        score = rat_count / len(params)
        layer_rationality[t] = score
        print(f"Layer {t:2d}: Rationality Score = {score:.2%}")

if __name__ == "__main__":
    find_transition()
