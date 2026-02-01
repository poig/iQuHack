import pyzx as zx
from qiskit import QuantumCircuit, transpile, qasm2
from qiskit_aer import AerSimulator
import json

def solve_skeleton():
    path = "challenge/P9_grand_summit.qasm"
    
    # Reconstruct Skeleton
    qc_orig = QuantumCircuit.from_qasm_file(path)
    g = zx.Circuit.from_qasm(qasm2.dumps(qc_orig)).to_graph()
    zx.full_reduce(g)
    circ_reduced = zx.extract_circuit(g)
    qc_zx = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())
    qc_trans = transpile(qc_zx, basis_gates=['u3', 'cx'], optimization_level=3)
    
    n = qc_trans.num_qubits
    qubit_depth = [0] * n
    qc_skeleton = QuantumCircuit(n)
    
    for inst in qc_trans.data:
        qargs = [qc_trans.find_bit(q).index for q in inst.qubits]
        start_time = max(qubit_depth[i] for i in qargs)
        if 30 <= start_time <= 60:
            qc_skeleton.append(inst.operation, inst.qubits)
        for i in qargs:
            qubit_depth[i] = start_time + 1
            
    qc_skeleton.measure_all()
    
    sim = AerSimulator(method='matrix_product_state', matrix_product_state_max_bond_dimension=128)
    print("Simulating Skeleton (506 gates, BD=128)...")
    job = sim.run(transpile(qc_skeleton, sim), shots=2000)
    counts = job.result().get_counts()
    
    top = max(counts, key=counts.get)
    print(f"Top Skeleton Result: {top} (Cnt: {counts[top]})")
    
    with open("results/p9_skeleton_res.json", "w") as f:
        json.dump(counts, f)

if __name__ == "__main__":
    solve_skeleton()
