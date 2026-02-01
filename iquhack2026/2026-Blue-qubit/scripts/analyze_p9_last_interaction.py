from qiskit import QuantumCircuit, transpile, qasm2
import pyzx as zx

def find_last_2q():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    
    # 1. PyZX Reduction
    print("Simplifying with PyZX...")
    qasm_str = qasm2.dumps(qc)
    g = zx.Circuit.from_qasm(qasm_str).to_graph()
    zx.full_reduce(g)
    circ_reduced = zx.extract_circuit(g)
    qc_red = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())
    
    n = qc_red.num_qubits
    last_2q_idx = [-1] * n
    
    data = list(qc_red.data)
    for i, instr in enumerate(data):
        if len(instr.qubits) == 2:
            u = qc_red.find_bit(instr.qubits[0]).index
            v = qc_red.find_bit(instr.qubits[1]).index
            last_2q_idx[u] = i
            last_2q_idx[v] = i
            
    print("\nLast 2-Qubit Gate Index per Qubit (Circuit Length: %d):" % len(data))
    results = []
    for i in range(n):
        results.append((i, last_2q_idx[i]))
        
    # Sort by index
    results.sort(key=lambda x: x[1])
    for i, idx in results:
        print(f"Q{i:2d}: Last 2Q Gate at index {idx:4d} ({len(data)-idx:3d} gates from end)")

if __name__ == "__main__":
    find_last_2q()
