import argparse
import time
from src.data_loader import load_problem_instance
from src.models import ProblemInstance
from src.heuristics import greedy_heuristic

def main():
    """
    Main script to run the benchmarking pipeline.
    It loads problem instances, runs a heuristic, and compares the result
    against the optimal solution.
    """
    parser = argparse.ArgumentParser(description="Benchmark task allocation heuristics.")
    parser.add_argument("--start_instance", type=int, default=0,
                        help="The starting ID of the problem instance to benchmark.")
    parser.add_argument("--end_instance", type=int, default=9,
                        help="The ending ID of the problem instance to benchmark (inclusive).")
    args = parser.parse_args()

    print(f"--- Running Benchmark for Instances {args.start_instance} to {args.end_instance} ---")

    results = []
    total_time = 0

    for i in range(args.start_instance, args.end_instance + 1):
        print(f"\nProcessing instance {i}...")

        # Load data
        problem_data, optimal_solution = load_problem_instance(i)
        if not problem_data or not optimal_solution:
            print(f"Skipping instance {i} due to missing data.")
            continue

        # Create problem model
        problem_instance = ProblemInstance(problem_data)

        # Run heuristic
        start_time = time.time()
        heuristic_solution = greedy_heuristic(problem_instance)
        end_time = time.time()

        duration = end_time - start_time
        total_time += duration

        # --- Analysis ---
        # Compare the heuristic's makespan to the optimal makespan.
        optimal_makespan = optimal_solution["makespan"]
        heuristic_makespan = heuristic_solution["makespan"]

        # Calculate the performance ratio. A value close to 1.0 is good.
        # Ratio > 1.0 means the heuristic was worse than optimal.
        # Ratio < 1.0 means the heuristic was better than the provided "optimal" solution.
        if optimal_makespan > 0:
            ratio = heuristic_makespan / optimal_makespan
        else:
            # Handle cases where optimal makespan is zero.
            ratio = float('inf') if heuristic_makespan > 0 else 1.0

        # Store the results for this instance
        results.append({
            "instance_id": i,
            "optimal_makespan": optimal_makespan,
            "heuristic_makespan": heuristic_makespan,
            "ratio": ratio,
            "duration": duration
        })

        print(f"  Optimal Makespan: {optimal_makespan:.2f}")
        print(f"  Heuristic Makespan: {heuristic_makespan:.2f} (Ratio: {ratio:.3f})")
        print(f"  Time taken: {duration:.4f}s")

    # --- Summary ---
    if not results:
        print("\nNo instances were processed.")
        return

    avg_ratio = sum(r['ratio'] for r in results) / len(results)
    avg_duration = total_time / len(results)

    print("\n--- Benchmark Summary ---")
    print(f"Processed {len(results)} instances.")
    print(f"Average Heuristic/Optimal Ratio: {avg_ratio:.4f}")
    print(f"Average Time per Instance: {avg_duration:.4f}s")
    print("-------------------------")


if __name__ == "__main__":
    main()
