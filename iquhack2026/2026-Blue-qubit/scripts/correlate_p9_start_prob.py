import json
from qiskit import QuantumCircuit

def correlate():
    with open("results/final_P9.json", "r") as f:
        data = json.load(f)
    
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc.num_qubits
    first = [999999] * n
    for i, inst in enumerate(qc.data):
        if len(inst.qubits) == 2:
            u = qc.find_bit(inst.qubits[0]).index
            v = qc.find_bit(inst.qubits[1]).index
            first[u] = min(first[u], i)
            first[v] = min(first[v], i)
            
    results = []
    for i in range(n):
        val = data[str(i)]['val']
        results.append((i, first[i], abs(val)))
        
    results.sort(key=lambda x: x[1])
    
    print(f"{'Qubit':<6} {'Start':<8} {'Certainty':<10}")
    print("-" * 25)
    for q, s, c in results:
        status = "HIGH" if c > 0.4 else ("MED" if c > 0.1 else "LOW")
        print(f"Q{q:02d}    {s:<8} {c:.4f} [{status}]")

if __name__ == "__main__":
    correlate()
