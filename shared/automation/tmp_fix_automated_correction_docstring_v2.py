file_path = "/home/shekinah/Public/Shekinah/new_project/scripts/automated_correction.py"

old_docstring_content = (
    '        """Check if solution context matches current situation"'
)
new_docstring_line = '        """Check if solution context matches current situation""'

try:
    with open(file_path, "r") as f:
        lines = f.readlines()

    print(f"--- Debugging {file_path} ---")
    print(f"Looking for: '{old_docstring_content}'")
    print("--- File Content ---")

    modified = False
    for i, line in enumerate(lines):
        print(
            f"Line {i+1}: '{line.strip()}'"
        )  # .strip() to remove trailing newline for cleaner output
        if old_docstring_content in line:
            lines[i] = new_docstring_line
            modified = True
            break

    print("--- End File Content ---")

    if modified:
        with open(file_path, "w") as f:
            f.writelines(lines)
        print(f"Successfully fixed docstring in {file_path}")
    else:
        print(f"Docstring not found or already correct in {file_path}")

except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")
