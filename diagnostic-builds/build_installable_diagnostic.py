"""Make the diagnostic package replace the existing AnkiWeb installation."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "2.05-macos-diagnostic.1/speed_streak_2_05_macos_diagnostic_1.ankiaddon"
OUTPUT = ROOT / "2.05-macos-diagnostic.2/speed_streak_2_05_macos_diagnostic_2.ankiaddon"
ANKIWEB_ID = "1237336370"


def build():
    previous = json.loads(SOURCE.with_suffix(".provenance.json").read_text())
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == previous["package_sha256"]
    with zipfile.ZipFile(SOURCE) as archive:
        assert archive.testzip() is None
        entries = {name: archive.read(name) for name in archive.namelist()}
    manifest = json.loads(entries["manifest.json"])
    manual_identity = manifest["package"]
    manifest["package"] = ANKIWEB_ID
    manifest["conflicts"] = sorted((set(manifest.get("conflicts", [])) | {manual_identity}) - {ANKIWEB_ID})
    entries["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    entries["build_info.py"] = b'BUILD_ID = "2.05-macos-diagnostic.2"\n'
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(entries.items()):
            archive.writestr(name, data)
    result = {
        **previous,
        "build": "2.05-macos-diagnostic.2",
        "package_sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
        "modified_entries": sorted(set(previous["modified_entries"]) | {"manifest.json"}),
        "previous_diagnostic_sha256": previous["package_sha256"],
        "installation_package": ANKIWEB_ID,
        "purpose": "Observational logging plus AnkiWeb installation identity; preserves the published feature implementation.",
    }
    OUTPUT.with_suffix(".provenance.json").write_text(json.dumps(result, indent=2) + "\n")
    print(OUTPUT)
    print("SHA256:", result["package_sha256"])


if __name__ == "__main__":
    build()
