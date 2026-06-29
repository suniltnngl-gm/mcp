import pathlib
import sys

def csvhead(file_path: pathlib.Path, num_rows: int = 5) -> None:
    """
    Extract the first few rows from a large CSV file.

    Args:
    - file_path (pathlib.Path): Path to the CSV file.
    - num_rows (int): Number of rows to extract (default: 5).
    """
    try:
        with open(file_path, 'r') as file:
            for _ in range(num_rows):
                print(file.readline().rstrip())
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Extract the first few rows from a CSV file.')
    parser.add_argument('file', type=pathlib.Path, help='Path to the CSV file.')
    parser.add_argument('-n', '--num-rows', type=int, default=5, help='Number of rows to extract.')
    args = parser.parse_args()

    csvhead(args.file, args.num_rows)