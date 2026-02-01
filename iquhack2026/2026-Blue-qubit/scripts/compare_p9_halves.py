from qiskit import QuantumCircuit
from collections import Counter
import numpy as np

def compare_halves():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc.num_qubits
    
    # Track layers
    qubit_time = [0] * n
    half1_gates = [[] for _ in range(n)]
    half2_gates = [[] for _ in range(n)]
    
    pivot = 43
    
    for instruction in qc.data:
        qargs = [qc.find_bit(q).index for q in instruction.qubits]
        start_time = max(qubit_time[i] for i in qargs)
        duration = 1
        for i in qargs:
            qubit_time[i] = start_time + duration
        
        if start_time < pivot:
            for q in qargs:
                half1_gates[q].append(instruction.name)
        else:
            for q in qargs:
                half2_gates[q].append(instruction.name)
                
    # Compare "Fingerprints"
    def get_fingerprint(gate_list):
        c = Counter(gate_list)
        return (c['u3'], c['cz'])
    
    f1 = [get_fingerprint(h) for h in half1_gates]
    f2 = [get_fingerprint(h) for h in half2_gates]
    
    print("Top 10 Fingerprints (U3, CZ) per qubit in Half 1:")
    print(sorted(f1, reverse=True)[:10])
    
    print("\nTop 10 Fingerprints (U3, CZ) per qubit in Half 2:")
    print(sorted(f2, reverse=True)[:10])
    
    # Check if multisets are equal
    if Counter(f1) == Counter(f2):
        print("\n[!!!] Fingerprint multisets MATCH EXACTLY! Permutation confirmed.")
    else:
        print("\nFingerprint multisets do NOT match exactly.")
        print(f"Unique fingerprints in H1: {len(set(f1))}")
        print(f"Unique fingerprints in H2: {len(set(f2))}")

if __name__ == "__main__":
    compare_halves()
