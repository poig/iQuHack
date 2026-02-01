import re

def analyze_reps():
    with open("challenge/P9_grand_summit.qasm", "r") as f:
        lines = f.readlines()
        
    pair_history = {} # qubit -> last pair it was in
    reps = 0
    total_cz = 0
    
    for line in lines:
        if line.startswith("cz"):
            total_cz += 1
            match = re.search(r"q\[(\d+)\],q\[(\d+)\]", line)
            if match:
                u, v = sorted([int(match.group(1)), int(match.group(2))])
                pair = (u, v)
                
                # Check if this pair was the last interaction for both qubits
                if pair_history.get(u) == pair and pair_history.get(v) == pair:
                    reps += 1
                
                pair_history[u] = pair
                pair_history[v] = pair
                
    print(f"Total CZ: {total_cz}")
    print(f"Immediate Pair Repetitions: {reps} ({reps/total_cz:.2%})")

if __name__ == "__main__":
    analyze_reps()
