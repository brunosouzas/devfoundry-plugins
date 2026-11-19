# WRS - Exclusions

These are the exclusions of the Customer Notifications journey, for every branch.

## Age exclusion

Parties under 18 years of age by date of birth are excluded.

## Safety flags

The flags below mark a job with a safety concern. When a job has any of them in `Job__Flags` or `Job__Flags2`, the customer is not notified by the automatic journey. Keep the list in property files: it could change.

| Code | Name |
| --- | --- |
| BRK | Brake system failure |
| STR | Steering defect |
| FUE | Fuel leak |
| EVB | EV battery fault |
| TYR | Tyre structure failure |
| RCL | Manufacturer recall |
| HAZ | Hazardous load |

## Party role

| Role | |
| --- | --- |
| OWN (owner) | **Included** |
| DRV (driver) | **Included** |
| REP (representative) | **Included** |
| LEAD (lead technician) | technician only |
| All other roles | excluded |

## Test parties

In the test environments, only parties whose last name contains `ZZTEST` are returned, so no real customer is notified by a test. This is driven by a toggle per environment: on in test, off in production.
