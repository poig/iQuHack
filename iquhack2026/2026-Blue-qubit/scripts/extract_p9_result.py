import json

def extract_bitstring():
    with open("results/final_P9.json", "r") as f:
        data = json.load(f)
    
    n = 56
    bitstring = ['?'] * n
    
    for k, v in data.items():
        idx = int(k)
        bit = v['bit']
        if 0 <= idx < n:
            bitstring[idx] = bit
            
    # Check completeness
    if '?' in bitstring:
        print("Incomplete bitstring!")
    else:
        # P9 format: qN-1 ... q0
        final_str = "".join(bitstring[::-1])
        print(f"Final Bitstring (q55..q0): {final_str}")

if __name__ == "__main__":
    extract_bitstring()
