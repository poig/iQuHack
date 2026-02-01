
from qiskit import QuantumCircuit
import networkx as nx
import matplotlib.pyplot as plt

def analyze_connectivity():
    path = "bitcoin_problem/P1_little_dimple.qasm"
    qc = QuantumCircuit.from_qasm_file(path)
    
    G = nx.Graph()
    G.add_nodes_from(range(qc.num_qubits))
    
    for inst in qc.data:
        if len(inst.qubits) == 2:
            q1 = qc.find_bit(inst.qubits[0]).index
            q2 = qc.find_bit(inst.qubits[1]).index
            G.add_edge(q1, q2)
            
    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")
    print(f"Avg Degree: {2 * G.number_of_edges() / G.number_of_nodes():.2f}")
    print(f"Max Degree: {max(dict(G.degree()).values())}")
    
    # Check if 1D or something else
    is_1d = all(d <= 2 for d in dict(G.degree()).values())
    print(f"Is 1D Chain Structure: {is_1d}")
    
    # Try to find a low-bandwidth reordering
    import numpy as np
    adj = nx.to_numpy_array(G)
    
    # Current Bandwidth
    bandwidth = 0
    for i in range(qc.num_qubits):
        for j in range(qc.num_qubits):
            if adj[i, j] > 0:
                bandwidth = max(bandwidth, abs(i - j))
    print(f"Current Bandwidth: {bandwidth}")
    
    # Use RCM (Reverse Cuthill-McKee) for reordering
    from scipy.sparse.csgraph import reverse_cuthill_mckee
    from scipy.sparse import csr_matrix
    
    rcm_perm = reverse_cuthill_mckee(csr_matrix(adj))
    print(f"RCM Permutation: {rcm_perm}")
    
    # New Bandwidth
    new_adj = adj[rcm_perm, :][:, rcm_perm]
    new_bandwidth = 0
    for i in range(qc.num_qubits):
        for j in range(qc.num_qubits):
            if new_adj[i, j] > 0:
                new_bandwidth = max(new_bandwidth, abs(i - j))
    print(f"New Bandwidth (RCM): {new_bandwidth}")

if __name__ == "__main__":
    analyze_connectivity()
