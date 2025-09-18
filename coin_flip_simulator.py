import os
import argparse
import random
from qiskit import QuantumCircuit
from qiskit_aer.primitives import Sampler as AerSampler
from qiskit.visualization import plot_histogram
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler as IBMSampler
import matplotlib.pyplot as plt

def classical_coin_flip(shots=1000):
    """Simulate a classical random coin flip."""
    heads = sum(1 for _ in range(shots) if random.choice([0, 1]) == 1)
    tails = shots - heads
    return {'0': tails, '1': heads}  # 0 for tails, 1 for heads

def run_on_simulator(qc, shots=1000):
    """Run the quantum circuit on the simulator."""
    sampler = AerSampler()
    job = sampler.run([qc], shots=shots)
    result = job.result()
    quasi_dist = result.quasi_dists[0]
    # Convert to dict for plotting
    return {key: int(value * shots) for key, value in quasi_dist.items()}

def run_on_real_device(qc, shots=1000):
    """Run the quantum circuit on a real IBM Quantum device."""
    # Prompt for API token if not set
    api_token = input("Enter your IBM Quantum API token: ").strip()
    if not api_token:
        raise ValueError("API token is required for real device runs.")

    # Authenticate
    service = QiskitRuntimeService(channel="ibm_quantum", token=api_token)

    # Select the least busy backend
    backend = service.least_busy(operational=True, simulator=False)
    print(f"Running on real device: {backend.name}")

    # Use Sampler for runtime
    sampler = IBMSampler(backend)
    job = sampler.run([qc], shots=shots)
    result = job.result()
    quasi_dist = result.quasi_dists[0]
    # Convert to dict for plotting
    return {key: int(value * shots) for key, value in quasi_dist.items()}

def main():
    parser = argparse.ArgumentParser(description="Quantum Coin Flip Simulation")
    parser.add_argument('--real', action='store_true', help="Run on real IBM Quantum hardware")
    parser.add_argument('--shots', type=int, default=1000, help="Number of shots (default: 1000)")
    args = parser.parse_args()

    # Ensure results directory exists
    os.makedirs('results', exist_ok=True)

    # Create Quantum Circuit
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)

    print("Quantum Coin Flip Circuit:")
    print(qc.draw('text'))

    # Classical Coin Flip
    print("\nRunning Classical Coin Flip...")
    classical_counts = classical_coin_flip(args.shots)
    print("Classical Results:", classical_counts)
    plot_histogram(classical_counts, title="Classical Coin Flip")
    plt.savefig("results/classical_histogram.png")
    plt.show()

    # Quantum Coin Flip
    if args.real:
        print("\nRunning Quantum Coin Flip on Real Device...")
        quantum_counts = run_on_real_device(qc, args.shots)
        filename = "results/real_device_histogram.png"
        title = "Quantum Coin Flip (Real Device)"
    else:
        print("\nRunning Quantum Coin Flip on Simulator...")
        quantum_counts = run_on_simulator(qc, args.shots)
        filename = "results/simulator_histogram.png"
        title = "Quantum Coin Flip (Simulator)"

    print("Quantum Results:", quantum_counts)
    plot_histogram(quantum_counts, title=title)
    plt.savefig(filename)
    plt.show()

    print(f"\nHistograms saved to results/ directory.")

if __name__ == "__main__":
    main()
