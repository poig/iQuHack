from qiskit import QuantumCircuit
from collections import Counter
import numpy as np

def find_best_permutation():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc.num_qubits
    
    # Track layers
    qubit_time = [0] * n
    pairs1 = []
    pairs2 = []
    
    pivot = 43
    
    for instruction in qc.data:
        qargs = [qc.find_bit(q).index for q in instruction.qubits]
        start_time = max(qubit_time[i] for i in qargs)
        duration = 1
        for i in qargs:
            qubit_time[i] = start_time + duration
        
        if len(qargs) == 2:
            u, v = sorted(qargs)
            if start_time < pivot:
                pairs1.append((u, v))
            else:
                pairs2.append((u, v))
                
    # Adjacency matrices
    adj1 = np.zeros((n, n))
    for u, v in pairs1:
        adj1[u, v] += 1
        adj1[v, u] += 1
        
    adj2 = np.zeros((n, n))
    for u, v in pairs2:
        adj2[u, v] += 1
        adj2[v, u] += 1
        
    # We want to find P such that adj1 is similar to P * adj2 * P^T
    # This is the Graph Isomorphism / Quadratic Assignment Problem.
    # Since n=56 is small, we can check degree sequences and eigendecomposition.
    
    # Degree sequences
    d1 = np.sum(adj1, axis=1)
    d2 = np.sum(adj2, axis=1)
    
    # Map by degree rank
    idx1 = np.argsort(d1)
    idx2 = np.argsort(d2)
    
    P_deg = {idx2[i]: idx1[i] for i in range(n)}
    
    # Check overlap with this P_deg
    overlap = 0
    for u, v in pairs1:
        pu, pv = sorted([P_deg[u], P_deg[v]]) # (Wait, mapping is idx2 -> idx1? No, from 2 to 1)
        # Actually mapping is from qubit in Half 2 to qubit in Half 1
        pass
    
    # Simpler: check if degree distributions match
    if np.all(np.sort(d1) == np.sort(d2)):
        print("Degree distributions MATCH PERFECTLY. The halves are likely isomorphic.")
    else:
        print("Degree distributions mismatch.")
        print(f"H1 Degrees: {np.sort(d1)}")
        print(f"H2 Degrees: {np.sort(d2)}")

if __name__ == "__main__":
    find_best_permutation()
