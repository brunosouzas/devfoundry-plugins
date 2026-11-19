# wrs-jobs-sys - /jobs (GET)

Lists the repair jobs created in a date range.

## Input details

| Name | Location | Type | Required | Notes |
| --- | --- | --- | --- | --- |
| dateFrom | query | date-time `yyyy-MM-ddTHH:mm:ss` | Yes | start of the range, UK time |
| dateTo | query | date-time `yyyy-MM-ddTHH:mm:ss` | Yes | end of the range, UK time |
| searchType | query | enum: `DATE-RANGE-SEARCH` | Yes | |
| filter | query | enum: `CUSTOMER-NOTIFY` | No | applies the Customer Notifications filter below |

## Processing

1. Log in to WRS (or reuse the cached session).
2. `JobSearch` with the date range (converted to `dd/MM/yyyy HH:mm`).
3. When `filter=CUSTOMER-NOTIFY`, keep only the jobs that pass these rules, in this order:

   | # | Rule | Field | Keep when |
   | --- | --- | --- | --- |
   | 1 | Filter branch | `Job__Branch` | value is `NRT` |
   | 2 | Filter job type | `Job__TypeCode` | the id is in the environment's id column of the job types list (see "WRS - Job Types"; the list could change, keep it in properties) |

4. For each job left: `JobById`, then `PersonById` for each party whose role is in the included roles (see "WRS - Exclusions"). A job with no included party is left out.
5. Map each job as in "Mapping" below and answer with the array.

## Mapping (WRS to API)

| WRS field | API field | Type | Rule |
| --- | --- | --- | --- |
| `Job__Branch` | branch | string | `NRT` becomes `NORTH-REGION`; any other value as it is |
| `Job__Id` | jobId | string | |
| `Job__FileNo` | jobReference | string | |
| `Job__BookingNo` | bookingReference | string | |
| `Job__TypeCode` | jobType | string | the job type name from the job types list (the id of the environment's WRS); `null` when the id is not in the list |
| `Job__TypeCode` | jobCode | string | the job type code from the same list (`SRV`, `BRK`...); `null` when the id is not in the list |
| `Job__Flags`, `Job__Flags2` | safetyFlags | boolean | each field holds zero or more codes separated by spaces; `true` when either holds any of the safety flags in "WRS - Exclusions" (keep them in properties: they could change) |
| `Job__CreatedUTC` | jobCreatedTime | date-time | WRS gives UTC (`dd/MM/yyyy HH:mm`); convert to Europe/London, ISO 8601 with offset |
| `Job__ReportedTime` | jobReportedTime | date-time | ISO 8601 |
| `Job__Status` | status | string | |
| `Job__OutcomeCode` | outcomeCode | string | |
| `Job__Outcome` | outcome | string | |
| `Job__Closed` | closed | boolean | `Y` is true, `N` false |
| `Note__CreTime` of notes with `Note__SubType = CU_OUTBOUND` | lastCustomerUpdate | date-time | the most recent one, given in UTC like `Job__CreatedUTC` and converted the same way; when there is none, `jobCreatedTime`. The sub-type could change: keep it in properties |
| party | parties[] | array | one entry per included party |
| `Party__Role` | parties[].partyRole | string | |
| `Person__Id` | parties[].personId | string | |
| `Person__FirstName`, `Person__LastName` | parties[].firstName, lastName | string | |
| `Person__DateOfBirth` | parties[].dateOfBirth | date | `yyyy-MM-dd` |
| `Phone__Number` | parties[].telephone | string | the most recent phone; `null` when it has fewer than 10 characters |
| `Email__Address` | parties[].email | string | the most recent e-mail that is a valid address (regex) |
| `Flag__Name`, `Flag__Active` | parties[].hasPortal | boolean | `true` when the person has the flag `CUSTOMER PORTAL USER` and it is active |
| technician | technician | object | the party with role `LEAD`: `{ personId, firstName, lastName, badgeNumber }` from the party itself (no `PersonById`); `null` when the job has no `LEAD` party or that party is not a Person |
| `Person__BadgeNo` | technician.badgeNumber | string | `null` when the technician is a contractor (see "WRS - Contractors"; the list could change) |
| `Inspection__Code`, `Inspection__Mandatory` | inspections[] | array | `{ code, mandatory }`, mandatory as boolean |

## Output

`200` with an array of jobs. `jobs-example.json` is the output for the samples in the **test** environment (test job type ids, the `ZZTEST` toggle on), with `JobById.xml` and the two `PersonById` samples (`PersonById.xml` for the owner, `PersonById-DRV.xml` for the driver).
