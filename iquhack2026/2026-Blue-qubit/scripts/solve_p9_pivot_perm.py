from qiskit import QuantumCircuit
from collections import defaultdict
import numpy as np

def solve_permutation():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    qubit_time = [0] * qc.num_qubits
    
    layer_instructions = defaultdict(lambda: defaultdict(list))
    
    for instruction in qc.data:
        qargs = [qc.find_bit(q).index for q in instruction.qubits]
        start_time = max(qubit_time[i] for i in qargs)
        duration = 1
        for i in qargs:
            qubit_time[i] = start_time + duration
        
        for q in qargs:
            layer_instructions[start_time][q].append(instruction)
            
    pivot = 43
    print(f"Solving for permutation around pivot Layer {pivot}...")
    
    # We want a map S such that Gate(L_pre, q) matches Gate(L_post, S[q])
    # Let's use Layer 41 and 45 as they have identical edges.
    # Actually, they have identical edges *without* a permutation! 
    # (0, 35) was in both.
    
    # Let's check Layer 39 vs 47.
    def get_edges(layer):
        edges = set()
        for q in range(qc.num_qubits):
            for inst in layer_instructions[layer][q]:
                if len(inst.qubits) == 2:
                    u, v = sorted([qc.find_bit(inst.qubits[0]).index, 
                                   qc.find_bit(inst.qubits[1]).index])
                    edges.add((u, v))
        return sorted(list(edges))

    e_39 = get_edges(39)
    e_47 = get_edges(47)
    
    print(f"Layer 39 Edges: {len(e_39)}")
    print(f"Layer 47 Edges: {len(e_47)}")
    
    # Try to find a mapping S such that S(e_39) = e_47
    # This is a graph isomorphism problem, but with specific pairs.
    
    import networkx as nx
    G1 = nx.Graph()
    G1.add_edges_from(e_39)
    G2 = nx.Graph()
    G2.add_edges_from(e_47)
    
    from networkx.algorithms import isomorphism
    GM = isomorphism.GraphMatcher(G1, G2)
    if GM.is_isomorphic():
        print("SUCCESS: Layer 39 and 47 are ISOMORPHIC!")
        S = GM.mapping
        print(f"Permutation S: {S}")
        
        # Verify if this S works for other layers
        e_37 = get_edges(37)
        e_49 = get_edges(49)
        
        mapped_37 = sorted([sorted([S.get(u, u), S.get(v, v)]) for u, v in e_37])
        if mapped_37 == e_49:
            print("DOUBLE SUCCESS: Permutation holds for Layer 37/49!")
        else:
            print("FAIL: Permutation does not hold for Layer 37/49.")
            # Maybe the permutation changes over time? "Sweeping"
    else:
        print("FAIL: Layer 39 and 47 are NOT isomorphic.")

if __name__ == "__main__":
    solve_permutation()
