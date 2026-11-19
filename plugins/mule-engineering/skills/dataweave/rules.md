# DataWeave: rules

Rules for DataWeave 2, ported from the `dataweave` skill of brunosouzas/agent-skills, from MuleSoft's DataWeave documentation and common practice; the IDs are kept. In an existing project, follow the conventions it already uses and report a difference instead of renaming; these rules decide new scripts and files.

Not here on purpose: the names of `.dwl` files beyond what DW-1 asks come from the project's conventions or a private pack (DW-3 of the `dataweave` skill is not ported); synthetic test inputs are FLOOR-1 of `project-profile` (DWTEST-2 of the `dataweave` skill).

Changed on purpose from the source: DW-1 says a module's file name must be a valid identifier; DW-4 says what a module's header is; DW-9 gives correct ways to index; DWTEST-1 adds an unknown value to the edge cases.

How to change this file: add a rule with the next number in its group; edit a rule in place and keep its ID; retire a rule by keeping its ID with `(retired in <version>: <reason>)`, never reusing the number.

## Scripts (DW)

- **DW-1** Move transformations longer than a few lines into `.dwl` files under `src/main/resources/dwl/`, in one folder per domain (`dwl/customer/`, `dwl/error/`, `dwl/common/`), and reuse functions through modules. A module's file name is a valid identifier, because it is imported by its path (`import * from dwl::customer::CustomerMapping`).
  Why: inline scripts cannot be tested or reused, and one flat folder of dozens of scripts hides what belongs together.
  Check: new long transforms reference a `.dwl` resource in a domain folder.

- **DW-2** Declare the output MIME type and handle null and missing fields explicitly (`default`, `?`).
  Why: a null in the input becomes a runtime error or a silent wrong value.
  Check: optional fields use `default` or a null-safe selector.

- **DW-4** Every script starts with `%dw 2.0` and an `output` directive (a module has `%dw 2.0` and no `output`, because it has no body); a script that does not read the Mule message (a module function's test input, a standalone script) also declares its `input` with its MIME type.
  Why: the default output and the guessed input type change with the runtime and the caller; the header makes the script say what it reads and writes.
  Check: each new script has the header, each new module `%dw 2.0`; standalone scripts declare `input`.

- **DW-5** Functions are pure: their result depends only on their parameters. Read `vars`, `attributes` and `p(...)` in the top-level script and pass the values in.
  Why: a function that reads the message can only be tested inside a flow and changes meaning when the flow changes.
  Check: no `vars.`, `attributes.` or `p(` inside a `fun` body of a module.

- **DW-6** A module's public functions declare their parameter and return types (`fun toCustomer(row: Object): Customer`), with the types defined in the module or imported.
  Why: a typed signature fails at compile time where an untyped one fails on the first odd input in production.
  Check: every `fun` a module exports has typed parameters and a return type.

- **DW-7** Branch on the shape or value of data with `match` and patterns, and give every `match` an `else` that either maps the unexpected case or fails with a message naming it (`fail("Unknown status: $(s)")`).
  Why: nested `if` chains hide a missing case, and a `match` with no `else` throws a generic error at runtime.
  Check: each `match` has an `else` case.

- **DW-8** Parse and format dates, times and numbers with an explicit `format` (and a time zone for date-times); never rely on the default format or the runtime's zone. Money is never built by string concatenation.
  Why: defaults differ between runtimes, locales and servers; a date that moves a day or an amount that loses a digit is a silent defect.
  Check: every `as Date`, `as DateTime`, `as String` of a number or date, and every `as Number` from a string has `{format: ...}`.

- **DW-9** Index or join large collections once (an object built once with `groupBy` or `{(items map {($.id): $})}`, or `dw::core::Arrays::join`, then look up by key) instead of searching inside a `map`.
  Why: `filter` or `firstWith` inside `map` makes the transform quadratic, which is invisible in tests and slow in production.
  Check: no `filter`, `find` or `firstWith` over the same collection inside a `map` body.

## Tests (DWTEST)

- **DWTEST-1** Each function of a module and each transform has a test with its edge cases: in a Mule application an MUnit test with the input in a file (`src/test/resources/`), in a DataWeave library the DataWeave testing framework run by its Maven plugin.
  Why: DataWeave fails on the shape of data, and a happy-path test does not exercise the shape.
  Check: tests cover at least one missing field, one empty collection and one wrong type or unknown value for each changed function.
