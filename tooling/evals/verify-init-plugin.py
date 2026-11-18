"""Plugin-arm isolation and skill-firing evidence from a stream-json run.
Usage: python3 verify-init-plugin.py <plugin name>[,<plugin name>...] <skill id>[,<skill id>...] <run.jsonl>...
clean=True only when the init event lists exactly the given skills, exactly the given non-builtin
plugins, no MCP servers and no CLAUDE.md in memory_paths (only 'auto'). Lists are comma-separated.
fired = the Skill tool_use calls made in the run (skill names)."""
import json, sys
names, skills = sorted(sys.argv[1].split(",")), sorted(sys.argv[2].split(","))
for path in sys.argv[3:]:
    init = res = None; fired = []
    for line in open(path):
        try: o = json.loads(line)
        except ValueError: continue
        if o.get("type") == "system" and o.get("subtype") == "init" and init is None: init = o
        if o.get("type") == "result": res = o
        if o.get("type") == "assistant":
            for c in o.get("message", {}).get("content", []):
                if c.get("type") == "tool_use" and c.get("name") == "Skill":
                    fired.append((c.get("input") or {}).get("skill"))
    if not init:
        print(path, "NO INIT EVENT"); continue
    user_plugins = [p.get("name") for p in init.get("plugins", []) if p.get("path") != "builtin"]
    clean = sorted(init.get("skills") or []) == skills and sorted(user_plugins) == names and not init.get("mcp_servers") \
        and set((init.get("memory_paths") or {}).keys()) <= {"auto"}
    print(f"{path.split('/')[-1]}: clean={clean} model={init.get('model')} version={init.get('claude_code_version')} "
          f"skills={init.get('skills')} mcp={len(init.get('mcp_servers') or [])} user_plugins={user_plugins} "
          f"memory={list((init.get('memory_paths') or {}).keys())} fired={fired} "
          f"is_error={res and res.get('is_error')} turns={res and res.get('num_turns')} cost={res and res.get('total_cost_usd')}")
