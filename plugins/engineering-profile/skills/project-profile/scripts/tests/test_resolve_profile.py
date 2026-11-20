"""Tests of resolve-profile.py. Run: uv run --with pyyaml python -m unittest discover -s <this folder>."""
import importlib.util, json, tempfile, textwrap, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("resolve_profile", HERE.parent / "resolve-profile.py")
rp = importlib.util.module_from_spec(spec); spec.loader.exec_module(rp)

PUBLIC = """\
# rules
- **CON-2** Errors use one shared error type.
  Check: one type.
  Class: auto
- **MUNIT-3** Keep the coverage gate.
- **CON-4** A breaking change is a new major version.
  Class: ask
- **FLOOR-2** (floor) No secret in code.
  Class: auto
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
                   f"apiVersion: mulesmith/v1\nkind: RulesPack\nname: {name}\nversion: 1.0.0\nlayer: company\n" + textwrap.dedent(body))

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
        self.assertTrue(any("need apiVersion mulesmith/v1" in e for e in self.run_()["errors"]))

    def test_pack_then_project_naming_precedence(self):
        self.pack("acme", "mulesoft:\n  naming: {flow: 'acme-{resource}-{operation}', variable: snake_case}\n")
        self.write("engineering/profile.yaml", """\
            apiVersion: mulesmith/v1
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
            apiVersion: mulesmith/v1
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
        self.pack("acme", "rules:\n  disable: {FLOOR-2: 'keys in config.yaml are simpler'}\n")
        self.pack("team", "rules:\n  override: {FLOOR-2: 'anything'}\n")
        self.write("engineering/profile.yaml", "apiVersion: mulesmith/v1\nkind: EngineeringProfile\nextends: [engineering/packs/acme, engineering/packs/team]\n")
        res = self.run_()
        self.assertEqual(res["errors"], [])
        self.assertEqual({r["action"] for r in res["refused"]}, {"disable", "override"})
        self.assertEqual(res["rules"]["FLOOR-2"]["status"], "active")
        self.assertEqual(res["rules"]["FLOOR-2"]["layer"], "public")
        self.assertIn("REFUSED", rp.report(res))

    def test_errors(self):
        self.pack("acme", "rules:\n  add: [{id: CON-2, text: t, why: w, check: c}, {id: bad, text: t}]\n  disable: {NOPE-1: x, MUNIT-3: ''}\n")
        self.write("engineering/profile.yaml", "apiVersion: mulesmith/v1\nkind: EngineeringProfile\nextends: [engineering/packs/acme, engineering/packs/missing]\n")
        errs = " | ".join(self.run_()["errors"])
        for needle in ("add CON-2 exists already", "add id 'bad'", "disable NOPE-1: no such rule",
                       "disable MUNIT-3 needs a reason", "packs/missing: no pack.yaml"):
            self.assertIn(needle, errs)

    def test_later_pack_reenables_a_disabled_rule(self):
        self.pack("a", "rules:\n  disable: {CON-2: 'old'}\n")
        self.pack("b", "rules:\n  override: {CON-2: 'Errors use the ACME error type'}\n")
        self.write("engineering/profile.yaml", "apiVersion: mulesmith/v1\nkind: EngineeringProfile\nextends: [engineering/packs/a, engineering/packs/b]\n")
        res = self.run_()
        self.assertEqual(res["rules"]["CON-2"]["status"], "active")
        self.assertEqual(res["rules"]["CON-2"]["layer"], "pack b@1.0.0")

    def test_cli_exit_codes(self):
        self.pack("acme", "rules:\n  disable: {FLOOR-2: 'x'}\n")
        self.write("engineering/profile.yaml", "apiVersion: mulesmith/v1\nkind: EngineeringProfile\nextends: [engineering/packs/acme]\n")
        args = [str(self.project), "--rules-root", str(self.tmp / "rules")]
        self.assertEqual(rp.main(args), 0)
        self.assertEqual(rp.main(args + ["--strict"]), 1)
        self.assertEqual(rp.main([str(self.tmp / "nowhere")]), 2)

    def test_malformed_sections_are_errors_not_crashes(self):
        self.pack("acme", "rules:\n  disable: [CON-2]\n  add: {id: X-1}\nmulesoft: x\n")
        self.write("engineering/profile.yaml", "apiVersion: mulesmith/v1\nkind: EngineeringProfile\nextends: engineering/packs/acme\n")
        errs = " | ".join(self.run_()["errors"])
        self.assertIn("extends must be a list", errs)
        self.write("engineering/profile.yaml", "apiVersion: mulesmith/v1\nkind: EngineeringProfile\nextends: [engineering/packs/acme]\nrules:\n  override: {CON-2: [a]}\n")
        errs = " | ".join(self.run_()["errors"])
        for needle in ("rules.disable must be a mapping", "rules.add must be a list", "mulesoft must be a mapping",
                       "override CON-2 needs the rule's text"):
            self.assertIn(needle, errs)

    def test_one_change_per_rule_per_layer(self):
        self.write("engineering/profile.yaml", "apiVersion: mulesmith/v1\nkind: EngineeringProfile\nrules:\n  override: {CON-2: x}\n  disable: {CON-2: y}\n")
        self.assertIn("CON-2 appears in override and disable", " | ".join(self.run_()["errors"]))

    def test_pack_rules_on_paths_kind_and_duplicates(self):
        self.pack("acme", "rules:\n  add: [{id: CON-99, text: t, why: w, check: c}]\n")
        self.write("engineering/packs/wrong/pack.yaml", "apiVersion: mulesmith/v1\nkind: EngineeringProfile\nrules:\n  disable: {CON-2: evil}\n")
        (self.tmp / "outside").mkdir()
        self.write("engineering/profile.yaml", "apiVersion: mulesmith/v1\nkind: EngineeringProfile\n"
                   "extends: [engineering/packs/acme, engineering/packs/acme, engineering/packs/wrong, ../outside]\n")
        res = self.run_()
        errs = " | ".join(res["errors"])
        for needle in ("uses the public prefix CON", "listed twice", "kind must be RulesPack", "must be inside the project"):
            self.assertIn(needle, errs)
        self.assertEqual(res["rules"]["CON-2"]["status"], "active")  # the wrong-kind pack is not applied

    def test_emit_profile_prints_nothing_on_errors(self):
        import io, contextlib
        self.write("engineering/profile.yaml", "apiVersion: mulesmith/v1\nkind: EngineeringProfile\nrules:\n  disable: {NOPE-1: x}\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = rp.main([str(self.project), "--rules-root", str(self.tmp / "rules"), "--emit-profile"])
        self.assertEqual((code, out.getvalue()), (1, ""))

    def test_installed_layout_finds_sibling_plugins(self):
        cache = self.tmp / "cache/mulesmith"
        for plugin, versions in (("engineering-profile", ("old", "new")), ("api-contracts", ("v1",))):
            for v in versions:
                d = cache / plugin / v
                (d / ".claude-plugin").mkdir(parents=True); (d / ".claude-plugin/plugin.json").write_text(json.dumps({"name": plugin}))
                (d / "skills/s").mkdir(parents=True)
                (d / "skills/s/rules.md").write_text(f"- **{plugin.upper().split('-')[0]}-1** {v}\n")
        import os, time
        os.utime(cache / "engineering-profile/old", (time.time() - 100, time.time() - 100))
        script = cache / "engineering-profile/new/skills/project-profile/scripts/resolve-profile.py"
        roots = rp.default_rules_roots(script)
        self.assertEqual(sorted(r.name for r in roots), ["new", "v1"])
        rules = rp.public_rules(roots)
        self.assertEqual(rules["ENGINEERING-1"]["text"], "new")
        self.assertIn("API-1", rules)

    def test_real_public_rules_are_found(self):
        rules = rp.public_rules(rp.default_rules_roots())
        for rid in ("CON-2", "APISEC-1", "MUNIT-5", "APIKIT-2", "FLOOR-1", "FLOOR-2"):
            self.assertIn(rid, rules)
        self.assertTrue(rules["APISEC-1"]["floor"] and rules["FLOOR-2"]["floor"])
        self.assertFalse(rules["CON-2"]["floor"])


    def test_classes_are_read_and_default_to_auto(self):
        self.write("engineering/profile.yaml", "apiVersion: mulesmith/v1\nkind: EngineeringProfile\n")
        rules = self.run_()["rules"]
        self.assertEqual((rules["CON-2"]["class"], rules["CON-4"]["class"], rules["MUNIT-3"]["class"]), ("auto", "ask", "auto"))

    def test_override_class_only_keeps_text_and_is_reported(self):
        self.pack("acme", "rules:\n  override: {CON-2: {class: propose}}\n")
        self.write("engineering/profile.yaml", """\
            apiVersion: mulesmith/v1
            kind: EngineeringProfile
            extends: [engineering/packs/acme]
            rules:
              override: {CON-4: {class: auto, text: "Breaking changes go to v2"}}
              add: [{id: ACME-LOG-1, text: t, why: w, check: c, class: ask}]
            """)
        res = self.run_()
        self.assertEqual(res["errors"], [])
        self.assertEqual(res["rules"]["CON-2"]["text"], "Errors use one shared error type.")
        self.assertEqual((res["rules"]["CON-2"]["class"], res["rules"]["CON-4"]["class"]), ("propose", "auto"))
        self.assertEqual(res["rules"]["ACME-LOG-1"]["class"], "ask")
        report = rp.report(res)
        self.assertIn("CON-2 override by pack acme@1.0.0 (was public), class auto -> propose", report)
        self.assertIn("Rules of class ask: ACME-LOG-1", report)
        self.assertIn("Rules of class propose: CON-2", report)

    def test_bad_class_is_an_error_and_floor_class_is_refused(self):
        self.write("engineering/profile.yaml", "apiVersion: mulesmith/v1\nkind: EngineeringProfile\nrules:\n"
                   "  override: {CON-2: {class: maybe}, FLOOR-2: {class: ask}, MUNIT-3: {why: x}}\n"
                   "  add: [{id: ACME-1, text: t, why: w, check: c, class: later}]\n")
        res = self.run_()
        errs = " | ".join(res["errors"])
        for needle in ("override CON-2: class must be one of auto, propose, ask", "add ACME-1: class must be one of",
                       "override MUNIT-3 needs the rule's text or class"):
            self.assertIn(needle, errs)
        self.assertEqual(res["refused"], [{"id": "FLOOR-2", "action": "override", "layer": "project"}])
        self.assertEqual(res["rules"]["FLOOR-2"]["class"], "auto")

    def test_every_real_public_rule_declares_one_class(self):
        errors = []
        rules = rp.public_rules(rp.default_rules_roots(), errors)
        self.assertEqual(errors, [])
        self.assertEqual([rid for rid, r in rules.items() if not r["class_declared"]], [])
        self.assertEqual((rules["CON-5"]["class"], rules["AFI-5"]["class"], rules["AFI-6"]["class"]), ("ask", "ask", "propose"))

    def test_class_line_is_scoped_to_its_rule_and_checked(self):
        (self.tmp / "rules/x").mkdir()
        (self.tmp / "rules/x/rules.md").write_text(
            "- **ZZ-1** No class here.\n  Why: w\n\n## Notes\n\n- a note\n  Class: ask\n"
            "- **ZZ-2** Wrong case.\n  Class: Ask\n- **ZZ-3** Twice.\n  Class: ask\n  Class: auto\n")
        errors = []
        rules = rp.public_rules([self.tmp / "rules"], errors)
        self.assertEqual((rules["ZZ-1"]["class"], rules["ZZ-1"]["class_declared"]), ("auto", False))
        self.assertEqual(rules["ZZ-3"]["class"], "ask")
        joined = " | ".join(errors)
        self.assertIn("ZZ-2: Class must be one of auto, propose, ask, got 'Ask'", joined)
        self.assertIn("ZZ-3: more than one Class line", joined)

    def test_override_noop_null_class_and_reenable(self):
        self.pack("a", "rules:\n  disable: {CON-2: 'old'}\n")
        self.write("engineering/profile.yaml", "apiVersion: mulesmith/v1\nkind: EngineeringProfile\nextends: [engineering/packs/a]\nrules:\n"
                   "  override: {CON-2: {class: propose}, CON-4: {class: ask}}\n"
                   "  add: [{id: ACME-1, text: t, why: w, check: c, class: null}]\n")
        res = self.run_()
        self.assertEqual(res["errors"], [])
        ids = [(c["id"], c["action"]) for c in res["changes"]]
        self.assertNotIn(("CON-4", "override"), ids)  # same class, same text: not a change
        self.assertEqual(res["rules"]["ACME-1"]["class"], "auto")
        self.assertIn("CON-2 override by project (was pack a@1.0.0), class auto -> propose, enabled again", rp.report(res))

if __name__ == "__main__":
    unittest.main()
