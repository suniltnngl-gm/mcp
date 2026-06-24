import json
import sys
from pathlib import Path

from src.hf_cli.client import search_models, search_datasets, list_files, repo_info
from src.hf_cli.download import download_model, download_dataset, cache_info, cache_clear
from src.hf_cli.push import upload_file


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return

    cmd = args[0]
    rest = args[1:]

    if cmd == "search":
        query = " ".join(rest) if rest else input("Search query: ")
        models = search_models(query)
        datasets = search_datasets(query)
        print(f"\n  Models ({len(models)}):")
        for m in models[:10]:
            print(f"    • {m.get('id', m.get('modelId', '?'))}")
        print(f"\n  Datasets ({len(datasets)}):")
        for d in datasets[:10]:
            print(f"    • {d.get('id', d.get('datasetId', '?'))}")

    elif cmd == "files":
        if not rest:
            print("  Usage: hf files <repo_id> [path]")
            return
        repo = rest[0]
        path = rest[1] if len(rest) > 1 else ""
        files = list_files(repo, path)
        print(f"\n  Files in {repo}{'/' + path if path else ''}:")
        for f in files[:30]:
            tp = "📁" if f.get("type") == "directory" else "📄"
            size = f.get("size", "")
            s = f" ({size} bytes)" if size else ""
            print(f"    {tp} {f.get('path', '?')}{s}")

    elif cmd == "info":
        if not rest:
            print("  Usage: hf info <repo_id>")
            return
        info = repo_info(rest[0])
        if info:
            print(f"\n  {info.get('id', rest[0])}")
            print(f"    Downloads: {info.get('downloads', '?')}")
            print(f"    Likes:     {info.get('likes', '?')}")
            print(f"    Pipeline:  {info.get('pipeline_tag', '?')}")
            if info.get("tags"):
                print(f"    Tags:      {', '.join(info['tags'][:10])}")
        else:
            print(f"  Repo not found: {rest[0]}")

    elif cmd == "dl" or cmd == "download":
        if len(rest) < 1:
            print("  Usage: hf dl <repo_id> [filename]")
            return
        repo = rest[0]
        filename = rest[1] if len(rest) > 1 else None
        result = download_model(repo, filename)
        if "error" in result:
            print(f"  ❌ {result['error']}")
        elif result.get("cached"):
            print(f"  ✅ Cached: {result['path']} ({result['size']} bytes)")
        else:
            print(f"  ✅ Downloaded: {result['path']} ({result['size']} bytes)")

    elif cmd == "dl-dataset":
        if len(rest) < 1:
            print("  Usage: hf dl-dataset <repo_id> [filename]")
            return
        repo = rest[0]
        filename = rest[1] if len(rest) > 1 else None
        result = download_dataset(repo, filename)
        if "error" in result:
            print(f"  ❌ {result['error']}")
        elif result.get("cached"):
            print(f"  ✅ Cached: {result['path']} ({result['size']} bytes)")
        else:
            print(f"  ✅ Downloaded: {result['path']} ({result['size']} bytes)")

    elif cmd == "push":
        if len(rest) < 2:
            print("  Usage: hf push <local_path> <repo_id> [message]")
            return
        local = Path(rest[0])
        repo = rest[1]
        msg = " ".join(rest[2:]) if len(rest) > 2 else "upload via hf-cli"
        if not local.exists():
            print(f"  ❌ Path not found: {local}")
            return
        result = upload_file("model", repo, local, message=msg)
        if "error" in result:
            print(f"  ❌ {result['error']}")
        else:
            print(f"  ✅ Pushed to {result['repo']}")

    elif cmd == "cache":
        info = cache_info()
        print(f"\n  Cache: {info['entries']} entries, {info['total_size_mb']} MB")
        if "--clear" in rest:
            key = rest[1] if len(rest) > 1 and rest[1] != "--clear" else None
            cache_clear(key)
            print("  ✅ Cache cleared")

    elif cmd == "json":
        if len(rest) < 1:
            print("  Usage: hf json <search|files|info> <args...>")
            return
        sub = rest[0]
        sub_rest = rest[1:]
        if sub == "search":
            q = " ".join(sub_rest) if sub_rest else ""
            print(json.dumps(search_models(q) + search_datasets(q), indent=2))
        elif sub == "files":
            repo = sub_rest[0] if sub_rest else ""
            path = sub_rest[1] if len(sub_rest) > 1 else ""
            print(json.dumps(list_files(repo, path), indent=2))
        elif sub == "info":
            repo = sub_rest[0] if sub_rest else ""
            print(json.dumps(repo_info(repo), indent=2))

    elif cmd in ("-h", "--help"):
        print("""hf-cli — Hugging Face Hub CLI

Commands:
  search <query>       Search models + datasets
  files <repo> [path]  List files in a repo
  info <repo>          Show repo metadata
  dl <repo> [file]     Download model (with resume + cache)
  dl-dataset <repo>    Download dataset
  push <path> <repo>   Upload files to repo
  cache                Show cache info (--clear to flush)
  json <sub> <args>    JSON output (for scripting)
""")

    else:
        print(f"  Unknown: {cmd}. Use --help for commands.")


if __name__ == "__main__":
    main()
