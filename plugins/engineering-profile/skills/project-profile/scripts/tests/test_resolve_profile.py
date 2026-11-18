"""Tests of resolve-profile.py. Run: uv run --with pyyaml python -m unittest discover -s <this folder>."""
import importlib.util, tempfile, textwrap, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("resolve_profile", HERE.parent / "resolve-profile.py")
rp = importlib.util.module_from_spec(spec); spec.loader.exec_module(rp)

PUBLIC = """\
# rules
- **CON-2** Errors use one shared error type.
- **MUNIT-3** Keep the coverage gate.
- **FLOOR-2** (floor) No secret in code.
"""


class Resolve(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "rules").mkdir()
        (self.tmp / "rules/rules.md").write_text(PUBLIC)
        self.project = self.tmp / "project"
        (self.project / "engineering").mkdir(parents=True)

    def write(self, rel, text):
        p = self.project / rel; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(text))

    def pack(self, name, body):
        self.write(f"engineering/packs/{name}/pack.yaml",
                   f"apiVersion: devfoundry/v1\nkind: RulesPack\nname: {name}\nversion: 1.0.0\nlayer: company\n" + textwrap.dedent(body))

    def run_(self):
        return rp.resolve(self.project, [self.tmp / "rules"])

    def test_v0_profile_still_reads(self):
        self.write("engineering/profile.yaml", """\
            apiVersion: engineering.poc/v0
            kind: EngineeringProfile
            name: a
            mulesoft:
              naming: {flow: "{resource}-{operation}-flow"}
            """)
        res = self.run_()
        self.assertEqual(res["errors"], [])
        self.assertEqual(res["mulesoft"]["naming"]["flow"], "{resource}-{operation}-flow")

    def test_v0_with_rules_is_an_error(self):
        self.write("engineering/profile.yaml", "apiVersion: engineering.poc/v0\nkind: EngineeringProfile\nrules: {}\n")
        self.assertTrue(any("need apiVersion devfoundry/v1" in e for e in self.run_()["errors"]))

    def test_pack_then_project_naming_precedence(self):
        self.pack("acme", "mulesoft:\n  naming: {flow: 'acme-{resource}-{operation}', variable: snake_case}\n")
        self.write("engineering/profile.yaml", """\
            apiVersion: devfoundry/v1
            kind: EngineeringProfile
            extends: [engineering/packs/acme]
            mulesoft:
              naming: {variable: camelCase}
            """)
        res = self.run_()
        self.assertEqual(res["errors"], [])
        self.assertEqual(res["mulesoft"]["naming"], {"flow": "acme-{resource}-{operation}", "variable": "camelCase"})
        self.assertEqual(res["replaced"][0]["key"], "mulesoft.naming.variable")
        self.assertEqual(res["replaced"][0]["was_layer"], "pack acme@1.0.0")

    def test_override_disable_add(self):
        self.pack("acme", """\
            rules:
              override: {MUNIT-3: {text: "Coverage at least 90%", why: "company gate"}}
              add:
                - {id: ACME-LOG-1, text: "Log entry and exit", why: "audit", check: "logger in each flow"}
            """)
        self.write("engineering/profile.yaml", """\
            apiVersion: devfoundry/v1
            kind: EngineeringProfile
            extends: [engineering/packs/acme]
            rules:
              disable: {CON-2: "legacy API keeps its own error shapes"}
            """)
        res = self.run_()
        self.assertEqual(res["errors"], [])
        self.assertEqual(res["rules"]["MUNIT-3"]["text"], "Coverage at least 90%")
        self.assertEqual(res["rules"]["MUNIT-3"]["layer"], "pack acme@1.0.0")
        self.assertEqual(res["rules"]["CON-2"]["status"], "disabled")
        self.assertIn("ACME-LOG-1", res["rules"])
        self.assertEqual([c["action"] for c in res["changes"]], ["add", "override", "disable"])

    def test_floor_rule_is_refused_not_applied(self):
        self.pack("acme", "rules:\n  disable: {FLOOR-2: 'keys in config.yaml are simpler'}\n  override: {FLOOR-2: 'anything'}\n")
        self.write("engineering/profile.yaml", "apiVersion: devfoundry/v1\nkind: EngineeringProfile\nextends: [engineering/packs/acme]\n")
        res = self.run_()
        self.assertEqual(res["errors"], [])
        self.assertEqual({r["action"] for r in res["refused"]}, {"disable", "override"})
        self.assertEqual(res["rules"]["FLOOR-2"]["status"], "active")
        self.assertEqual(res["rules"]["FLOOR-2"]["layer"], "public")
        self.assertIn("REFUSED", rp.report(res))

    def test_errors(self):
        self.pack("acme", "rules:\n  add: [{id: CON-2, text: t, why: w, check: c}, {id: bad, text: t}]\n  disable: {NOPE-1: x, MUNIT-3: ''}\n")
        self.write("engineering/profile.yaml", "apiVersion: devfoundry/v1\nkind: EngineeringProfile\nextends: [engineering/packs/acme, engineering/packs/missing]\n")
        errs = " | ".join(self.run_()["errors"])
        for needle in ("add CON-2 exists already", "add id 'bad'", "disable NOPE-1: no such rule",
                       "disable MUNIT-3 needs a reason", "packs/missing: no pack.yaml"):
            self.assertIn(needle, errs)

    def test_later_pack_reenables_a_disabled_rule(self):
        self.pack("a", "rules:\n  disable: {CON-2: 'old'}\n")
        self.pack("b", "rules:\n  override: {CON-2: 'Errors use the ACME error type'}\n")
        self.write("engineering/profile.yaml", "apiVersion: devfoundry/v1\nkind: EngineeringProfile\nextends: [engineering/packs/a, engineering/packs/b]\n")
        res = self.run_()
        self.assertEqual(res["rules"]["CON-2"]["status"], "active")
        self.assertEqual(res["rules"]["CON-2"]["layer"], "pack b@1.0.0")

    def test_cli_exit_codes(self):
        self.pack("acme", "rules:\n  disable: {FLOOR-2: 'x'}\n")
        self.write("engineering/profile.yaml", "apiVersion: devfoundry/v1\nkind: EngineeringProfile\nextends: [engineering/packs/acme]\n")
        args = [str(self.project), "--rules-root", str(self.tmp / "rules")]
        self.assertEqual(rp.main(args), 0)
        self.assertEqual(rp.main(args + ["--strict"]), 1)
        self.assertEqual(rp.main([str(self.tmp / "nowhere")]), 2)

    def test_real_public_rules_are_found(self):
        rules = rp.public_rules([rp.default_rules_root()])
        for rid in ("CON-2", "APISEC-1", "MUNIT-5", "APIKIT-2", "FLOOR-1", "FLOOR-2"):
            self.assertIn(rid, rules)
        self.assertTrue(rules["APISEC-1"]["floor"] and rules["FLOOR-2"]["floor"])
        self.assertFalse(rules["CON-2"]["floor"])


if __name__ == "__main__":
    unittest.main()
