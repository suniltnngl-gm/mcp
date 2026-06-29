import os
import pathlib

def envdiff(path1: pathlib.Path, path2: pathlib.Path) -> None:
    """
    Compare environment variable sets between two files.

    Args:
    path1 (pathlib.Path): Path to the first environment file.
    path2 (pathlib.Path): Path to the second environment file.
    """

    try:
        with open(path1, 'r') as f1, open(path2, 'r') as f2:
            env1 = dict(line.strip().split('=', 1) for line in f1 if '=' in line)
            env2 = dict(line.strip().split('=', 1) for line in f2 if '=' in line)

        only_in_1 = {k: env1[k] for k in set(env1) - set(env2)}
        only_in_2 = {k: env2[k] for k in set(env2) - set(env1)}
        diff = {k: (env1[k], env2[k]) for k in set(env1) & set(env2) if env1[k] != env2[k]}

        print("Only in {}:".format(path1))
        for k, v in only_in_1.items():
            print(f"{k}={v}")

        print("\nOnly in {}:".format(path2))
        for k, v in only_in_2.items():
            print(f"{k}={v}")

        print("\nDifferences:")
        for k, (v1, v2) in diff.items():
            print(f"{k}: {v1} != {v2}")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=os.sys.stderr)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python envdiff.py <file1> <file2>", file=os.sys.stderr)
        sys.exit(1)

    path1 = pathlib.Path(sys.argv[1])
    path2 = pathlib.Path(sys.argv[2])

    envdiff(path1, path2)