from pathlib import Path
settings = Path(__file__).resolve().parents[1] / 'core/settings/label_studio.py'
line = 'MIDDLEWARE.append("draft_preview.middleware.DraftPreviewMiddleware")'
source = settings.read_text()
if line not in source:
    settings.write_text(source + '\n# Autosaved draft previews\n' + line + '\n')
