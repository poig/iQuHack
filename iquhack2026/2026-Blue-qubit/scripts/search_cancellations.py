from qiskit import QuantumCircuit

def search_cancellation():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    data = list(qc.data)
    n = len(data)
    
    # Simple check for immediate CZ cancellation
    cz_pairs = 0
    for i in range(n-1):
        i1 = data[i]
        i2 = data[i+1]
        
        if i1.operation.name == 'cz' and i2.operation.name == 'cz':
            q1 = set(qc.find_bit(q).index for q in i1.qubits)
            q2 = set(qc.find_bit(q).index for q in i2.qubits)
            if q1 == q2:
                cz_pairs += 1
                
    print(f"Immediate CZ Cancellations: {cz_pairs}")
    
    # Check for CZ pairs separated only by commuting gates (RZ)
    # u3(0, phi, lam) is effectively RZ
    deferred_cancellations = 0
    # ... more complex logic if needed ...

if __name__ == "__main__":
    search_cancellation()
