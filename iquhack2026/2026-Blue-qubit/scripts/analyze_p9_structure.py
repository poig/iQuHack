from collections import Counter
import re

def analyze_structural_symmetry():
    with open("challenge/P9_grand_summit.qasm", "r") as f:
        lines = f.readlines()
        
    pairs = []
    for line in lines:
        if line.startswith("cz"):
            match = re.search(r"q\[(\d+)\],q\[(\d+)\]", line)
            if match:
                u, v = sorted([int(match.group(1)), int(match.group(2))])
                pairs.append((u, v))
                
    n = len(pairs)
    mid = n // 2
    
    # Counter for first half and second half
    first_half = Counter(pairs[:mid])
    second_half = Counter(pairs[mid:])
    
    # Intersection of pairs
    common = set(first_half.keys()) & set(second_half.keys())
    print(f"Total CZ pairs: {n}")
    print(f"Unique pairs in 1st half: {len(first_half)}")
    print(f"Unique pairs in 2nd half: {len(second_half)}")
    print(f"Common pairs: {len(common)}")
    
    # If it's a simple U-Udagger, common should be very high.
    # If there's a Permutation, the pairs will different but the GRAPH will be isomorphic.
    
    # Check degree distribution (how many neighbors each qubit has in each half)
    def get_degrees(counter):
        degs = Counter()
        for (u, v), count in counter.items():
            degs[u] += count
            degs[v] += count
        return sorted(list(degs.values()))

    d1 = get_degrees(first_half)
    d2 = get_degrees(second_half)
    
    # Compare degree distributions (sorted)
    # If isomorphic, degree distributions must match perfectly.
    same_dist = (d1 == d2)
    print(f"Degree Distributions Match: {same_dist}")
    
    if not same_dist:
        # Check similarity (e.g., MSE of degree ranks)
        maxlen = max(len(d1), len(d2))
        d1_pad = d1 + [0]*(maxlen - len(d1))
        d2_pad = d2 + [0]*(maxlen - len(d2))
        mse = np.mean((np.array(d1_pad) - np.array(d2_pad))**2)
        print(f"Degree Correlation (MSE): {mse:.2f}")

if __name__ == "__main__":
    import numpy as np
    analyze_structural_symmetry()
