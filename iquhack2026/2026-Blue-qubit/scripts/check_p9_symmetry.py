import re

def check_mirror_symmetry():
    with open("challenge/P9_grand_summit.qasm", "r") as f:
        lines = f.readlines()
        
    pairs = []
    for line in lines:
        if line.startswith("cz"):
            match = re.search(r"q\[(\d+)\],q\[(\d+)\]", line)
            if match:
                u, v = sorted([int(match.group(1)), int(match.group(2))])
                pairs.append((u, v))
                
    n_qubits = 56
    mirrored_pairs = []
    for u, v in pairs:
        mu, mv = sorted([n_qubits - 1 - u, n_qubits - 1 - v])
        mirrored_pairs.append((mu, mv))
        
    n = len(pairs)
    symmetry_score = 0
    for i in range(n):
        if pairs[i] == mirrored_pairs[i]:
            symmetry_score += 1
            
    print(f"Total CZ Gates: {n}")
    print(f"Mirror Symmetry Matches: {symmetry_score} ({symmetry_score/n:.2%})")
    
    # Check if the sequence itself is mirrored (first gate matches mirror of last gate?)
    rev_mirrored = mirrored_pairs[::-1]
    rev_symmetry = 0
    for i in range(n):
        if pairs[i] == rev_mirrored[i]:
            rev_symmetry += 1
    print(f"Reverse Mirror Symmetry Matches: {rev_symmetry} ({rev_symmetry/n:.2%})")

if __name__ == "__main__":
    check_mirror_symmetry()
