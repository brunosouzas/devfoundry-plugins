"""Print the isolation evidence from a stream-json run: skills, slash commands, MCP, non-builtin plugins, memory, model, result."""
import json, sys
for path in sys.argv[1:]:
    init = res = None
    for line in open(path):
        try: o = json.loads(line)
        except ValueError: continue
        if o.get("type") == "system" and o.get("subtype") == "init" and init is None: init = o
        if o.get("type") == "result": res = o
    if not init:
        print(path, "NO INIT EVENT"); continue
    user_plugins = [p.get("name") for p in init.get("plugins", []) if p.get("path") != "builtin"]
    clean = not init.get("skills") and not init.get("slash_commands") and not init.get("mcp_servers") and not user_plugins \
        and set((init.get("memory_paths") or {}).keys()) <= {"auto"}
    print(f"{path.split('/')[-1]}: clean={clean} model={init.get('model')} version={init.get('claude_code_version')} "
          f"skills={len(init.get('skills') or [])} slash={len(init.get('slash_commands') or [])} mcp={len(init.get('mcp_servers') or [])} "
          f"user_plugins={user_plugins} memory={list((init.get('memory_paths') or {}).keys())} "
          f"is_error={res and res.get('is_error')} turns={res and res.get('num_turns')} cost={res and res.get('total_cost_usd')}")
