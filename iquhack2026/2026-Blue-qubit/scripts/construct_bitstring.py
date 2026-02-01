import json
import numpy as np

def construct():
    try:
        with open("results/final_P9_local.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Results file not found.")
        return

    # Check for 56 qubits
    if len(data) != 56:
        print(f"Warning: Data contains {len(data)} qubits (expected 56).")

    # Construct bitstring (q55...q0)
    # Endianness: q0 is rightmost (Least Significant Bit)
    
    bits = ['?'] * 56
    magnitudes = []
    
    print("High Confidence Qubits (>0.4):")
    for k, v in data.items():
        if k.isdigit():
            idx = int(k)
            bit = v['bit']
            val = v['val']
            bits[idx] = bit
            magnitudes.append(abs(val))
            
            if abs(val) > 0.4:
                print(f"  Q{idx}: {bit} ({val:.3f})")

    final_str = "".join(list(reversed(bits)))
    avg_conf = np.mean(magnitudes) if magnitudes else 0
    
    print("\n[CANDIDATE SOLUTION]")
    print(f"Bitstring: {final_str}")
    print(f"Avg Confidence: {avg_conf:.3f}")
    
    # Check consistency with the strong signals
    # If the distribution is truly peaked, the weak ones might still be correct by sign.
    
    with open("solutions/p9_candidate.txt", "w") as f:
        f.write(final_str)
    print("Saved to solutions/p9_candidate.txt")

if __name__ == "__main__":
    construct()
