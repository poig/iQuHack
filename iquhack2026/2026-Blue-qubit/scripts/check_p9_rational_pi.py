import re
import math

def check_rational_pi():
    with open("challenge/P9_grand_summit.qasm", "r") as f:
        content = f.read()
        
    # Extract all floats
    floats = re.findall(r"[-+]?\d*\.\d+|\d+", content)
    unique_floats = sorted(list(set(float(x) for x in floats if "." in x)))
    
    pi = math.pi
    print(f"Total unique floats: {len(unique_floats)}")
    
    rational_matches = 0
    for val in unique_floats:
        # Check for multiples of pi/k for k up to 24
        found = False
        for k in range(1, 25):
            for n in range(-24, 25):
                target = (n * pi) / k
                if abs(val - target) < 1e-4:
                    # print(f"{val:.6f} approx {n}*pi/{k}")
                    rational_matches += 1
                    found = True
                    break
            if found: break
            
    print(f"Rational Pi Multiples: {rational_matches}")

if __name__ == "__main__":
    check_rational_pi()
