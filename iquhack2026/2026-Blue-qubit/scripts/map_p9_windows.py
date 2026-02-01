from qiskit import QuantumCircuit

def map_windows():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc.num_qubits
    first = [999999] * n
    last = [-1] * n
    
    for i, inst in enumerate(qc.data):
        if len(inst.qubits) == 2:
            u = qc.find_bit(inst.qubits[0]).index
            v = qc.find_bit(inst.qubits[1]).index
            first[u] = min(first[u], i)
            first[v] = min(first[v], i)
            last[u] = max(last[u], i)
            last[v] = max(last[v], i)
            
    print(f"{'Qubit':<6} {'First':<8} {'Last':<8} {'Span':<8} {'CZ Counts':<10}")
    results = []
    counts = [0] * n
    for inst in qc.data:
        if len(inst.qubits) == 2:
            for q in inst.qubits: counts[qc.find_bit(q).index] += 1

    for i in range(n):
        results.append((i, first[i], last[i], last[i] - first[i], counts[i]))
        
    results.sort(key=lambda x: x[1])
    for r in results:
        print(f"Q{r[0]:02d}    {r[1]:<8} {r[2]:<8} {r[3]:<8} {r[4]:<10}")


if __name__ == "__main__":
    map_windows()
