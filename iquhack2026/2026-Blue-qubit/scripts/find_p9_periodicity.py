def find_periodicity():
    with open("challenge/P9_grand_summit.qasm", "r") as f:
        lines = f.readlines()
        
    cz_sequence = []
    for line in lines:
        if line.startswith("cz"):
            cz_sequence.append(line.strip())
            
    n = len(cz_sequence)
    print(f"Total CZ Gates: {n}")
    
    # Try different period lengths
    for period in range(10, n // 2):
        # Check if the first 'period' gates match the next 'period' gates
        # We allow for some small variation in rotations if we were looking at full blocks,
        # but for CZs they should be identical.
        matches = 0
        matches_count = 0
        for i in range(period):
            if cz_sequence[i] == cz_sequence[i + period]:
                matches += 1
        
        if matches / period > 0.9: # 90% overlap
            print(f"Potential Period Found: {period} (Overlap: {matches/period:.2f})")
            # Verify if it holds for the third step
            if 3 * period <= n:
                matches3 = 0
                for i in range(period):
                    if cz_sequence[i] == cz_sequence[i + 2*period]:
                        matches3 += 1
                print(f"  Third Step Overlap: {matches3/period:.2f}")
            
            # Print first few in period
            print(f"  First 5 in period: {cz_sequence[:5]}")
            break
    else:
        print("No simple periodic CZ sequence found.")

if __name__ == "__main__":
    find_periodicity()
