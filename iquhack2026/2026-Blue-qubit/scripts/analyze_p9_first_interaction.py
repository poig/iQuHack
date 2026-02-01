from qiskit import QuantumCircuit

def find_first_2q():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc.num_qubits
    first_2q_idx = [999999] * n
    
    data = list(qc.data)
    for i, instr in enumerate(data):
        if len(instr.qubits) == 2:
            u = qc.find_bit(instr.qubits[0]).index
            v = qc.find_bit(instr.qubits[1]).index
            if first_2q_idx[u] == 999999: first_2q_idx[u] = i
            if first_2q_idx[v] == 999999: first_2q_idx[v] = i
            
    print("\nFirst 2-Qubit Gate Index per Qubit:")
    results = []
    for i in range(n):
        results.append((i, first_2q_idx[i]))
        
    results.sort(key=lambda x: x[1], reverse=True)
    for i, idx in results:
        if idx > 100:
             print(f"Q{i:2d}: First 2Q Gate at index {idx:4d}")

if __name__ == "__main__":
    find_first_2q()
