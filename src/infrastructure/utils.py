import time
import functools

def timing_decorator(func):
    """
    A decorator that logs the execution time of a function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Wrapper function to time the decorated function."""
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            run_time = end_time - start_time
            print(f"Finished '{func.__name__}' in {run_time:.4f} secs")
    return wrapper 