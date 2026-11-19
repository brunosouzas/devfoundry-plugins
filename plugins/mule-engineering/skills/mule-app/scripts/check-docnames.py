#!/usr/bin/env python3
"""Check Mule 4 flow XML for missing display names and flow descriptions.

What it does
    Reads every Mule configuration file (root element <mule>) under the paths
    given and reports, with file and line:
    - FLOW-2: a processor or scope directly inside a flow, sub-flow, try, when,
      otherwise, foreach, parallel-foreach, async, route, error-handler,
      on-error-* or until-successful that has no
      doc:name, or whose doc:name is a palette default ("Transform Message",
      "Logger", "Choice"...);
    - FLOW-4: a flow or sub-flow without doc:description.

Why it exists
    These two rules have one right answer, so a script checks them instead of
    an agent reading XML by eye (the skill's step "Verify" runs it). The rules
    themselves, with their reasons, are in ../rules.md.

How to run
    python3 check-docnames.py [PATH ...]
    PATH is a file or a folder (searched for *.xml); the default is
    src/main/mule. Python 3.9 or newer, standard library only.
    Exit code: 0 nothing found, 1 findings printed, 2 a path does not exist
    or a file could not be read or parsed (printed on stderr; the other files
    are still checked).

What can go wrong
    - A file that is not well-formed XML cannot be checked: it is reported and
      the exit code is 2. Fix the XML first (Studio would not open it either).
    - Only direct children of the scopes above are checked, as the rule says.
      Value elements (ee:message, http:headers...) are not processors and are
      skipped; the on-error-* handlers inside an error-handler are checked.
    - The palette default list is the common Studio set, not every connector's
      default; a connector default not in the list is not reported.
"""

import argparse
import sys
import xml.sax
from pathlib import Path

# The namespaces that decide what an element is. Mule core holds flows and
# scopes; doc:name and doc:description live in the documentation namespace.
CORE = "http://www.mulesoft.org/schema/mule/core"
DOC = "http://www.mulesoft.org/schema/mule/documentation"

# FLOW-2: the scopes whose direct children must be named.
CONTAINERS = {
    "flow", "sub-flow", "try", "when", "otherwise", "foreach", "parallel-foreach",
    "async", "route", "error-handler", "on-error-propagate", "on-error-continue",
    "until-successful",
}

# Children of those scopes that are structure or values, not processors.
NOT_PROCESSORS = {"error-handler", "message", "variables", "headers", "body", "attributes"}

# FLOW-2: names Anypoint Studio gives by default; a name equal to one of these
# says nothing about what the processor does.
PALETTE_DEFAULTS = {
    "Async", "Choice", "Error Handler", "First Successful", "Flow Reference",
    "For Each", "Listener", "Logger", "On Error Continue", "On Error Propagate",
    "Parallel For Each", "Raise error", "Remove Variable", "Request",
    "Round Robin", "Scatter-Gather", "Set Payload", "Set Variable",
    "Transform Message", "Try", "Until Successful",
}


class Finder(xml.sax.ContentHandler):
    """Walks one file and collects (line, rule, message) findings."""

    def __init__(self):
        super().__init__()
        self.stack = []  # (namespace, local name) of the open elements
        self.findings = []
        self.is_mule = None  # decided by the root element

    def setDocumentLocator(self, locator):
        # The locator gives the line of the element being read.
        self.locator = locator

    def startElementNS(self, name, qname, attrs):
        namespace, local = name
        line = self.locator.getLineNumber()
        # Only Mule configuration files are checked; anything else is skipped.
        if self.is_mule is None:
            self.is_mule = namespace == CORE and local == "mule"
        if self.is_mule:
            self.check(namespace, local, attrs, line)
        self.stack.append((namespace, local))

    def endElementNS(self, name, qname):
        self.stack.pop()

    def check(self, namespace, local, attrs, line):
        # FLOW-4: every flow and sub-flow says what it does.
        if namespace == CORE and local in ("flow", "sub-flow"):
            if not (attrs.get((DOC, "description")) or "").strip():
                flow = attrs.get((None, "name"), "?")
                self.findings.append((line, "FLOW-4", f"{local} '{flow}' has no doc:description"))
        # FLOW-2: a direct child of a scope is a processor and needs a real name.
        if not self.stack:
            return
        parent_ns, parent = self.stack[-1]
        if parent_ns != CORE or parent not in CONTAINERS or local in NOT_PROCESSORS:
            return
        label = local if namespace == CORE else f"{prefix_of(namespace)}:{local}"
        doc_name = (attrs.get((DOC, "name")) or "").strip()
        if not doc_name:
            self.findings.append((line, "FLOW-2", f"<{label}> has no doc:name"))
        elif doc_name in PALETTE_DEFAULTS:
            self.findings.append((line, "FLOW-2", f"<{label}> keeps the palette default name '{doc_name}'"))


def prefix_of(namespace):
    # Mule namespaces name the module right after /schema/mule/ (.../mule/http,
    # .../mule/ee/core); use it as the prefix in messages, so a finding reads
    # like the XML.
    if not namespace:
        return "?"
    return namespace.split("/schema/mule/", 1)[-1].strip("/").split("/", 1)[0]


def xml_files(paths):
    # A folder means every XML file below it, in a stable order.
    for path in paths:
        if path.is_dir():
            yield from sorted(path.rglob("*.xml"))
        else:
            yield path


def check_file(path):
    """Return the findings of one file; raises on unreadable or malformed XML."""
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, True)
    # Never fetch external entities or DTDs: the input is untrusted text.
    parser.setFeature(xml.sax.handler.feature_external_ges, False)
    finder = Finder()
    parser.setContentHandler(finder)
    # A file object, not a string: sax reads a string as a URL and would fetch it.
    with open(path, "rb") as stream:
        parser.parse(stream)
    return finder.findings


def main(argv=None):
    parser = argparse.ArgumentParser(description="Report Mule processors without doc:name (FLOW-2) and flows without doc:description (FLOW-4).")
    parser.add_argument("paths", nargs="*", type=Path, default=[Path("src/main/mule")], help="files or folders (default: src/main/mule)")
    args = parser.parse_args(argv)

    found = broken = 0
    # A path that does not exist is an error, not "nothing found".
    for path in args.paths:
        if not path.exists():
            print(f"{path}: no such file or folder", file=sys.stderr)
            broken += 1
    for path in xml_files(p for p in args.paths if p.exists()):
        # A file that cannot be read is reported, and the others still run.
        try:
            findings = check_file(path)
        except (OSError, ValueError, xml.sax.SAXException) as error:
            print(f"{path}: cannot check: {error}", file=sys.stderr)
            broken += 1
            continue
        for line, rule, message in findings:
            print(f"{path}:{line}: {rule} {message}")
        found += len(findings)

    # Exit 2 wins over 1: an unchecked file means the result is incomplete.
    if broken:
        return 2
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
