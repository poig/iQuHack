import pyzx as zx
from qiskit import QuantumCircuit, transpile, qasm2
from qiskit.quantum_info import Operator
import numpy as np

def decompose_skeleton():
    path = "challenge/P9_grand_summit.qasm"
    
    # 1. PyZX Reduction
    qc_orig = QuantumCircuit.from_qasm_file(path)
    g = zx.Circuit.from_qasm(qasm2.dumps(qc_orig)).to_graph()
    zx.full_reduce(g)
    circ_reduced = zx.extract_circuit(g)
    qc_zx = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())
    qc_trans = transpile(qc_zx, basis_gates=['u3', 'cx'], optimization_level=3)
    
    # 2. Extract Skeleton (Layers 30-60)
    # The outer layers were dense, but middle was sparse.
    # Let's verify if the OUTERS can be approximated as Identity 
    # or if we need to account for them.
    # If Outer1 * Outer2^-1 = I, then we just need the Core.
    # So let's isolate the Core gates.
    
    n = qc_trans.num_qubits
    qubit_depth = [0] * n
    
    qc_skeleton = QuantumCircuit(n)
    
    # We filter gates that are in the "sparse region"
    # From previous analysis: approx layers 35 to 50 are sparse.
    # Let's grab layers 30 to 60 to be safe.
    
    gates_kept = 0
    
    for inst in qc_trans.data:
        qargs = [qc_trans.find_bit(q).index for q in inst.qubits]
        start_time = max(qubit_depth[i] for i in qargs)
        
        if 30 <= start_time <= 60:
            qc_skeleton.append(inst.operation, inst.qubits)
            gates_kept += 1
            
        for i in qargs:
            qubit_depth[i] = start_time + 1
            
    print(f"Extracted Skeleton: {gates_kept} gates.")
    print(f"Skeleton Depth: {qc_skeleton.depth()}")
    
    # Analyze the skeleton unitary
    # It might be disconnected.
    # Check connectivity of skeleton.
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for inst in qc_skeleton.data:
        if len(inst.qubits) == 2:
            u, v = [qc_skeleton.find_bit(q).index for q in inst.qubits]
            G.add_edge(u, v)
            
    comps = list(nx.connected_components(G))
    print(f"Skeleton Connectivity: {len(comps)} components.")
    for i, c in enumerate(comps):
        if len(c) > 1:
            print(f"  Comp {i}: {len(c)} qubits -> {list(c)}")
            
    # If components are small, we can solve exactly!
    # If large, maybe linear?

if __name__ == "__main__":
    decompose_skeleton()
