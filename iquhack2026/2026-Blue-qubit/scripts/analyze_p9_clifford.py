import re
import math

def analyze_gates():
    with open("challenge/P9_grand_summit.qasm", "r") as f:
        lines = f.readlines()
        
    u3_count = 0
    clifford_like = 0
    pi = math.pi
    
    # Regex to find u3 parameters
    # u3(val, val, val)
    pattern = re.compile(r'u3\(([^,]+),([^,]+),([^,]+)\)')
    
    unique_params = set()
    
    for line in lines:
        match = pattern.search(line)
        if match:
            u3_count += 1
            p1, p2, p3 = match.groups()
            unique_params.add((p1, p2, p3))
            
            # Helper to evaluate expression
            def eval_p(p):
                try:
                    # Replace pi with math.pi
                    p_eval = p.replace('pi', str(pi))
                    return eval(p_eval)
                except:
                    return None
            
            params = [eval_p(p) for p in [p1, p2, p3]]
            
            if None not in params:
                # Check if multiple of pi/2
                is_clifford = True
                for p in params:
                    # Normalize to [0, 2pi)
                    p_norm = p % (2*pi)
                    # Check if close to 0, pi/2, pi, 3pi/2
                    dists = [abs(p_norm - k*pi/2) for k in range(5)]
                    if min(dists) > 1e-4:
                        is_clifford = False
                        break
                if is_clifford:
                    clifford_like += 1
                    
    print(f"Total U3 Gates: {u3_count}")
    print(f"Clifford-like (multiples of pi/2): {clifford_like}")
    print(f"Unique Parameter Sets: {len(unique_params)}")
    
    if len(unique_params) < 50:
        print("Unique Params:")
        for p in unique_params:
            print(f"  {p}")

if __name__ == "__main__":
    analyze_gates()
