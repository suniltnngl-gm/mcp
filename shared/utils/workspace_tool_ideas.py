import pathlib
import os

def list_files(directory: pathlib.Path) -> None:
    """
    Lists all files in a given directory.

    Args:
        directory (pathlib.Path): The directory to list files from.
    """
    if directory.exists() and directory.is_dir():
        for file in directory.iterdir():
            if file.is_file():
                print(file.name)
    else:
        print(f"Error: '{directory}' is not a valid directory.")

if __name__ == "__main__":
    current_dir = pathlib.Path(os.getcwd())
    print(f"Files in '{current_dir}':")
    list_files(current_dir)