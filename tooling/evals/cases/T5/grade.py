"""Deterministic part of the T5 rubric (tooling/evals/cases/T5/grading.md), read from the project a run left.
Usage: python3 grade.py <project dir>... Prints one JSON line per project (skill-creator grading shape).
- N1 is decided here: no idempotent-message-validator and no os:store failIfPresent="true" (dedup) in the project.
- B3 timeout half is decided here: the score call has an explicit responseTimeout below 60000 ms (attribute on the
  request or its config, resolved from config.yaml). The failure-classification half of B3 needs judgment.
- B1, B2, B4 need judgment: passed=null, with the code signals as evidence (breaker state, a branch that skips the call,
  a cool-down check, a half-open/trial state). The grader confirms from the flow and the answer."""
import glob, json, os, re, sys

def prop(project, expr):
    m = re.fullmatch(r"\$\{([^}]+)\}", expr.strip())
    if not m: return expr
    keys = m.group(1).split(".")
    for f in glob.glob(os.path.join(project, "src/main/resources/*.yaml")):
        lines, stack = open(f).read().splitlines(), []
        for ln in lines:
            if not ln.strip() or ln.strip().startswith("#"): continue
            ind = len(ln) - len(ln.lstrip()); k, _, v = ln.strip().partition(":")
            stack = [s for s in stack if s[0] < ind] + [(ind, k.strip())]
            if [s[1] for s in stack] == keys: return v.strip().strip('"\'')
    return expr

def grade(project):
    xml = {os.path.relpath(f, project): open(f).read() for f in glob.glob(os.path.join(project, "src/main/mule/**/*.xml"), recursive=True)}
    allx = "\n".join(xml.values())
    ev = lambda pat: [f"{f}: {m.group(0)[:90]}" for f, t in xml.items() for m in re.finditer(pat, t)]
    dedup = ev(r'<idempotent-message-validator[^>]*>') + ev(r'<os:store[^>]*failIfPresent="true"[^>]*>')
    state = ev(r'"(OPEN|HALF_OPEN|HALF-OPEN|CLOSED)"') + ev(r"'(OPEN|HALF_OPEN|CLOSED)'") + ev(r'<os:(store|retrieve)[^>]*>')
    skip = ev(r'<raise-error[^>]*>') + ev(r'<when expression="[^"]*(OPEN|open|state)[^"]*"')
    cooldown = ev(r'(openedAt|openUntil|opened_at|open_until|lastFailure|cooldown|coolDown|openSeconds|resetTimeout)')
    # explicit timeout on the score call: on an http:request to /scores, or on the request-config it uses
    timeouts = []
    for f, t in xml.items():
        for m in re.finditer(r'<http:request\b[^>]*>', t):
            tag = m.group(0)
            if "scores" not in tag: continue
            rt = re.search(r'responseTimeout="([^"]+)"', tag)
            cfg = re.search(r'config-ref="([^"]+)"', tag)
            if not rt and cfg:
                c = re.search(r'<http:request-config[^>]*name="%s"[^>]*>' % re.escape(cfg.group(1)), allx)
                rt = c and re.search(r'responseTimeout="([^"]+)"', c.group(0))
            if rt:
                val = prop(project, rt.group(1))
                timeouts.append((f, rt.group(1), val))
    t_ok = any(v.isdigit() and int(v) < 60000 for _, _, v in timeouts)
    exp = [
        {"text": "B1 open: fail fast (state shared across requests, call skipped)", "passed": None,
         "evidence": "signals: " + "; ".join((state[:3] + skip[:2])) if (state and skip) else "no breaker state or no branch that skips the call"},
        {"text": "B2 recovery: half-open trial after the cool-down", "passed": None,
         "evidence": "signals: " + "; ".join(cooldown[:3]) if cooldown else "no cool-down signal in code"},
        {"text": "B3a explicit response timeout below the default on the score call", "passed": t_ok,
         "evidence": "; ".join(f"{f}: responseTimeout={r} -> {v}" for f, r, v in timeouts) or "no explicit responseTimeout on the score call"},
        {"text": "B3b only unhealthy errors trip it (not 4xx)", "passed": None, "evidence": "judge from the error handlers"},
        {"text": "B4 limit stated (per worker vs shared, approximate under concurrency)", "passed": None, "evidence": "judge from the answer and comments"},
        {"text": "N1 no Idempotent Receiver", "passed": not dedup, "evidence": "; ".join(dedup) or "no dedup construct"},
    ]
    return {"run": project, "expectations": exp}

for p in sys.argv[1:]: print(json.dumps(grade(p.rstrip("/"))))
