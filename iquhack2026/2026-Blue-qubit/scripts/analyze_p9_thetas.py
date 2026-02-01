import re
import matplotlib.pyplot as plt

def analyze_theta():
    with open("challenge/P9_grand_summit.qasm", "r") as f:
        content = f.read()
        
    # Extract u3(theta, phi, lambda)
    thetas = re.findall(r"u3\(([-+]?\d*\.\d+|\d+),", content)
    thetas = [float(x) for x in thetas]
    
    print(f"Total U3: {len(thetas)}")
    print(f"Min Theta: {min(thetas):.4f}")
    print(f"Max Theta: {max(thetas):.4f}")
    
    plt.figure(figsize=(10, 5))
    plt.hist(thetas, bins=50)
    plt.title("Distribution of U3 Theta Parameters")
    plt.savefig("p9_thetas.png")

if __name__ == "__main__":
    analyze_theta()
