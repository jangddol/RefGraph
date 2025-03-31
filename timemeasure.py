import time

# Dictionary to store execution times for each function
execution_times = {}

def timeit(func):
    """
    Decorator to measure the execution time of a function.
    """
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        execution_times[func.__name__] = execution_times.get(func.__name__, 0) + elapsed_time
        return result
    return wrapper

def print_execution_times():
    """
    Print the total execution time for each function when the program exits.
    """
    print("\nExecution times for each function:")
    for func_name, total_time in execution_times.items():
        print(f"  {func_name}: {total_time:.4f} seconds")
