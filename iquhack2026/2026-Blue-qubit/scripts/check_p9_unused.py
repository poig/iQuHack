from qiskit import QuantumCircuit

def find_unused():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc.num_qubits
    used = [False] * n
    for inst in qc.data:
        for q in inst.qubits:
            used[qc.find_bit(q).index] = True
            
    for i in range(n):
        if not used[i]:
            print(f"Qubit {i} is NOT used.")

if __name__ == "__main__":
    find_unused()
