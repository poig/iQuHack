import re
import numpy as np

def analyze_params():
    with open("challenge/P9_grand_summit.qasm", "r") as f:
        content = f.read()
        
    # Extract u3(theta, phi, lambda)
    # Actually, let's just extract all floats in order
    matches = re.findall(r"[-+]?\d*\.\d+|\d+", content)
    params = [float(x) for x in matches if "." in x]
    
    n = len(params)
    print(f"Total float parameters: {n}")
    
    # Check for mirror symmetry across a pivot
    best_pivot = 0
    max_corr = 0
    
    # Try different pivot points (where the circuit might be mirrored)
    for pivot in range(n // 4, 3 * n // 4, 10):
        # Compare params[pivot-k] with params[pivot+k]
        size = min(pivot, n - pivot)
        p1 = np.array(params[pivot-size:pivot])
        p2 = np.array(params[pivot:pivot+size][::-1]) # Reversed
        
        # Cross-correlation or just difference
        diff = np.mean(np.abs(p1 - p2))
        corr = np.corrcoef(p1, p2)[0, 1]
        
        if abs(corr) > abs(max_corr):
            max_corr = corr
            best_pivot = pivot
            
    print(f"Best parameter pivot found at match index {best_pivot}")
    print(f"Correlation: {max_corr:.4f}")
    
    # Check per-qubit gate sequence symmetry?
    # This might be more robust to permutations if we look at qubit-wise.

if __name__ == "__main__":
    analyze_params()
