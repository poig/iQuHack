import pyzx as zx
from qiskit import QuantumCircuit, transpile, qasm2

def analyze_transpiled():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    print(f"Original Qubits: {qc.num_qubits}")
    
    # 1. PyZX Reduction
    print("Simplifying with PyZX...")
    qasm_str = qasm2.dumps(qc)
    g = zx.Circuit.from_qasm(qasm_str).to_graph()
    zx.full_reduce(g)
    circ_reduced = zx.extract_circuit(g)
    qc_zx = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())
    
    # 2. Aggressive Approximation
    deg = 0.99 
    print(f"Applying Refined Approximation (degree={deg})...")
    qc_trans = transpile(qc_zx, 
                          basis_gates=['u3', 'cx'],
                          optimization_level=3, 
                          approximation_degree=deg)
    
    qubit_data = {}
    for i in range(qc_trans.num_qubits):
        qubit_data[i] = {"depth": 0, "two_qubit_count": 0}

    for instruction in qc_trans.data:
        qargs = instruction.qubits
        for q in qargs:
            idx = qc_trans.find_bit(q).index
            qubit_data[idx]["depth"] += 1 
            if len(qargs) == 2:
                qubit_data[idx]["two_qubit_count"] += 1
                
    print("\nQubit Statistics (0.99, Sorted by Ops):")
    sorted_stats = sorted(qubit_data.items(), key=lambda x: x[1]['depth'])
    for i, data in sorted_stats:
        print(f"Q{i:2d}: Ops={data['depth']:4d}, 2Q-Gates={data['two_qubit_count']:3d}")





    
    # Specifically check q6 if possible, as user hinted at "few depth"
    # Actually, let's just output the sorted list
    
if __name__ == "__main__":
    analyze_transpiled()
