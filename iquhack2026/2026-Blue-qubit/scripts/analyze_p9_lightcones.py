from qiskit import QuantumCircuit
import networkx as nx

def analyze_lightcones():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    n = qc.num_qubits
    
    # We want to know for each qubit i, which qubits it depends on.
    # We can builds a dependency graph.
    # Node: (qubit, time_step) or just keep track of qubit sets.
    
    dependencies = [set([i]) for i in range(n)]
    
    # Iterate gates in order
    for instr in qc.data:
        qargs = instr.qubits
        if len(qargs) == 1:
            continue # U3 doesn't add new qubit dependencies
        elif len(qargs) == 2:
            u = qc.find_bit(qargs[0]).index
            v = qc.find_bit(qargs[1]).index
            
            # Combine their dependent sets
            union = dependencies[u] | dependencies[v]
            dependencies[u] = union
            dependencies[v] = union
            
    print(f"Total Qubits: {n}")
    for i in range(n):
        print(f"Qubit {i} Lightcone Size: {len(dependencies[i])}")
        
    # Stats
    sizes = [len(d) for d in dependencies]
    print(f"Min Size: {min(sizes)}")
    print(f"Max Size: {max(sizes)}")
    print(f"Avg Size: {sum(sizes)/n:.2f}")

if __name__ == "__main__":
    analyze_lightcones()
