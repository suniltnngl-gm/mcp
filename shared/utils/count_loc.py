import pathlib

def count_lines_of_code(directory: pathlib.Path) -> int:
    """
    Counts the lines of code in all files in the given directory and its subdirectories.

    Args:
        directory: The directory to start counting lines of code from.

    Returns:
        The total number of lines of code.
    """
    total_lines = 0
    for file in directory.rglob('*'):
        if file.is_file():
            try:
                with file.open('r', encoding='utf-8', errors='ignore') as f:
                    total_lines += sum(1 for _ in f)
            except Exception as e:
                print(f"Error reading file {file}: {e}")
    return total_lines

def main() -> None:
    directory = pathlib.Path('.')
    print(f"Lines of code in '{directory}': {count_lines_of_code(directory)}")

if __name__ == "__main__":
    main()