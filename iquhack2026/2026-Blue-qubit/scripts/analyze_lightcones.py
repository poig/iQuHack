import argparse
from qiskit import QuantumCircuit, transpile
from qiskit.converters import circuit_to_dag
import matplotlib.pyplot as plt
import numpy as np

def get_lightcone_size(qc, qubit_index):
    """
    Computes the size (number of qubits, number of gates) of the causal cone 
    for a specific qubit at the end of the circuit.
    This is a backward traversal.
    """
    # dag = circuit_to_dag(qc) # Not needed for simple list traversal
    
    # We want the lightcone for the output of 'qubit_index'
    # Start with the specific qubit as the dependency target
    target_bit = qc.qubits[qubit_index]
    depend_on = {target_bit}
    
    # Get ops in reverse
    ops = list(qc.data)
    ops.reverse()
    
    op_count = 0
    
    for instruction in ops:
        if instruction.operation.name == 'barrier':
            continue
            
        # Check if gate involves any qubit we care about
        gate_qubits = set(instruction.qubits)
        if not gate_qubits.isdisjoint(depend_on):
            # This gate affects our lightcone
            depend_on.update(gate_qubits)
            op_count += 1
            
    return len(depend_on), op_count

def analyze_lightcones(qasm_path):
    print(f"--- Analyzing Lightcones for {qasm_path} ---")
    try:
        qc = QuantumCircuit.from_qasm_file(qasm_path)
    except FileNotFoundError:
        print("File not found.")
        return

    # Assuming standard transpilation first to match what we would run
    # (Or analyzing raw structure, which is arguably better for 'potential')
    # Let's analyze raw first to be fast.
    
    num_qubits = qc.num_qubits
    print(f"Total Qubits: {num_qubits}")
    
    cone_sizes = [] # (n_qubits, n_gates)
    
    print("\nQubit | Cone Qubits | Cone Gates")
    print("--------------------------------")
    
    for i in range(num_qubits):
        nq, ng = get_lightcone_size(qc, i)
        cone_sizes.append(nq)
        print(f"  {i:2d}  |     {nq:2d}      |    {ng:4d}")
        
    avg_cone = np.mean(cone_sizes)
    min_cone = np.min(cone_sizes)
    max_cone = np.max(cone_sizes)
    
    print("\nStats (Qubit Count in Cone):")
    print(f"  Average: {avg_cone:.2f}")
    print(f"  Min:     {min_cone}")
    print(f"  Max:     {max_cone}")
    
    if max_cone < num_qubits:
        print("\n[CONCLUSION] Lightcones are smaller than full circuit! Structure exploitation possible.")
    else:
        print("\n[CONCLUSION] Lightcones span the full circuit. No trivial separation.")

if __name__ == "__main__":
    analyze_lightcones("../challenge/P9_grand_summit.qasm")
