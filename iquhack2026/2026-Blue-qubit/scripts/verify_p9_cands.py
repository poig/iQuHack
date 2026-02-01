from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import json

def verify_candidates():
    # Candidates
    candidates = {
        "Improved": "00111101110101010011100001111011110111100000111101010111",
        "PyZX":     "00111001000111000010100000111010111110110101001100001100",
        "Mine":     "11010001100000100110001000001111110000001100001010010011"
    }
    
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    qc.measure_all()
    
    # We want to check Probability(candidate).
    # Running full simulation is expensive.
    # But checking prob amplitude of ONE state is cheaper?
    # No, for MPS easier to sample.
    
    sim = AerSimulator(method='matrix_product_state', 
                       matrix_product_state_max_bond_dimension=64)
                       
    print("Running Verification MPS (BD=64)...")
    job = sim.run(transpile(qc, sim), shots=2000)
    counts = job.result().get_counts()
    
    print("\nCandidate Counts:")
    for name, s in candidates.items():
        print(f"  {name}: {counts.get(s, 0)}")
        
    # Also print top found
    top = max(counts, key=counts.get)
    print(f"\nTop Found in Run: {top} (Cnt: {counts[top]})")
    
    # Check Hamming to top
    def hamming(s1, s2): return sum(c1!=c2 for c1,c2 in zip(s1,s2))
    
    print(f"Hamming(Top, Improved): {hamming(top, candidates['Improved'])}")

if __name__ == "__main__":
    verify_candidates()
