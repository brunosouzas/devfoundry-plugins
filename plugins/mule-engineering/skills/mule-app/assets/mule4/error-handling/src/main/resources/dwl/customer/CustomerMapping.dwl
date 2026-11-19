%dw 2.0
import fail from dw::Runtime

// The backend's customer row mapped to the API's Customer. Pure functions (DW-5), typed (DW-6).

type Customer = {
  customerId: String,
  name: String,
  status: String,
  since: String
}

// Every backend code is mapped; an unknown one fails with a message that names it (DW-7).
fun toStatus(code: String): String = code match {
  case "A" -> "ACTIVE"
  case "S" -> "SUSPENDED"
  else -> fail("Unknown customer status: $(code)")
}

// The backend sends dates as yyyyMMdd; the API answers ISO dates. Both formats are explicit (DW-8).
fun toCustomer(row: Object): Customer = {
  customerId: row.id as String,
  name: (row.name default "") as String,
  status: toStatus((row.statusCode default "") as String),
  since: (row.createdAt as String) as Date {format: "yyyyMMdd"} as String {format: "yyyy-MM-dd"}
}
