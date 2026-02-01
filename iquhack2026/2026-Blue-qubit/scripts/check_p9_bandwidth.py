from qiskit import QuantumCircuit
import networkx as nx
from networkx.utils import reverse_cuthill_mckee_ordering

def compute_bandwidth():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc.num_qubits
    
    # Build interaction graph (weighted by count?)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    
    gate_counts = 0
    for instruction in qc.data:
        if len(instruction.qubits) == 2:
            u, v = [qc.find_bit(q).index for q in instruction.qubits]
            if G.has_edge(u, v):
                G[u][v]['weight'] += 1
            else:
                G.add_edge(u, v, weight=1)
            gate_counts += 1
            
    print(f"Graph Construction: {n} nodes, {G.number_of_edges()} edges from {gate_counts} gates.")
    
    # Calculate original bandwidth
    def bandwidth(G, order):
        pos = {node: i for i, node in enumerate(order)}
        bw = 0
        for u, v in G.edges():
            bw = max(bw, abs(pos[u] - pos[v]))
        return bw
        
    orig_bw = bandwidth(G, range(n))
    print(f"Original Bandwidth: {orig_bw}")
    
    # RCM Ordering
    try:
        rcm_gen = reverse_cuthill_mckee_ordering(G)
        rcm_order = list(rcm_gen)
        rcm_bw = bandwidth(G, rcm_order)
        print(f"RCM Bandwidth: {rcm_bw}")
        
        # Check if RCM ordering gives a clue about structure
        print(f"RCM Order: {rcm_order}")
        
        # Also check Spectral Ordering (Fiedler vector)
        laplacian = nx.laplacian_matrix(G).todense()
        from scipy.linalg import eigh
        w, v = eigh(laplacian)
        # 2nd smallest eigenvalue's eigenvector
        fiedler = v[:, 1]
        spectral_order = list(np.argsort(fiedler))
        spec_bw = bandwidth(G, spectral_order)
        print(f"Spectral Bandwidth: {spec_bw}")
        
    except Exception as e:
        print(f"Error computing ordering: {e}")

if __name__ == "__main__":
    import numpy as np
    compute_bandwidth()
