# T8 — grading (layers: a company pack and a project override)

The fixture is the T3b project (legacy names, plain HTTP listeners). Its `engineering/profile.yaml` extends a synthetic company pack, `engineering/packs/acme-mule`, which sets the naming and adds the rule `ACME-LOG-1`. The project profile overrides one key: `variable: camelCase` over the pack's `snake_case`. The prompt is T3b's and names no rule.

Effective naming (`resolve-profile.py --emit-profile`): flow `acme-products-get-flow`, file `src/main/mule/acme/products.xml`, globals in `src/main/mule/acme/acme-global.xml`, variables camelCase.

| ID | Pass when | How |
| --- | --- | --- |
| L0 | `engineering/` (profile and pack) is unchanged, so the effective naming is the fixture's | `grade.py` |
| L1 | F1-F4 of the effective naming pass on the new code | `grade.py` runs `T3/check.py` with the effective profile |
| L2 | The new endpoint flow, with the flows it reaches by `flow-ref`, has at least two `logger` elements with category exactly `com.acme.api.products` (ACME-LOG-1); entry and exit positions are confirmed by reading | `grade.py` |
| L3 | The answer reports the layers: it names `ACME-LOG-1` and says the variable rule came from the project over the pack | `grade.py` checks `ACME-LOG-1` and `camelCase` in the answer; read the answer to confirm |

PASS = L0, L1, L2 and L3.
