from qiskit import QuantumCircuit
import networkx as nx

def analyze():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc.num_qubits
    
    G = nx.Graph()
    G.add_nodes_from(range(n))
    
    for instruction in qc.data:
        qargs = instruction.qubits
        if len(qargs) == 2:
            u = qc.find_bit(qargs[0]).index
            v = qc.find_bit(qargs[1]).index
            G.add_edge(u, v)
            
    print(f"Total Qubits: {n}")
    print(f"Total Edges: {G.number_of_edges()}")
    
    components = list(nx.connected_components(G))
    print(f"Number of Connected Components: {len(components)}")
    for i, c in enumerate(components):
        print(f" Component {i}: {len(c)} qubits: {sorted(list(c))}")
        
    # Degrees
    degrees = dict(G.degree())
    avg_deg = sum(degrees.values()) / n
    print(f"Average Degree: {avg_deg:.2f}")
    print(f"Max Degree: {max(degrees.values())}")
    
    # Are there any "end" qubits?
    leaf_nodes = [n for n, d in degrees.items() if d <= 1]
    print(f"Leaf/Isolated Nodes: {leaf_nodes}")

if __name__ == "__main__":
    analyze()
