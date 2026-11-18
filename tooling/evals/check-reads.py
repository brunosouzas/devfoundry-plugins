"""Which skill files did a run read? Usage: python3 check-reads.py <run.jsonl>...
For each run: successful and denied tool calls that touch each pattern reference and example project (Idempotent Receiver, Circuit Breaker),
and whether ${CLAUDE_SKILL_DIR} reached the model unexpanded (in a tool input)."""
import json, re, sys
TARGETS = {  # regexes over the tool input
    "ir-reference": r"references/idempotent-receiver\.md", "ir-mule4": r"references/mule4/idempotent-receiver\.md",
    "ir-example": r"assets/mule4/idempotent-receiver",
    "cb-reference": r"references/circuit-breaker\.md", "cb-mule4": r"references/mule4/circuit-breaker\.md",
    "cb-example": r"assets/mule4/circuit-breaker"}
for path in sys.argv[1:]:
    calls, res, literal = {}, {k: [0, 0] for k in TARGETS}, False
    for line in open(path):
        try: o = json.loads(line)
        except ValueError: continue
        if o.get("type") == "assistant":
            for c in o["message"]["content"]:
                if c.get("type") == "tool_use":
                    s = json.dumps(c.get("input"))
                    literal |= "${CLAUDE_SKILL_DIR}" in s
                    hit = [k for k, t in TARGETS.items() if re.search(r"(?<!mule4/)" + t if k.endswith("reference") else t, s)]
                    if hit: calls[c["id"]] = hit
        if o.get("type") == "user" and isinstance(o["message"].get("content"), list):
            for c in o["message"]["content"]:
                if c.get("type") == "tool_result" and c.get("tool_use_id") in calls:
                    for k in calls[c["tool_use_id"]]: res[k][1 if c.get("is_error") else 0] += 1
    print(f"{path.split('/')[-1]}: " + " ".join(f"{k} ok={v[0]} denied={v[1]}" for k, v in res.items()) + f" literal_CLAUDE_SKILL_DIR={literal}")
