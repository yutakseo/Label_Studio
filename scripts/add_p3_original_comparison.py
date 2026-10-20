"""Run inside Label Studio: add the preserved P3 masks as comparison predictions."""
import json
import os
from pathlib import Path
from urllib.parse import unquote, urlparse, parse_qs

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.label_studio')
import django
django.setup()
from django.db import transaction
from tasks.models import Task, Prediction

source = Path('/label-studio/data/files/P3_72_with_masks/tasks.json')
originals = {
    Path(parse_qs(urlparse(t['data']['image']).query)['d'][0]).name:
    t['annotations'][0]['result']
    for t in json.loads(source.read_text())
}
tasks = list(Task.objects.filter(project__title='P3-Masking'))
assert len(tasks) == len(originals) == 72
with transaction.atomic():
    for task in tasks:
        name = Path(unquote(parse_qs(urlparse(task.data['image']).query)['d'][0])).name
        result = originals[name]
        Prediction.objects.update_or_create(
            task=task, project_id=task.project_id, model_version='mask_original',
            defaults={'result': result, 'score': None},
        )
        count = Prediction.objects.filter(task=task).count()
        Task.objects.filter(pk=task.pk).update(total_predictions=count)
print('Verified comparison tabs:', Prediction.objects.filter(
    project__title='P3-Masking', model_version='mask_original').count())
