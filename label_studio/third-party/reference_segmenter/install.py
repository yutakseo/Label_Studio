"""Enable the extension's panel injection after settings are initialized."""
from pathlib import Path

settings = Path(__file__).resolve().parents[1] / "core/settings/label_studio.py"
line = 'MIDDLEWARE.append("reference_segmenter.middleware.PanelMiddleware")'
source = settings.read_text()
if line not in source:
    settings.write_text(source + '\n# Curved dark-line masking extension\n' + line + '\n')
