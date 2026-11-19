%dw 2.0
/**
 * ACME audit entry. Called by the template's audit-start and audit-end sub-flows.
 */
fun auditEntry(stage: String, correlationId: String, path: String): Object = {
  audit: stage,
  app: "acme-template-app",
  correlationId: correlationId,
  (path: path) if (!isEmpty(path))
}
