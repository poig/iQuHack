from qiskit import QuantumCircuit

def find_cz_midpoint():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    q_t = [0] * qc.num_qubits
    cz_layers = []
    
    for instruction in qc.data:
        qargs = [qc.find_bit(q).index for q in instruction.qubits]
        start_time = max(q_t[i] for i in qargs)
        for i in qargs:
            q_t[i] = start_time + 1
        
        if len(qargs) == 2:
            cz_layers.append(start_time)
            
    cz_layers.sort()
    mid_idx = len(cz_layers) // 2
    mid_layer = cz_layers[mid_idx]
    
    print(f"Total CZ: {len(cz_layers)}")
    print(f"Geometric Midpoint (index {mid_idx}): Layer {mid_layer}")

if __name__ == "__main__":
    find_cz_midpoint()
