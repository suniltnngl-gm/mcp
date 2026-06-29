import pathlib
import os
import sys

def main(argv=None):
    """
    Compare environment variable settings between two shells.

    Usage: envdiff <file1> <file2>
    Each file should contain environment variable settings in the format:
    VAR=value
    """

    if argv is None:
        argv = sys.argv[1:]

    if len(argv) != 2:
        print("Usage: envdiff <file1> <file2>", file=sys.stderr)
        return 1

    file1 = pathlib.Path(argv[0])
    file2 = pathlib.Path(argv[1])

    if not file1.exists() or not file2.exists():
        print("Both files must exist", file=sys.stderr)
        return 1

    env1 = {}
    env2 = {}

    with file1.open('r') as f:
        for line in f:
            line = line.strip()
            if line and '=' in line:
                var, _, value = line.partition('=')
                env1[var] = value

    with file2.open('r') as f:
        for line in f:
            line = line.strip()
            if line and '=' in line:
                var, _, value = line.partition('=')
                env2[var] = value

    only_in_1 = {var: value for var, value in env1.items() if var not in env2}
    only_in_2 = {var: value for var, value in env2.items() if var not in env1}
    different = {var: (env1[var], env2[var]) for var in env1 if var in env2 and env1[var] != env2[var]}

    print("Only in", file1)
    for var, value in only_in_1.items():
        print(f"{var}={value}")

    print("\nOnly in", file2)
    for var, value in only_in_2.items():
        print(f"{var}={value}")

    print("\nDifferent")
    for var, (value1, value2) in different.items():
        print(f"{var}: {value1} != {value2}")

if __name__ == "__main__":
    main()