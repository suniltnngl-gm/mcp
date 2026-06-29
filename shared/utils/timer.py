import time
import pathlib
import sys

def timer(cmd: str) -> None:
    """
    Measure the execution time of a command.

    Args:
    cmd (str): The command to be executed.
    """
    start_time = time.time()
    try:
        output = subprocess.check_output(cmd, shell=True, text=True)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Execution time: {elapsed_time:.6f} seconds")
        print(output, end='')
    except subprocess.CalledProcessError as e:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Execution time: {elapsed_time:.6f} seconds", file=sys.stderr)
        print(e.output, end='', file=sys.stderr)
        sys.exit(e.returncode)

if __name__ == "__main__":
    import subprocess
    if len(sys.argv) < 2:
        print("Usage: python timer.py <command>", file=sys.stderr)
        sys.exit(1)
    cmd = ' '.join(sys.argv[1:])
    timer(cmd)