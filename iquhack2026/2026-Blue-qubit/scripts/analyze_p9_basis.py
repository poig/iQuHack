from qiskit import QuantumCircuit
import numpy as np

def analyze_p9_basis():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    
    print(f"Total instructions: {len(qc.data)}")
    
    gate_counts = {}
    u3_types = {"clifford": 0, "rz_like": 0, "rx_like": 0, "complex": 0}
    
    for inst in qc.data:
        name = inst.operation.name
        gate_counts[name] = gate_counts.get(name, 0) + 1
        
        if name == 'u3':
            # U3(theta, phi, lam)
            # Rz(lam) Ry(theta) Rz(phi)
            # If theta = 0, it is Rz(phi+lam). (Diagonal)
            # If theta = pi, it is X * Phase. (Bit Flip)
            # If theta = pi/2, it is H-like (Basis Change).
            
            theta, phi, lam = inst.operation.params
            
            # Check theta
            t_pi = theta / np.pi
            is_zero = abs(theta) < 1e-5
            is_pi = abs(abs(theta) - np.pi) < 1e-5
            is_half = abs(abs(theta) - np.pi/2) < 1e-5
            
            if is_zero:
                u3_types["rz_like"] += 1
            elif is_pi:
                u3_types["clifford"] += 1 # Bit flip
            elif is_half:
                u3_types["clifford"] += 1 # Superposition
            else:
                u3_types["complex"] += 1 # Arbitrary rotation
                
    print("\nGate Counts:", gate_counts)
    print("U3 Analysis:", u3_types)

if __name__ == "__main__":
    analyze_p9_basis()
