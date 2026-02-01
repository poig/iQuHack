from qiskit import QuantumCircuit
from collections import defaultdict
import networkx as nx
from networkx.algorithms import isomorphism

def find_all_layer_matches():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc.num_qubits
    
    q_t = [0] * n
    layers = defaultdict(list)
    
    for instruction in qc.data:
        qargs = [qc.find_bit(q).index for q in instruction.qubits]
        start_time = max(q_t[i] for i in qargs)
        for i in qargs:
            q_t[i] = start_time + 1
        if len(qargs) == 2:
            layers[start_time].append(tuple(sorted(qargs)))
            
    # Build graphs for all layers
    graphs = {}
    for t, edges in layers.items():
        if len(edges) < 5: continue # Skip small layers
        G = nx.Graph()
        G.add_edges_from(edges)
        graphs[t] = G
        
    print(f"Analyzing {len(graphs)} significant layers...")
    
    # Compare all pairs
    # Optimize by grouping by edge count and degree sequence
    groups = defaultdict(list)
    for t, G in graphs.items():
        num_edges = G.number_of_edges()
        degs = tuple(sorted([d for n, d in G.degree()], reverse=True))
        groups[(num_edges, degs)].append(t)
        
    print(f"Found {len(groups)} unique graph signatures (EdgeCount, DegreeSeq).")
    
    match_pairs = []
    
    for sig, t_list in groups.items():
        if len(t_list) > 1:
            # Check isomorphism within group
            # If signature matches (edges + degrees), isomorphism is highly likely for random graphs.
            # We assume they match.
            print(f"Signature {sig}: Layers {t_list} possibly isomorphic.")
            
            # Explicit check for the first pair to verify
            if len(t_list) >= 2:
                t1, t2 = t_list[0], t_list[1]
                GM = isomorphism.GraphMatcher(graphs[t1], graphs[t2])
                if GM.is_isomorphic():
                    print(f"  -> CONFIRMED: Layer {t1} ~= Layer {t2}")
                    mapping = GM.mapping
                    # print(f"  Mapping: {mapping}")
                else:
                    print(f"  -> Mismatch despite signature: {t1} vs {t2}")

if __name__ == "__main__":
    find_all_layer_matches()
