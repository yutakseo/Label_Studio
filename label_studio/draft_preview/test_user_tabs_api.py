import os
import unittest
os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings.label_studio')
import django
django.setup()
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.test import APIRequestFactory,force_authenticate
from tasks.models import Task,Annotation,AnnotationDraft
from tasks.api import AnnotationsListAPI
from .user_isolation import draft_annotation,latest_user_drafts


class UserTabTests(unittest.TestCase):
    def test_user_save_updates_existing_and_drafts_attach_to_same_tab(self):
        user=get_user_model().objects.get(pk=1)
        source=Task.objects.for_user(user).filter(project_id=16).first()
        with transaction.atomic():
            try:
                task=Task.objects.create(project_id=source.project_id,data=source.data)
                factory=APIRequestFactory()
                def save():
                    req=factory.post('/api/tasks/0/annotations/',{'result':[]},format='json')
                    force_authenticate(req,user=user)
                    return AnnotationsListAPI.as_view()(req,pk=task.pk)
                first=save();self.assertEqual(first.status_code,201,first.data)
                ident=first.data['id']
                again=save();self.assertEqual(again.status_code,201,again.data)
                self.assertEqual(again.data['id'],ident)
                self.assertEqual(Annotation.objects.filter(task=task,completed_by=user).count(),1)
                merge=Annotation.objects.create(task=task,project_id=task.project_id,completed_by=user,result=[])
                task.meta={'mask_merge_annotations':{str(merge.pk):{'name':'MERGE'}}};task.save()
                self.assertEqual(save().data['id'],ident)
                self.assertTrue(Annotation.objects.filter(pk=merge.pk).exists())
                self.assertEqual(draft_annotation(task.pk,None,user),ident)
                a=AnnotationDraft.objects.create(task=task,user=user,annotation_id=ident,result=[])
                b=AnnotationDraft.objects.create(task=task,user=user,annotation_id=ident,result=[])
                shown=list(latest_user_drafts(AnnotationDraft.objects.filter(task=task),user).values_list('pk',flat=True))
                self.assertEqual(shown,[b.pk])
                self.assertTrue(AnnotationDraft.objects.filter(pk=a.pk).exists())
            finally:transaction.set_rollback(True)

    def test_all_authors_update_saved_time_and_export_latest_mask(self):
        import io
        import json
        import tempfile
        import zipfile
        from datetime import timedelta
        from pathlib import Path
        import numpy as np
        from PIL import Image
        from django.utils import timezone
        from tasks.api import AnnotationAPI
        from data_export.serializers import AnnotationSerializer as ExportAnnotationSerializer
        from mask_cleanup.tree_export.archive import write_archive
        from reference_segmenter.processing import brush_result

        users=list(get_user_model().objects.filter(is_active=True).order_by('pk'))
        self.assertGreaterEqual(len(users),2)
        source=Task.objects.for_user(users[0]).filter(project_id=16).first()
        factory=APIRequestFactory()
        with tempfile.TemporaryDirectory() as directory, transaction.atomic():
            try:
                image=Path(directory)/'test_dataset/images/test.png'
                image.parent.mkdir(parents=True)
                Image.new('RGB',(2,2)).save(image)
                task=Task.objects.create(project_id=source.project_id,
                    data={'image':'/data/local-files/?d=files/test_dataset/images/test.png'})
                old=timezone.now()-timedelta(days=3)
                records=[]
                for user in users:
                    annotation=Annotation.objects.create(task=task,project_id=task.project_id,
                        completed_by=user,result=[])
                    # A later-created annotation must not win over a freshly updated one.
                    Annotation.objects.filter(pk=annotation.pk).update(created_at=old,updated_at=old)
                    annotation.refresh_from_db()
                    records.append((user,annotation))
                merge=Annotation.objects.create(task=task,project_id=task.project_id,
                    completed_by=users[0],result=[])
                task.meta={'mask_merge_annotations':{str(merge.pk):{'name':'MERGE'}}};task.save()
                Annotation.objects.filter(pk=merge.pk).update(created_at=old,updated_at=old)
                merge.refresh_from_db()
                records.append((users[0],merge))
                for index,(user,annotation) in enumerate(records):
                    pixels=np.zeros((2,2),np.uint8);pixels.flat[index%4]=255
                    result=brush_result(pixels,'brush','image','Exposure')
                    before=timezone.now()
                    request=factory.patch(f'/api/annotations/{annotation.pk}/',
                        {'result':result,'updated_at':old.isoformat()},format='json')
                    force_authenticate(request,user=user)
                    response=AnnotationAPI.as_view()(request,pk=annotation.pk)
                    self.assertEqual(response.status_code,200,response.data)
                    annotation.refresh_from_db()
                    self.assertEqual(annotation.created_at,old)
                    self.assertGreaterEqual(annotation.updated_at,before)
                    self.assertEqual(annotation.updated_by_id,user.pk)
                    self.assertEqual(annotation.completed_by_id,user.pk)
                    self.assertEqual(annotation.result,result)
                    self.assertEqual(task.annotations.order_by('-updated_at','-pk').first().pk,annotation.pk)
                    exported=ExportAnnotationSerializer(annotation).data
                    self.assertEqual(exported['updated_at'],response.data['updated_at'])
                    self.assertEqual(exported['result'],result)
                    out=io.BytesIO()
                    manifest=write_archive(out,[task],directory,'image','brush','image','Exposure',task.project_id)
                    self.assertEqual(manifest['exported'][0]['annotation_id'],annotation.pk)
                    self.assertEqual(manifest['exported'][0]['updated_at'],annotation.updated_at.isoformat())
                    with zipfile.ZipFile(out) as archive:
                        with Image.open(io.BytesIO(archive.read('test_dataset/masks/test.png'))) as mask:
                            np.testing.assert_array_equal(np.array(mask),pixels)
                        saved=json.loads(archive.read(f'_annotations/task-{task.pk}.json'))['annotations'][0]
                        self.assertEqual(saved['updated_at'],annotation.updated_at.isoformat())
                        self.assertEqual(saved['updated_by'],user.pk)
                        self.assertEqual(saved['completed_by'],user.pk)
                    # Other authors' masks and timestamps stay intact.
                    for _,other in records:
                        if other.pk==annotation.pk:continue
                        previous=other.updated_at
                        other.refresh_from_db()
                        self.assertEqual(other.updated_at,previous)
            finally:
                transaction.set_rollback(True)
