
import json
import time
from pathlib import Path
from solve_circuit import solve

CIRCUITS = {
    "P1": "P1_little_peak.qasm",
    "P2": "P2_small_bump.qasm",
    "P3": "P3_tiny_ripple.qasm",
    "P4": "P4_gentle_mound.qasm",
    "P5": "P5_soft_rise.qasm",
    "P6": "P6_low_hill.qasm",
    "P7": "P7_rolling_ridge.qasm",
    "P8": "P8_bold_peak.qasm",
    "P9": "P9_grand_summit.qasm",
    "P10": "P10_eternal_mountain.qasm",
}

CIRCUIT_OVERRIDES = {
    "P6": {"skip_pyzx": True, "approx_degree": 0.99},
}

def run_all(qasm_dir: str = "challenge", output_dir: str = "results", shots: int = 1000, bond_dim: int = 128):
    qasm_dir_p = Path(qasm_dir)
    output_dir_p = Path(output_dir)
    output_dir_p.mkdir(exist_ok=True)

    results = {}
    print("\n" + "=" * 70 + "\nSOLVING ALL CIRCUITS\n" + "=" * 70)

    for name, filename in CIRCUITS.items():
        qasm_file = qasm_dir_p / filename
        if not qasm_file.exists():
            print(f"Skipping {name}: {qasm_file} not found")
            continue

        overrides = CIRCUIT_OVERRIDES.get(name, {})
        try:
            res = solve(str(qasm_file), shots=shots, bond_dim=bond_dim, **overrides)
            results[name] = res["bitstring"]
            # Save individual JSON
            with open(output_dir_p / f"{name}_res.json", "w") as f:
                json.dump(res, f, indent=2)
        except Exception as e:
            print(f"Error on {name}: {e}")

    print("\n" + "=" * 70 + "\nSUMMARY\n" + "=" * 70)
    for name, bs in results.items():
        print(f"{name:<5}: {bs}")

    with open(output_dir_p / "p1_p10_final.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_all()
