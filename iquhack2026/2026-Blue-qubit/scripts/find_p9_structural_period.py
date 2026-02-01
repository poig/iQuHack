def find_pair_periodicity():
    with open("challenge/P9_grand_summit.qasm", "r") as f:
        lines = f.readlines()
        
    pairs = []
    for line in lines:
        if line.startswith("cz"):
            # Extract q[i],q[j]
            import re
            match = re.search(r"q\[(\d+)\],q\[(\d+)\]", line)
            if match:
                u, v = sorted([int(match.group(1)), int(match.group(2))])
                pairs.append((u, v))
                
    n = len(pairs)
    print(f"Total CZ Pairs: {n}")
    
    # Check for repeating patterns in pairs
    for period in range(10, n // 2):
        matches = 0
        for i in range(period):
            if pairs[i] == pairs[i + period]:
                matches += 1
        
        if matches / period > 0.95:
            print(f"Structural Period Found: {period} (Pair Overlap: {matches/period:.2f})")
            # Check 3rd step
            if 3 * period <= n:
                m3 = 0
                for i in range(period):
                    if pairs[i] == pairs[i + 2*period]:
                        m3 += 1
                print(f"  Third Step Structural Overlap: {m3/period:.2f}")
            break
    else:
         print("No repeating structural interaction pattern found.")

if __name__ == "__main__":
    find_pair_periodicity()
