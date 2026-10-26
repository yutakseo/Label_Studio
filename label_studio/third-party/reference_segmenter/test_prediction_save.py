"""Run against the configured DB inside a transaction that is always rolled back."""
import os
import unittest
os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings.label_studio')
import django
django.setup()
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory,force_authenticate
from tasks.models import Task,Prediction
from .views import ReferencePredictionSaveAPI


class PredictionSaveTests(unittest.TestCase):
    def test_create_retry_update_deduplication_and_invalid_requests(self):
        user=get_user_model().objects.get(pk=1)
        project_task=Task.objects.for_user(user).filter(project__organization=user.active_organization).first()
        self.assertIsNotNone(project_task)
        factory=APIRequestFactory()
        view=ReferencePredictionSaveAPI.as_view({'post':'create'})
        with transaction.atomic():
            try:
                task=Task.objects.create(project_id=project_task.project_id,data=project_task.data)
                other=Prediction.objects.create(task=task,project_id=task.project_id,model_version='Other model',result=[])
                def save(data,authenticated=True):
                    req=factory.post('/reference-segmenter/predictions/save',data,format='json')
                    if authenticated:force_authenticate(req,user=user)
                    return view(req)
                payload={'task':task.pk,'result':[]}
                first=save(payload)
                self.assertEqual(first.status_code,201,first.data)
                ident=first.data['id']
                retry=save(payload)
                self.assertEqual(retry.status_code,200,retry.data)
                self.assertEqual(retry.data['id'],ident)
                duplicate=Prediction.objects.create(task=task,project_id=task.project_id,model_version='Reference Segmenter',result=[])
                import numpy as np
                from .processing import brush_result
                updated_mask=np.zeros((64,64),np.uint8);updated_mask[5:10,8:15]=255
                payload['result']=brush_result(updated_mask,'brush','image','Exposure')
                updated=save(payload)
                self.assertEqual(updated.status_code,200)
                self.assertEqual(updated.data['id'],ident)
                self.assertEqual(Prediction.objects.get(pk=ident).result,payload['result'])
                self.assertFalse(Prediction.objects.filter(pk=duplicate.pk).exists())
                self.assertEqual(Prediction.objects.filter(task=task,model_version='Reference Segmenter').count(),1)
                self.assertTrue(Prediction.objects.filter(pk=other.pk).exists())
                self.assertEqual(save({'task':task.pk}).status_code,400)
                self.assertEqual(save({'task':'invalid','result':[]}).status_code,400)
                self.assertIn(save(payload,False).status_code,(401,403))
            finally:
                transaction.set_rollback(True)
