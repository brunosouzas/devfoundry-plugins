# T3b — grading (H1, profile isolation in a larger project)

The fixture is an existing project with 4 files and 6 flows, written before the profile existed. It uses legacy naming that matches neither profile: flows like `getOrderByIdFlow`, files like `orders-api.xml`, global elements in `global-config.xml`, and variables like `orderID`. The profile was then placed in `engineering/profile.yaml`, the same fixture under profile A and profile B. The request asks for a new endpoint and does not mention naming. New code must follow the profile, not the surrounding legacy code. Existing code is not graded, and renaming it is not required.

Resource = `products`, operation = `get`. Same checklist as T3 (`tooling/evals/cases/T3/grading.md`), applied to the new code only. PASS = every applicable field followed.

| Field | Profile A expects | Profile B expects |
| --- | --- | --- |
| F1 flow | new flow `products-get-flow` | new flow `ACM_PRODUCTS_GET_FL` |
| F2 implFile | in `src/main/mule/products.xml` | in `src/main/mule/impl/products-impl.xml` |
| F3 globalConfigFile | any new global element (e.g. the catalog `http:request-config`) in `src/main/mule/global.xml` | in `src/main/mule/common/acm-global-config.xml` |
| F4 variable | new flow variables camelCase, e.g. `productId` | `v_` + snake_case, e.g. `v_product_id` |

F3 is N/A when the run adds no new global element, for example when it reuses an existing config. F4 is N/A when the run creates no variable. Record whether the run noticed the conflict between the profile and the legacy code.
