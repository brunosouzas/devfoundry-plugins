# wrs-jobs-sys

System API over the Workshop Records System (WRS), the system of record of ACME Fleet Services' repair workshops. It reads repair jobs and the people linked to them, and presents them in JSON.

- Technical name: `wrs-jobs-sys`, version 1.0.0, layer: system.
- Consumers: the Customer Notifications process (a scheduled process that tells customers about their repairs) and the workshop dashboards.
- Resources in this release: `GET /jobs` and `GET /jobs/{jobRef}`. Others (`/vehicles`, `/parts`) come later.

## WRS access

WRS is a SOAP 1.2 service. Every call needs a session.

### Login

`LoginWS` with the API's username and password (secure properties) returns a `SessionId`. **A session is valid for 20 minutes.** The API keeps the session in a cache for 16 minutes and reuses it for every call, instead of logging in for each request.

Request:

```xml
<soap12:Envelope xmlns:soap12="http://www.w3.org/2003/05/soap-envelope" xmlns:wrs="http://example.test/wrs">
  <soap12:Body>
    <wrs:LoginWS>
      <wrs:userName>...</wrs:userName>
      <wrs:password>...</wrs:password>
    </wrs:LoginWS>
  </soap12:Body>
</soap12:Envelope>
```

Response: `<wrs:LoginWSResponse><wrs:LoginWSResult><SessionId>...</SessionId></wrs:LoginWSResult></wrs:LoginWSResponse>`.

### Queries

`QueryWS` runs a query. The query is a `<Find>` XML document **encoded as text** (escaped) inside the `<wrs:query>` element, sent with the session id:

```xml
<soap12:Envelope xmlns:soap12="http://www.w3.org/2003/05/soap-envelope" xmlns:wrs="http://example.test/wrs">
  <soap12:Body>
    <wrs:QueryWS>
      <wrs:sessionId>...</wrs:sessionId>
      <wrs:query>&lt;Find type="JobById"&gt;&lt;JobId&gt;7000000000000000000101&lt;/JobId&gt;&lt;/Find&gt;</wrs:query>
    </wrs:QueryWS>
  </soap12:Body>
</soap12:Envelope>
```

| Query (`Find type`) | Parameters | Returns |
| --- | --- | --- |
| `JobSearch` | `DateFrom`, `DateTo` (format `dd/MM/yyyy HH:mm`, UK time), `SearchType` | the ids of the jobs created in the range, with `Job__Branch` and `Job__TypeCode` |
| `JobById` | `JobId` | one job with its parties, notes and inspections (sample `JobById.xml`) |
| `JobByRef` | `JobRef` (`Job__FileNo`) | the same shape (sample `JobByRef.xml`) |
| `PersonById` | `PersonId` | one person with phones, e-mails and flags (sample `PersonById.xml`) |

The response wraps the result in `<wrs:QueryWSResponse><wrs:QueryWSResult>...</wrs:QueryWSResult></wrs:QueryWSResponse>`. A WRS error comes back as a SOAP fault. There is no sample of a `JobSearch` result nor a full login response envelope: their shapes are the ones above, and tests build their own.
