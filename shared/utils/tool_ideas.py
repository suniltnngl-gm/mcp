import pathlib
import shutil

def main(src: pathlib.Path, dst: pathlib.Path) -> None:
    """
    Copy a file from source to destination.

    Args:
        src (pathlib.Path): Source file path.
        dst (pathlib.Path): Destination file path.
    """
    if not src.exists():
        raise FileNotFoundError(f"Source file '{src}' does not exist.")

    shutil.copy2(src, dst)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python file_copy.py <src> <dst>")
        sys.exit(1)

    src = pathlib.Path(sys.argv[1])
    dst = pathlib.Path(sys.argv[2])

    try:
        main(src, dst)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)