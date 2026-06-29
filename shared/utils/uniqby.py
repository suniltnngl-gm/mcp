import pathlib
from typing import List

def uniqby(file_path: pathlib.Path, column: int) -> None:
    """
    Remove duplicate lines from a file based on a specific column.

    Args:
    - file_path (pathlib.Path): Path to the input file.
    - column (int): 0-based column index to consider for duplicates.

    The output will overwrite the input file.
    """
    try:
        with file_path.open('r') as file:
            lines = file.readlines()

        seen = set()
        output_lines: List[str] = []

        for line in lines:
            columns = line.strip().split()
            if len(columns) <= column:
                raise ValueError(f"Line '{line.strip()}' has fewer than {column+1} columns")

            key = columns[column]
            if key not in seen:
                seen.add(key)
                output_lines.append(line)

        with file_path.open('w') as file:
            file.writelines(output_lines)

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python uniqby.py <file_path> <column>", file=sys.stderr)
        sys.exit(1)

    file_path = pathlib.Path(sys.argv[1])
    try:
        column = int(sys.argv[2])
    except ValueError:
        print("Column must be an integer", file=sys.stderr)
        sys.exit(1)

    uniqby(file_path, column)