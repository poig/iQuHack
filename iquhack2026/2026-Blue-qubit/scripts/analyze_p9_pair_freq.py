from collections import Counter
import re

def analyze_freq():
    with open("challenge/P9_grand_summit.qasm", "r") as f:
        lines = f.readlines()
        
    pairs = []
    for line in lines:
        if line.startswith("cz"):
            match = re.search(r"q\[(\d+)\],q\[(\d+)\]", line)
            if match:
                u, v = sorted([int(match.group(1)), int(match.group(2))])
                pairs.append((u, v))
                
    counts = Counter(pairs)
    freq_dist = Counter(counts.values())
    
    print(f"Total Unique Pairs: {len(counts)}")
    print("Frequency Distribution:")
    for freq, count in sorted(freq_dist.items()):
        print(f"  {freq} times: {count} pairs")
        
    # Show some most common
    print("\nMost common pairs:")
    for pair, freq in counts.most_common(10):
        print(f"  {pair}: {freq} times")

if __name__ == "__main__":
    analyze_freq()
