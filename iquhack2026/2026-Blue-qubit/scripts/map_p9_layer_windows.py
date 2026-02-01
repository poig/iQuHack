from qiskit import QuantumCircuit
import numpy as np

def map_qubit_layers():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    qubit_time = [0] * qc.num_qubits
    
    first_layer = [999] * qc.num_qubits
    last_layer = [0] * qc.num_qubits
    
    for instruction in qc.data:
        qargs = [qc.find_bit(q).index for q in instruction.qubits]
        start_time = max(qubit_time[i] for i in qargs)
        duration = 1
        for i in qargs:
            qubit_time[i] = start_time + duration
            first_layer[i] = min(first_layer[i], start_time)
            last_layer[i] = max(last_layer[i], start_time)
            
    # Print sorted by start layer
    data = []
    for i in range(qc.num_qubits):
        data.append((i, first_layer[i], last_layer[i]))
        
    data.sort(key=lambda x: x[1])
    
    print(f"{'Qubit':<6} {'Start':<6} {'End':<6} {'Span':<6}")
    for q, s, e in data:
        print(f"{q:<6} {s:<6} {e:<6} {e-s:<6}")

if __name__ == "__main__":
    map_qubit_layers()
