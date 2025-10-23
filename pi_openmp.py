import random

try:
    from omp4py import omp, omp_set_num_threads  # type: ignore
    HAS_OMP = True
except ImportError:
    print("Warning: omp4py not installed. Running in sequential mode.")
    HAS_OMP = False
    # Fallback decorator
    def omp(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    def omp_set_num_threads(n):
        pass

# Set number of threads
if HAS_OMP:
    omp_set_num_threads(4)

@omp
def pi(num_points: int) -> float:
    """Calculate Pi using Monte Carlo method with OpenMP parallelization"""
    count = 0
    
    if HAS_OMP:
        # Parallel block: "parallel for" with reduction on count
        with omp("parallel for reduction(+:count)"):
            for i in range(num_points):
                x = random.random()
                y = random.random()
                
                if x*x + y*y <= 1.0:
                    count += 1
    else:
        # Sequential fallback
        for i in range(num_points):
            x = random.random()
            y = random.random()
            
            if x*x + y*y <= 1.0:
                count += 1
    
    # Pi estimation: (points in circle / total points) * 4
    pi_estimate = (count / num_points) * 4.0
    return pi_estimate

if __name__ == "__main__":
    import time
    
    num_points = 10_000_000
    
    print(f"Calculating Pi with {num_points:,} random points...")
    
    t0 = time.perf_counter()
    pi_value = pi(num_points)
    t1 = time.perf_counter()
    
    elapsed = t1 - t0
    error = abs(pi_value - 3.141592653589793)
    
    print(f"Estimated Pi: {pi_value:.10f}")
    print(f"Actual Pi:    3.1415926536")
    print(f"Error:        {error:.10f}")
    print(f"Time:         {elapsed:.3f} seconds")
    
    if HAS_OMP:
        print("Mode: OpenMP Parallel")
    else:
        print("Mode: Sequential (omp4py not available)")
