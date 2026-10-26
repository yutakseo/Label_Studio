from pathlib import Path
settings = Path(__file__).resolve().parents[1] / 'core/settings/label_studio.py'
line = 'MIDDLEWARE.append("draft_preview.middleware.DraftPreviewMiddleware")'
source = settings.read_text()
if line not in source:
    settings.write_text(source + '\n# Autosaved draft previews\n' + line + '\n')

source = settings.read_text()
merge_urlconf = 'ROOT_URLCONF = "draft_preview.merge_urls"'
if merge_urlconf not in source:
    settings.write_text(source + '\n# Merge saved annotation and prediction masks\n' + merge_urlconf + '\n')

# Apply before exports are serialized, including snapshot format conversions.
from export_filter import patch
patch(settings.parents[2] / 'data_export/serializers.py')
