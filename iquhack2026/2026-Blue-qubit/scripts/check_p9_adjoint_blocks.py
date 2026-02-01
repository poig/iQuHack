from qiskit import QuantumCircuit
from collections import defaultdict
import numpy as np

def check_adjoint_layers():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc.num_qubits
    
    qubit_time = [0] * n
    layers = defaultdict(list)
    
    for instruction in qc.data:
        qargs = [qc.find_bit(q).index for q in instruction.qubits]
        start_time = max(qubit_time[i] for i in qargs)
        duration = 1
        for i in qargs:
            qubit_time[i] = start_time + duration
        
        layers[start_time].append(instruction)
        
    num_layers = max(layers.keys()) + 1
    
    # We want to find i, j such that Layer(i) is Adjoint of Layer(j)
    # This is hard due to single-qubit vs two-qubit layers.
    # Let's group them into blocks of 2 (1Q + 2Q).
    
    blocks = []
    for i in range(0, num_layers, 2):
        block_insts = layers[i] + layers[i+1]
        blocks.append(block_insts)
        
    print(f"Total 2-layer blocks: {len(blocks)}")
    
    def get_block_fingerprint(insts):
        # A simple fingerprint: (set of edges, set of (qubit, rounded parameters))
        edges = set()
        params = []
        for inst in insts:
            qs = tuple(sorted([qc.find_bit(q).index for q in inst.qubits]))
            if len(qs) == 2:
                edges.add(qs)
            else:
                params.append((qs[0], tuple(np.round(inst.params, 4))))
        return (frozenset(edges), frozenset(params))

    fingerprints = [get_block_fingerprint(b) for b in blocks]
    
    # Check for direct matches or adjoints
    # In HQAP, U and Udagger are adjoints. 
    # Adjoint of U3(theta, phi, lam) is U3(theta, -lam, -phi) or similar.
    
    def get_adjoint_fingerprint(fp):
        edges, params = fp
        adj_params = []
        for q, (theta, phi, lam) in params:
            # U3(theta, phi, lam)^\dagger = U3(-theta, -lam, -phi) or U3(theta, pi-lam, pi-phi)?
            # Standard is U3(theta, phi, lam)^\dagger = U3(theta, -lam, -phi) if we ignore global phase.
            adj_params.append((q, (theta, -lam, -phi)))
        return (edges, frozenset(adj_params))

    for i in range(len(blocks)):
        f1 = fingerprints[i]
        adj_f1 = get_adjoint_fingerprint(f1)
        for j in range(i + 1, len(blocks)):
            f2 = fingerprints[j]
            if f1 == f2:
                print(f"Block {i} and {j} are IDENTICAL.")
            if adj_f1 == f2:
                print(f"Block {j} is the ADJOINT of Block {i}.")
            
            # Check for permuted matches
            if f1[0] == f2[0]: # Edges match
                 print(f"Block {i} and {j} have SAME CONNECTIVITY.")

if __name__ == "__main__":
    check_adjoint_layers()
