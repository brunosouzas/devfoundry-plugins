# T3 — grading (H1, profile isolation)

Run the same prompt twice: fixture + `profiles/profile-a.yaml` copied to `engineering/profile.yaml`, and fixture + `profiles/profile-b.yaml`. The prompt never mentions the profile. Resource = `customers`, operation = `get`.

PASS = every applicable field of the active profile followed. Checked on the final files (manual in Stage 0; the validator script is Stage 1).

| Field | Profile A expects | Profile B expects |
| --- | --- | --- |
| F1 flow | flow named `customers-get-flow` | flow named `ACM_CUSTOMERS_GET_FL` |
| F2 implFile | flow lives in `src/main/mule/customers.xml` | flow lives in `src/main/mule/impl/customers-impl.xml` |
| F3 globalConfigFile | HTTP listener config (and any other global element) in `src/main/mule/global.xml` | in `src/main/mule/common/acm-global-config.xml` |
| F4 variable | the id variable is camelCase, e.g. `customerId` (any flow variable created must be camelCase) | `v_` + snake_case, e.g. `v_customer_id` |

If the run creates no flow variable at all, F4 is N/A (recorded as N/A, not as pass).
