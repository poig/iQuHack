from qiskit import QuantumCircuit
import matplotlib.pyplot as plt

def plot_density():
    qc = QuantumCircuit.from_qasm_file("challenge/P9_grand_summit.qasm")
    
    # Track depth of each instruction
    # qiskit.circuit.QuantumCircuit.depth() is a total. We want layer-wise.
    # We can use DAGCircuit or just track per-qubit time.
    
    qubit_time = [0] * qc.num_qubits
    layer_counts = {}
    
    for instruction in qc.data:
        qargs = [qc.find_bit(q).index for q in instruction.qubits]
        start_time = max(qubit_time[i] for i in qargs)
        duration = 1
        for i in qargs:
            qubit_time[i] = start_time + duration
        
        if len(qargs) == 2:
            layer_counts[start_time] = layer_counts.get(start_time, 0) + 1
            
    # Plotting
    times = sorted(layer_counts.keys())
    counts = [layer_counts[t] for t in times]
    
    plt.figure(figsize=(10, 5))
    plt.plot(times, counts)
    plt.title("CZ Gate Density per Layer")
    plt.xlabel("Layer Index")
    plt.ylabel("CZ Count")
    plt.savefig("p9_density.png")
    print(f"Max Layer: {max(times)}")
    print(f"Max CZ per Layer: {max(counts)}")

if __name__ == "__main__":
    plot_density()
