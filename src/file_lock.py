import os
import time
from contextlib import contextmanager


@contextmanager
def file_lock(lock_path: str, timeout: float = 60.0, poll_interval: float = 0.1):
    start = time.time()
    fd = None

    while fd is None:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.write(fd, str(os.getpid()).encode("utf-8"))
        except FileExistsError:
            if (time.time() - start) >= timeout:
                raise TimeoutError(f"Timed out waiting for lock: {lock_path}")
            time.sleep(poll_interval)

    try:
        yield
    finally:
        if fd is not None:
            os.close(fd)
        if os.path.exists(lock_path):
            os.unlink(lock_path)
