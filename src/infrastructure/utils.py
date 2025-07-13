import time
import functools
import logging
import sys

# Configuración global de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("output.log", mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)  # Opcional: también muestra en consola
    ]
)

# Redefinir print para que use logging.info
print = lambda *args, **kwargs: logging.info(' '.join(str(a) for a in args))

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
            logging.info(f"Finished '{func.__name__}' in {run_time:.4f} secs")
    return wrapper 