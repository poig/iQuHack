from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np

def solve_backbone():
    path = "challenge/P9_grand_summit.qasm"
    qc = QuantumCircuit.from_qasm_file(path)
    
    # Create Backbone Circuit
    # Replace 'Complex' U3s with Identity?
    # Or replace with simplified Rz?
    # If theta is 'complex', it's likely part of the obfuscation.
    # Let's try replacing ALL U3s where theta is not 0 modulo pi with Identity?
    # No, that's too aggressive.
    # U3(theta, phi, lam). If theta != k*pi/2, set theta=0?
    # If we set theta=0, it becomes Rz. Rz preserves 0/1 basis.
    
    qc_backbone = QuantumCircuit(qc.num_qubits)
    
    replaced_count = 0
    
    for inst in qc.data:
        if inst.operation.name == 'u3':
            theta, phi, lam = inst.operation.params
            
            # Snap to nearest Clifford?
            # Or just check if "complex" (theta not 0, pi, pi/2) and replace with I?
            # User said "Core is Identity".
            # The most robust assumption: The "Complex" part IS the Identity Block wrapper.
            # So if we strip it, we might lose the identity property?
            # OR, if we strip it, we reveal the "underlying" state.
            
            # Strict Clifford Check: Theta, Phi, Lam must all be multiples of pi/2
            is_clifford = True
            for p in [theta, phi, lam]:
                 # Check mod pi/2
                 if min(abs(p % (np.pi/2)), abs((p % (np.pi/2)) - (np.pi/2))) > 1e-4:
                     is_clifford = False
                     
            if not is_clifford:
                # Replace with Identity
                replaced_count += 1
                continue
            else:
                qc_backbone.append(inst.operation, inst.qubits)
        else:
            qc_backbone.append(inst.operation, inst.qubits)

            
    qc_backbone.measure_all()
    print(f"Replaced {replaced_count} complex gates with Identity.")
    
    # Debug: Check remaining
    final_counts = {}
    for inst in qc_backbone.data:
        final_counts[inst.operation.name] = final_counts.get(inst.operation.name, 0) + 1
        # Check params again?
        if inst.operation.name == 'u3':
            # Verify?
            pass
            
    print("Remaining Gates:", final_counts)
    
    # Transpile to basis supported by stabilizer
    # stabilize supports: cx, id, x, y, z, h, s, sdg, sx, sxdg
    # We must decompose the remaining U3s.
    
    qc_cliff = transpile(qc_backbone, 
                        basis_gates=['cx', 'cz', 'id', 'x', 'y', 'z', 'h', 's', 'sdg', 'sx', 'sxdg', 'rz'],
                        optimization_level=1) 
                        
    sim = AerSimulator(method='stabilizer')
    print("Simulating Backbone (Stabilizer) after transpile...")
    job = sim.run(qc_cliff, shots=1000)
    counts = job.result().get_counts()
    
    top = max(counts, key=counts.get)
    print(f"Backbone Result: {top}")
    
    # Save
    with open("results/p9_backbone.json", "w") as f:
         import json
         json.dump(counts, f)

if __name__ == "__main__":
    solve_backbone()
