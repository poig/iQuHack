import json

def report():
    with open("results/final_P9.json", "r") as f:
        data = json.load(f)
        
    results = []
    for k, v in data.items():
        if k.isdigit():
            results.append((int(k), v['bit'], v['val']))
            
    results.sort(key=lambda x: x[0])
    
    print(f"{'Qubit':<6} {'Bit':<4} {'Confidence':<10} {'ID':<10}")
    print("-" * 35)
    for q, b, v in results:
        status = "CERTAIN" if abs(v) > 0.4 else ("MEDIUM" if abs(v) > 0.1 else "LOW")
        print(f"Q{q:02d}    {b}      {v: .4f}    [{status}]")

if __name__ == "__main__":
    report()
