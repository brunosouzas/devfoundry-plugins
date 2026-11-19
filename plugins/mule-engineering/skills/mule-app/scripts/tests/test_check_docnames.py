"""Tests of check-docnames.py: each rule it checks, the exemptions, and the exit codes.

Run: python3 -m unittest discover -s plugins/mule-engineering/skills/mule-app/scripts/tests
"""

import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "check-docnames.py"
spec = importlib.util.spec_from_file_location("check_docnames", SCRIPT)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)

HEAD = ('<mule xmlns="http://www.mulesoft.org/schema/mule/core" '
        'xmlns:doc="http://www.mulesoft.org/schema/mule/documentation" '
        'xmlns:ee="http://www.mulesoft.org/schema/mule/ee/core" '
        'xmlns:http="http://www.mulesoft.org/schema/mule/http">')


def run(xml):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "flows.xml"
        path.write_text(HEAD + xml + "</mule>")
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = check.main([str(path)])
        return code, out.getvalue()


class CheckDocnames(unittest.TestCase):
    def test_named_and_described_flow_passes(self):
        code, out = run('<flow name="get-customer" doc:description="Reads one customer.">'
                        '<logger doc:name="Log request received" message="x"/>'
                        '<ee:transform doc:name="Build customer response"><ee:message/></ee:transform></flow>')
        self.assertEqual((code, out), (0, ""))

    def test_missing_doc_name_is_flow_2(self):
        code, out = run('<flow name="f" doc:description="d"><logger message="x"/></flow>')
        self.assertEqual(code, 1)
        self.assertIn("FLOW-2 <logger> has no doc:name", out)

    def test_palette_default_is_flow_2(self):
        code, out = run('<flow name="f" doc:description="d"><ee:transform doc:name="Transform Message"/></flow>')
        self.assertEqual(code, 1)
        self.assertIn("palette default name 'Transform Message'", out)

    def test_missing_description_is_flow_4(self):
        code, out = run('<sub-flow name="s"><logger doc:name="Log step" message="x"/></sub-flow>')
        self.assertEqual(code, 1)
        self.assertIn("FLOW-4 sub-flow 's' has no doc:description", out)

    def test_value_elements_are_not_processors(self):
        code, out = run('<flow name="f" doc:description="d"><http:request doc:name="Get customer from backend">'
                        '<http:headers>#[{}]</http:headers></http:request></flow>')
        self.assertEqual((code, out), (0, ""))

    def test_missing_path_exits_2(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(check.main(["/no/such/folder"]), 2)


if __name__ == "__main__":
    unittest.main()
