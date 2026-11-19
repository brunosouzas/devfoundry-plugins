%dw 2.0
/**
 * ACME error catalogue: error type to HTTP status, code and message. An API adds its own error types here.
 */
var errors = {
  "APIKIT:BAD_REQUEST": { status: 400, code: "BAD_REQUEST", message: "The request is not valid" },
  "APIKIT:NOT_FOUND": { status: 404, code: "NOT_FOUND", message: "Resource not found" },
  "APIKIT:METHOD_NOT_ALLOWED": { status: 405, code: "METHOD_NOT_ALLOWED", message: "Method not allowed" },
  "APIKIT:NOT_ACCEPTABLE": { status: 406, code: "NOT_ACCEPTABLE", message: "Not acceptable" },
  "APIKIT:UNSUPPORTED_MEDIA_TYPE": { status: 415, code: "UNSUPPORTED_MEDIA_TYPE", message: "Unsupported media type" }
}

fun errorFor(errorType: String): Object =
  errors[errorType] default { status: 500, code: "INTERNAL_ERROR", message: "Unexpected error" }
