from qiskit import QuantumCircuit
import networkx as nx
from networkx.algorithms import isomorphism
from collections import defaultdict

def solve_permutation_39_53():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    q_t = [0] * qc.num_qubits
    layers = defaultdict(list)
    
    for instruction in qc.data:
        qargs = [qc.find_bit(q).index for q in instruction.qubits]
        start_time = max(q_t[i] for i in qargs)
        for i in qargs:
            q_t[i] = start_time + 1
        if len(qargs) == 2:
            layers[start_time].append(tuple(sorted(qargs)))
            
    # Solve for 39 -> 53
    edges39 = layers[39]
    edges53 = layers[53]
    
    G39 = nx.Graph()
    G39.add_edges_from(edges39)
    # Ensure all nodes present for correct mapping size
    G39.add_nodes_from(range(qc.num_qubits))
    
    G53 = nx.Graph()
    G53.add_edges_from(edges53)
    G53.add_nodes_from(range(qc.num_qubits))
    
    GM = isomorphism.GraphMatcher(G39, G53)
    if GM.is_isomorphic():
        print("SUCCESS: Layer 39 and 53 are ISOMORPHIC!")
        S = GM.mapping
        # Print mapping in a copy-pasteable format
        print("Scrambling Map S = {")
        for k, v in sorted(S.items()):
            print(f"    {k}: {v},")
        print("}")
        
        # Verify if this S works for Layer 37 -> 55 (Distance 2 out)
        # S maps 39 to 53. Does it map 37 to 55?
        edges37 = layers[37]
        edges55 = layers[55]
        
        mapped_37 = []
        for u, v in edges37:
            mapped_37.append(tuple(sorted([S[u], S[v]])))
        mapped_37 = sorted(mapped_37)
        
        if mapped_37 == sorted(edges55):
             print("DOUBLE SUCCESS: Permutation S holds for Layer 37 -> 55!")
        else:
             print("FAIL: Permutation S does NOT hold for Layer 37 -> 55.")
    else:
        print("FAIL: Layer 39 and 53 are NOT isomorphic.")

if __name__ == "__main__":
    solve_permutation_39_53()
