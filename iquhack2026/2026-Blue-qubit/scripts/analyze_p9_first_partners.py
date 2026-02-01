from qiskit import QuantumCircuit

def first_partners():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc.num_qubits
    first_partner = [None] * n
    
    for i, inst in enumerate(qc.data):
        if len(inst.qubits) == 2:
            u = qc.find_bit(inst.qubits[0]).index
            v = qc.find_bit(inst.qubits[1]).index
            if first_partner[u] is None: first_partner[u] = v
            if first_partner[v] is None: first_partner[v] = u
            
    for i in range(n):
        print(f"Q{i:02d} first partner: Q{first_partner[i]:02d}")

if __name__ == "__main__":
    first_partners()
