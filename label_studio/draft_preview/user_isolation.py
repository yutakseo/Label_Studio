"""Keep each annotator's saves separate and retain mask revision snapshots."""
import copy
import json
import os
from pathlib import Path
from uuid import uuid4

from django.db import transaction
from django.db.models.signals import pre_delete, pre_save
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied


def isolate_update(view, request, args, kwargs, update):
    from tasks.models import Annotation, AnnotationDraft

    with transaction.atomic():
        original = view.get_object()  # Preserve the view's project permission checks.
        original = Annotation.objects.select_for_update().get(pk=original.pk)
        if original.completed_by_id not in (None, request.user.pk):
            # Validate before making a copy; a bad request must not create a label.
            serializer = view.get_serializer(original, data=request.data, partial=request.method == 'PATCH')
            serializer.is_valid(raise_exception=True)
            own = Annotation.objects.filter(
                task_id=original.task_id, completed_by=request.user,
                parent_annotation=original,
            ).order_by('pk').first()
            if own is None:
                own = Annotation.objects.create(
                    task=original.task, project=original.project,
                    completed_by=request.user, updated_by=request.user,
                    parent_annotation=original, result=copy.deepcopy(original.result),
                    result_count=original.result_count, lead_time=0,
                )
            # Rebind only this user's autosave, never another user's draft.
            AnnotationDraft.objects.filter(annotation=original, user=request.user).update(annotation=own)
            view.kwargs[view.lookup_url_kwarg or view.lookup_field] = own.pk
            kwargs[view.lookup_url_kwarg or view.lookup_field] = own.pk
        return update(request, *args, **kwargs)


def protect_delete(annotation, user):
    if annotation.completed_by_id not in (None, user.pk):
        raise PermissionDenied('다른 사용자의 라벨은 삭제할 수 없습니다.')


def draft_annotation(task_id, annotation_id, user):
    from tasks.models import Annotation

    if annotation_id is None:
        return None
    annotation = Annotation.objects.get(pk=annotation_id, task_id=task_id)
    # Keep drafts detached from a foreign label so saving that label cannot
    # delete someone else's unsent work. The result itself still stays intact.
    return annotation.pk if annotation.completed_by_id == user.pk else None


def archive_revision(sender, instance, **kwargs):
    """Archive the persisted revision before any save or deletion, fail closed."""
    if not instance.pk:
        return
    previous = sender.objects.filter(pk=instance.pk).values().first()
    if previous is None:
        return
    root = Path(os.environ.get('LABEL_STUDIO_REVISION_DIR', '/label-studio/data/mask-revisions'))
    folder = root / str(previous.get('task_id')) / sender.__name__ / str(instance.pk)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (timezone.now().strftime('%Y%m%dT%H%M%S%fZ') + '-' + uuid4().hex + '.json')
    # Exclusive creation and fsync retain completed snapshots on the data volume.
    with path.open('x') as stream:
        json.dump(previous, stream, ensure_ascii=False, default=str)
        stream.flush()
        os.fsync(stream.fileno())


def install_revision_history():
    from tasks.models import Annotation, AnnotationDraft

    for model in (Annotation, AnnotationDraft):
        for signal in (pre_save, pre_delete):
            signal.connect(archive_revision, sender=model, weak=False,
                           dispatch_uid=f'mask_revision_{model.__name__}_{id(signal)}')
