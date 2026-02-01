
from qiskit import QuantumCircuit
import numpy as np
import collections

def analyze_angles():
    path = "bitcoin_problem/P1_little_dimple.qasm"
    qc = QuantumCircuit.from_qasm_file(path)
    
    angles = []
    for inst in qc.data:
        if inst.operation.name == 'u':
            # u(theta, phi, lambda)
            p = inst.operation.params
            angles.extend([float(x) for x in p])
            
    # Check for small vs large angles
    rounded = [round(a / (np.pi/4)) for a in angles]
    counts = collections.Counter(rounded)
    print("Multiples of Pi/4:")
    for m, c in sorted(counts.items()):
        print(f"  {m}*Pi/4: {c}")

    non_clifford = 0
    for a in angles:
        # Check if it's close to m * Pi/2
        if not any(np.isclose(a % (np.pi/2), [0, np.pi/2], atol=1e-5)):
            non_clifford += 1
            
    print(f"\nTotal params: {len(angles)}")
    print(f"Potentially non-Clifford params: {non_clifford}")

if __name__ == "__main__":
    analyze_angles()
