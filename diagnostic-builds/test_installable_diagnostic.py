"""Verify package scope and Anki 26.08.1's actual installer in a temp fixture."""
import ast
import __future__
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
OLD = ROOT / "2.05-macos-diagnostic.1/speed_streak_2_05_macos_diagnostic_1.ankiaddon"
NEW = ROOT / "2.05-macos-diagnostic.2/speed_streak_2_05_macos_diagnostic_2.ankiaddon"
ANKI_SOURCE = "https://raw.githubusercontent.com/ankitects/anki/26.08.1/qt/aqt/addons.py"


class PackageTests(unittest.TestCase):
    def test_only_installation_manifest_and_build_label_changed(self):
        with zipfile.ZipFile(OLD) as old, zipfile.ZipFile(NEW) as new:
            self.assertIsNone(new.testzip())
            self.assertEqual(set(old.namelist()), set(new.namelist()))
            changed = {name for name in old.namelist() if old.read(name) != new.read(name)}
            self.assertEqual(changed, {"manifest.json", "build_info.py"})
            manifest = json.loads(new.read("manifest.json"))
            self.assertEqual(manifest["package"], "1237336370")
            self.assertIn("speed_streak_v2_05", manifest["conflicts"])
            self.assertNotIn(manifest["package"], manifest["conflicts"])
            self.assertIn(b"2.05-macos-diagnostic.2", new.read("build_info.py"))
        provenance = json.loads(NEW.with_suffix(".provenance.json").read_text())
        self.assertEqual(hashlib.sha256(NEW.read_bytes()).hexdigest(), provenance["package_sha256"])


class ActualAnkiInstallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Execute only the vendor's install/metadata functions against temporary
        # files. Never import Anki or interact with a real profile/application.
        with urllib.request.urlopen(ANKI_SOURCE, timeout=25) as response:
            tree = ast.parse(response.read())
        manager = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "AddonManager")
        methods = {"install", "_install", "_disableConflicting", "allAddonConflicts", "isEnabled",
                   "addonConflicts", "addonMeta", "writeAddonMeta", "_addonMetaPath", "allAddons",
                   "_userFilesPath", "backupUserFiles", "restoreUserFiles", "_userFilesBackupPath",
                   "addonsFolder", "readManifestFile"}
        nodes = [node for node in manager.body if isinstance(node, ast.FunctionDef) and node.name in methods]
        nodes += [node for node in manager.body if isinstance(node, ast.AnnAssign)
                  and isinstance(node.target, ast.Name) and node.target.id == "_manifest_schema"]
        manager.body = nodes
        helpers = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "package_name_valid"]
        namespace = {"os": os, "json": json, "ZipFile": zipfile.ZipFile, "zipfile": zipfile,
                     "defaultdict": defaultdict,
                     "InstallError": SimpleNamespace, "InstallOk": SimpleNamespace,
                     "gui_hooks": SimpleNamespace(addon_manager_will_install_addon=lambda *_: None,
                                                   addon_manager_did_install_addon=lambda *_: None)}
        module = ast.Module(body=helpers + [manager], type_ignores=[])
        exec(compile(module, ANKI_SOURCE, "exec", flags=__future__.annotations.compiler_flag), namespace)
        cls.manager_class = namespace["AddonManager"]

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / "addons21"
        self.root.mkdir()
        self.manager = object.__new__(self.manager_class)
        self.manager.mw = SimpleNamespace(pm=SimpleNamespace(addonFolder=lambda: str(self.root)))

        def meta(package):
            data = self.manager.addonMeta(package)
            return SimpleNamespace(dir_name=package, enabled=not data.get("disabled", False),
                                   conflicts=data.get("conflicts", []), compatible=lambda: True)

        def enable(package, enable=None):
            data = self.manager.addonMeta(package)
            data["disabled"] = not enable
            self.manager.writeAddonMeta(package, data)

        def delete(package):
            target = Path(self.manager.addonsFolder(package)).resolve()
            self.assertEqual(target.parent, self.root)
            shutil.rmtree(target)

        self.manager.addon_meta = meta
        self.manager.all_addon_meta = lambda: [meta(package) for package in self.manager.allAddons()]
        self.manager.toggleEnabled = enable
        self.manager.deleteAddon = delete

    def existing(self, package):
        path = self.root / package
        (path / "user_files").mkdir(parents=True)
        (path / "__init__.py").write_text("# existing build")
        (path / "obsolete.py").write_text("# should be removed during replacement")
        (path / "user_files/custom.wav").write_bytes(b"original uploaded audio")
        (path / "meta.json").write_text(json.dumps({"disabled": False, "config": {
            "question_seconds": 37, "audio_enabled": False, "sentinel": "keep"},
            "custom_metadata": "keep too"}))
        return path

    def test_replacement_and_reinstall_preserve_configuration_and_user_files(self):
        installed = self.existing("1237336370")
        for _ in range(2):
            self.manager.install(str(NEW), force_enable=True)
            self.assertFalse((installed / "obsolete.py").exists())
            self.assertEqual((installed / "user_files/custom.wav").read_bytes(), b"original uploaded audio")
            data = self.manager.addonMeta("1237336370")
            self.assertEqual(data["config"]["question_seconds"], 37)
            self.assertFalse(data["config"]["audio_enabled"])
            self.assertEqual(data["custom_metadata"], "keep too")
            self.assertFalse(data["disabled"])
            self.assertEqual(self.manager.allAddons(), ["1237336370"])

    def test_existing_manual_diagnostic_is_disabled_during_replacement(self):
        self.existing("1237336370")
        manual = self.existing("speed_streak_v2_05")
        self.manager.install(str(NEW), force_enable=True)
        self.assertTrue(self.manager.addonMeta("speed_streak_v2_05")["disabled"])
        self.assertFalse(self.manager.addonMeta("1237336370")["disabled"])
        self.assertTrue((manual / "user_files/custom.wav").exists())


if __name__ == "__main__":
    unittest.main()
