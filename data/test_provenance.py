"""Provenance contract tests; temporary text fixtures are not CFD results."""
import copy
from pathlib import Path
import tempfile
import unittest

from process_forces import sha256, verify_conversion


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="force_provenance_test_")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.native = self.root / "native.txt"
        self.native.write_text("provenance test fixture only", encoding="utf-8")
        self.derived = self.root / "derived.txt"
        self.derived.write_bytes(self.native.read_bytes())
        self.evidence = {"native_force_source": {"path": str(self.native), "sha256": sha256(self.native)}}
        self.meta = {"conversion": {"mode": "identity", "column_mapping": {
            key: {"source": key, "expression": key, "source_units": unit, "target_units": unit}
            for key, unit in [("iteration", "iteration"), ("Fx_N", "N"), ("Fy_N", "N"), ("Fz_N", "N")]
        }}}

    def test_identity_requires_exact_native_bytes(self):
        verify_conversion(self.meta, self.evidence, self.derived)
        self.derived.write_text("different fixture", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "byte-identical"):
            verify_conversion(self.meta, self.evidence, self.derived)

    def test_native_source_mandatory(self):
        with self.assertRaisesRegex(ValueError, "native_force_source"):
            verify_conversion(self.meta, {}, self.derived)

    def test_mode_mandatory(self):
        with self.assertRaisesRegex(ValueError, "conversion.mode"):
            verify_conversion({}, self.evidence, self.derived)

    def test_all_column_mappings_mandatory(self):
        for key in ["iteration", "Fx_N", "Fy_N", "Fz_N"]:
            meta = copy.deepcopy(self.meta)
            del meta["conversion"]["column_mapping"][key]
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "column_mapping"):
                verify_conversion(meta, self.evidence, self.derived)

    def test_sign_and_unit_mapping_mandatory(self):
        for field in ["source", "expression", "source_units", "target_units"]:
            meta = copy.deepcopy(self.meta)
            del meta["conversion"]["column_mapping"]["Fx_N"][field]
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "mapping"):
                verify_conversion(meta, self.evidence, self.derived)

    def test_script_required_for_transformation(self):
        self.meta["conversion"]["mode"] = "script"
        with self.assertRaisesRegex(ValueError, "conversion_script"):
            verify_conversion(self.meta, self.evidence, self.derived)
        script = self.root / "conversion.py"
        script.write_text("# provenance test fixture", encoding="utf-8")
        self.evidence["conversion_script"] = {"path": str(script), "sha256": sha256(script)}
        verify_conversion(self.meta, self.evidence, self.derived)
        with self.assertRaisesRegex(ValueError, "preserve the native"):
            verify_conversion(self.meta, self.evidence, self.native)


if __name__ == "__main__":
    unittest.main()
