"""Build only runtime files, using stable ordering/timestamps for reproducibility."""
from pathlib import Path
import json
import zipfile

root = Path(__file__).resolve().parent.parent
manifest = json.loads((root / "manifest.json").read_text())
files = ["manifest.json", "palette.js", "theme.js", "background.js", "palette.css",
         "chrome.css", "content.css", "compose.css", *sorted(manifest["icons"].values())]
output = root / "dist" / f"everforest-dark-medium-{manifest['version']}.xpi"
output.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
    for name in files:
        info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, (root / name).read_bytes())
print(output)
