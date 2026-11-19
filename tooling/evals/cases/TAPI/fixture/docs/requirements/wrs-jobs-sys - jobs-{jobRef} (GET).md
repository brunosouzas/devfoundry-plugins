# wrs-jobs-sys - /jobs/{jobRef} (GET)

Reads one repair job by its reference.

## Input details

| Name | Location | Type | Required |
| --- | --- | --- | --- |
| jobRef | path | string (`Job__FileNo`) | Yes |

## Processing

1. Log in to WRS (or reuse the cached session).
2. `JobByRef` with the reference.
3. `PersonById` for each party whose role is in the included roles.
4. Map the job as in the mapping of `/jobs` (same table) and answer with the object.

A reference WRS does not know comes back as an empty `<wrs:QueryWSResult/>`; the API answers `404`.
