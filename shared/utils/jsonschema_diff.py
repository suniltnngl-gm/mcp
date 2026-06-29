import json
from pathlib import Path

def jsonschema_diff(schema1_path: Path, schema2_path: Path) -> dict:
    """
    Compute the difference between two JSON schema versions.

    Args:
        schema1_path (Path): Path to the first JSON schema file.
        schema2_path (Path): Path to the second JSON schema file.

    Returns:
        dict: A dictionary describing the differences between the two schemas.
    """

    with schema1_path.open('r') as f1, schema2_path.open('r') as f2:
        schema1 = json.load(f1)
        schema2 = json.load(f2)

    def diff(obj1, obj2, path=''):
        diffs = {}
        if isinstance(obj1, dict) and isinstance(obj2, dict):
            for k in set(obj1) | set(obj2):
                v1 = obj1.get(k)
                v2 = obj2.get(k)
                if v1 != v2:
                    sub_path = f"{path}.{k}" if path else k
                    if isinstance(v1, (dict, list)) and isinstance(v2, (dict, list)):
                        sub_diffs = diff(v1, v2, sub_path)
                        if sub_diffs:
                            diffs[sub_path] = sub_diffs
                    else:
                        diffs[sub_path] = f"{v1} (schema1) vs {v2} (schema2)"
        elif obj1 != obj2:
            diffs[path] = f"{obj1} (schema1) vs {obj2} (schema2)"
        return diffs

    return diff(schema1, schema2)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: jsonschema-diff <schema1.json> <schema2.json>")
        sys.exit(1)

    schema1_path = Path(sys.argv[1])
    schema2_path = Path(sys.argv[2])

    diffs = jsonschema_diff(schema1_path, schema2_path)
    if diffs:
        print(json.dumps(diffs, indent=4))
    else:
        print("No differences found.")