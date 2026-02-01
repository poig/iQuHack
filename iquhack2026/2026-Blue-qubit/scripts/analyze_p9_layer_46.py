from qiskit import QuantumCircuit
import numpy as np

def analyze_layer_46():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc.num_qubits
    
    qubit_time = [0] * n
    layer_insts = []
    
    for instruction in qc.data:
        qargs = [qc.find_bit(q).index for q in instruction.qubits]
        start_time = max(qubit_time[i] for i in qargs)
        duration = 1
        for i in qargs:
            qubit_time[i] = start_time + duration
        layer_insts.append((start_time, instruction))
    
    print("Layer 46 U3 Parameters:")
    for t, inst in layer_insts:
        if t == 46 and inst.name == 'u3':
            qs = [qc.find_bit(q).index for q in inst.qubits]
            params = inst.params
            print(f"Q{qs[0]}: {np.round(params, 4)}")
            
            # Check for rationality
            is_rat = True
            for p in params:
                 ratio = p / (np.pi/2) 
                 if abs(ratio - round(ratio)) > 1e-4:
                     is_rat = False
            if not is_rat:
                print(f"  -> IRRATIONAL")
            else:
                print(f"  -> Rational")

if __name__ == "__main__":
    analyze_layer_46()
