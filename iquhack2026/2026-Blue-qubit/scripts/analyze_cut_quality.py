import pyzx as zx
from qiskit import QuantumCircuit, qasm2
import networkx as nx
import numpy as np
import argparse

# P9: Grand Summit
TARGET_QASM = "challenge/P9_grand_summit.qasm"

def analyze_cut():
    print(f"\n=== Analyzing Cut Quality for P9 ===")
    
    # 1. Load and Graph
    try:
        qc = QuantumCircuit.from_qasm_file(TARGET_QASM)
        # Simplify first to get true connectivity
        qasm_str = qasm2.dumps(qc)
        g = zx.Circuit.from_qasm(qasm_str).to_graph()
        zx.full_reduce(g) # Remove trivial connections
        circ_reduced = zx.extract_circuit(g)
        qc_zx = QuantumCircuit.from_qasm_str(circ_reduced.to_qasm())
        n = qc_zx.num_qubits
        
        # Build Interaction Graph
        G = nx.Graph()
        G.add_nodes_from(range(n))
        for instr in qc_zx.data:
            if len(instr.qubits) == 2:
                u = instr.qubits[0]._index
                v = instr.qubits[1]._index
                if u != v:
                    if G.has_edge(u, v): G[u][v]['weight'] += 1
                    else: G.add_edge(u, v, weight=1)
        
        print(f"  Graph: {n} Nodes, {G.number_of_edges()} Edges")
        
        # 2. Spectral Bisection
        L = nx.laplacian_matrix(G, weight='weight').todense()
        evals, evecs = np.linalg.eigh(L)
        fiedler_val = evals[1]
        fiedler_vec = evecs[:, 1]
        
        print(f"  Fiedler Value: {fiedler_val:.4f} (Hairball Metric)")
        
        # 3. Partition
        # Split nodes based on sign of Fiedler Vector
        set_A = [i for i in range(n) if fiedler_vec[i] >= 0]
        set_B = [i for i in range(n) if fiedler_vec[i] < 0]
        
        print(f"  Partition A: {len(set_A)} qubits")
        print(f"  Partition B: {len(set_B)} qubits")
        
        # 4. Count Cuts and Identify Bridge
        cut_edges = 0
        cut_weight = 0
        bridge_nodes_A = set()
        bridge_nodes_B = set()
        
        for u, v, data in G.edges(data=True):
            u_in_A = (u in set_A)
            v_in_A = (v in set_A)
            
            if u_in_A != v_in_A: # Edge crosses the cut
                cut_edges += 1
                cut_weight += data['weight']
                if u_in_A: 
                    bridge_nodes_A.add(u)
                    bridge_nodes_B.add(v)
                else: 
                    bridge_nodes_A.add(v)
                    bridge_nodes_B.add(u)
                
        print(f"  [RESULT] Cut Size: {cut_edges} Edges")
        print(f"  [RESULT] Total Cut Weight: {cut_weight}")
        
        print(f"  Bridge Nodes in A ({len(bridge_nodes_A)}): {sorted(list(bridge_nodes_A))}")
        print(f"  Bridge Nodes in B ({len(bridge_nodes_B)}): {sorted(list(bridge_nodes_B))}")
        
        # Calculate Density of the Bridge
        bridge_density = cut_edges / (len(bridge_nodes_A) * len(bridge_nodes_B))
        print(f"  Bridge Density: {bridge_density:.2f}")

        overhead = 4 ** cut_edges # Rough approx for naive cutting
        print(f"  Est. Classical Overhead: 4^{cut_edges} ~ {overhead:.2e}")
        
        if cut_edges < 12:
            print("  [CONCLUSION] Cutting IS Viable! We should factor this.")
        else:
            print("  [CONCLUSION] Cutting is EXPENSIVE. Too many wires cross the middle.")

    except Exception as e:
        print(f"      [Error] Analysis failed: {e}")

if __name__ == "__main__":
    analyze_cut()
