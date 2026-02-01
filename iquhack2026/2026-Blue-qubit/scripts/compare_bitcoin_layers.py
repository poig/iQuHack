
from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag
import numpy as np

def compare_layer_params():
    qc = QuantumCircuit.from_qasm_file("bitcoin_problem/P1_little_dimple.qasm")
    dag = circuit_to_dag(qc)
    layers = list(dag.layers())
    
    print(f"Total Layers: {len(layers)}")
    
    layer_fingerprints = []
    for i, layer in enumerate(layers):
        ops = []
        for node in layer['graph'].op_nodes():
            q_indices = sorted([qc.find_bit(q).index for q in node.qargs])
            params = [round(float(p), 6) for p in node.op.params]
            ops.append((node.op.name, tuple(q_indices), tuple(params)))
        ops.sort()
        layer_fingerprints.append(tuple(ops))
        
    # Check for duplicates
    from collections import defaultdict
    duplicates = defaultdict(list)
    for i, fp in enumerate(layer_fingerprints):
        duplicates[fp].append(i)
        
    found_dup = False
    for fp, indices in duplicates.items():
        if len(indices) > 1:
            print(f"Layers {indices} are IDENTICAL.")
            found_dup = True
            
    if not found_dup:
        print("No identical layers found.")
        
    # Check for Adjoint layers: same connectivity, minus params?
    # Actually, U(theta, phi, lambd).adjoint() is U(-theta, -lambd, -phi)
    def is_adjoint(fp1, fp2):
        if len(fp1) != len(fp2): return False
        for op1, op2 in zip(fp1, fp2):
            if op1[0] != op2[0] or op1[1] != op2[1]: return False
            if op1[0] == 'u':
                p1, p2 = op1[2], op2[2]
                # Check theta2 == -theta1, phi2 == -lambd1, lambd2 == -phi1
                if not (np.isclose(p2[0], -p1[0], atol=1e-5) and 
                        np.isclose(p2[1], -p1[2], atol=1e-5) and 
                        np.isclose(p2[2], -p1[1], atol=1e-5)):
                    return False
            # For CZ, no params
        return True

    adjoints = []
    for i in range(len(layer_fingerprints)):
        for j in range(i + 1, len(layer_fingerprints)):
            if is_adjoint(layer_fingerprints[i], layer_fingerprints[j]):
                adjoints.append((i, j))
                
    if adjoints:
        print("\nAdjoint Layer Pairs found:")
        for i, j in adjoints:
            print(f"  Layer {i} and Layer {j}")
    else:
        print("\nNo adjoint layer pairs found.")

if __name__ == "__main__":
    compare_layer_params()
