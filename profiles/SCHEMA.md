# Engineering profile — draft schema v0

A project's conventions live in `engineering/profile.yaml`. Skills read them from there and never hold the values themselves. Not a Claude Code standard: a devFoundry convention, draft v0.

```yaml
apiVersion: engineering.poc/v0
kind: EngineeringProfile
name: <profile name>
mulesoft:
  naming:
    flow: <pattern>             # name of each flow; placeholders {resource} {RESOURCE} {operation} {OPERATION}
    implFile: <pattern>         # file that holds the flow
    globalConfigFile: <path>    # file that holds every global element (listener, request and other configs)
    variable: <case or pattern> # flow variable names: camelCase, snake_case, or a pattern such as v_{snake_case}
  precedence:
    newCode: profile            # new code follows naming, even next to legacy code; missing files are created
    legacyCode: keep            # existing code is not renamed, moved or reformatted
    divergence: report          # legacy divergences are reported to the developer, not changed
```

- `{resource}`: plural resource name from the endpoint path (`/products/{id}` → `products`); upper-case form `{RESOURCE}`.
- `{operation}`: `list` (GET collection), `get` (GET by id), `create` (POST), `update` (PUT/PATCH), `delete` (DELETE); upper-case form `{OPERATION}`.
- `precedence` values in v0: `newCode: profile`, `legacyCode: keep`, `divergence: report`. Other values are not defined yet.
