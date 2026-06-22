"""Brain CLI — manage lesson cache and context graph."""

import json


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Brain — self-improving memory for agents")
    parser.add_argument("command", nargs="?",
                        choices=["learn", "status", "graph", "sync", "search"])
    parser.add_argument("args", nargs="*", help="Command arguments")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    from brain import LessonCache, ContextGraph, overnight_sync

    if args.command == "learn":
        cache = LessonCache()
        task = args.args[0] if args.args else ""
        correction = " ".join(args.args[1:]) if len(args.args) > 1 else ""
        source = "cli"
        if not task:
            print("Usage: brain learn <task> <correction> [--source <src>]")
            return
        lid = cache.add_lesson(task, correction, source)
        cache.save()
        print(f"Learned lesson {lid}: '{task}' → '{correction}'")
        return

    if args.command == "status":
        cache = LessonCache()
        s = cache.stats()
        if args.json:
            print(json.dumps(s))
        else:
            print(f"Lessons: {s['total_lessons']} total, {s['applied']} applied")
            print(f"Suppressions: {s['active_suppressions']} active, {s['total_suppressed']} total hits")
        return

    if args.command == "graph":
        graph = ContextGraph()
        s = graph.stats()
        if args.json:
            print(json.dumps(s))
        else:
            print(f"Context graph: {s['total_entries']} entries")
            for t, c in s.get("by_type", {}).items():
                print(f"  {t}: {c}")
        return

    if args.command == "sync":
        result = overnight_sync()
        print(f"Overnight sync complete: {result['lessons_added']} lessons, {result['context_entries']} context entries")
        return

    if args.command == "search":
        query = " ".join(args.args) if args.args else ""
        if not query:
            print("Usage: brain search <query>")
            return
        ql = query.lower()
        cache = LessonCache()
        graph = ContextGraph()
        results = []
        for l in cache.lessons:
            if ql in l["task"].lower() or ql in l["correction"].lower():
                results.append(("lesson", l["id"], l["task"], l["correction"]))
        for e in graph.entries:
            if ql in e["title"].lower() or ql in e["content"].lower():
                results.append(("context", e["id"], e["title"], e["content"][:100]))
        if args.json:
            print(json.dumps(results))
        else:
            if not results:
                print(f"No brain entries for '{query}'")
                return
            print(f"Brain results for '{query}':")
            for typ, eid, title, content in results[:10]:
                print(f"  [{typ}] {eid}: {title} — {content[:80]}")
        return


if __name__ == "__main__":
    main()
