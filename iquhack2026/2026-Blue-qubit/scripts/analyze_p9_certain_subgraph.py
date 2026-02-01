import networkx as nx
import re

def analyze_certain_subgraph():
    certain_qubits = [2, 4, 5, 41, 42, 48, 53]
    
    with open("challenge/P9_grand_summit.qasm", "r") as f:
        lines = f.readlines()
        
    G = nx.Graph()
    for line in lines:
        if line.startswith("cz"):
            match = re.search(r"q\[(\d+)\],q\[(\d+)\]", line)
            if match:
                u, v = int(match.group(1)), int(match.group(2))
                G.add_edge(u, v)
                
    sub = G.subgraph(certain_qubits)
    print(f"Certain Qubits: {certain_qubits}")
    print(f"Edges between them: {list(sub.edges())}")
    
    # Check external neighbors
    for q in certain_qubits:
        neighbors = list(G.neighbors(q))
        certain_neighbors = [n for n in neighbors if n in certain_qubits]
        print(f"Q{q:02d}: {len(neighbors)} neighbors total, {len(certain_neighbors)} are 'certain'")

if __name__ == "__main__":
    analyze_certain_subgraph()
