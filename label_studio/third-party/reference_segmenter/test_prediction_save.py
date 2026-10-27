"""DB checks always roll back; predictions are isolated by brush/image/class."""
import os
import unittest
os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings.label_studio')
import django
django.setup()
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory,force_authenticate
from tasks.models import Task,Prediction
from projects.models import Project
from .views import ReferencePredictionSaveAPI
from .targets import prediction_version


class PredictionSaveTests(unittest.TestCase):
    def test_class_save_retry_legacy_adoption_and_access(self):
        import numpy as np
        from .processing import brush_result
        user=get_user_model().objects.get(pk=1)
        factory=APIRequestFactory()
        view=ReferencePredictionSaveAPI.as_view({'post':'create'})
        with transaction.atomic():
            try:
                project=Project.objects.create(title='Reference class regression',organization=user.active_organization,
                    created_by=user,label_config='<View><Image name="image" value="$image"/><BrushLabels name="brush" toName="image"><Label value="Exposure"/><Label value="Dryspot"/></BrushLabels></View>')
                task=Task.objects.create(project=project,data={'image':'/test.png'})
                pixels=np.zeros((64,64),np.uint8);pixels[4:8,10:15]=255
                exposure=brush_result(pixels,'brush','image','Exposure')
                dryspot=brush_result(pixels,'brush','image','Dryspot')
                legacy=Prediction.objects.create(task=task,project=project,model_version='Reference Segmenter',result=exposure)
                mixed=Prediction.objects.create(task=task,project=project,model_version='Reference Segmenter',result=exposure+dryspot)
                other=Prediction.objects.create(task=task,project=project,model_version='Other model',result=[])
                def save(data,authenticated=True):
                    req=factory.post('/reference-segmenter/predictions/save',{'task':task.pk,**data},format='json')
                    if authenticated:force_authenticate(req,user=user)
                    return view(req)
                first=save({'result':exposure})
                self.assertEqual(first.status_code,200,first.data)
                self.assertEqual(first.data['id'],legacy.pk)
                duplicate=Prediction.objects.create(task=task,project=project,model_version=prediction_version(('brush','image','Exposure')),result=exposure)
                retry=save({'result':exposure})
                self.assertEqual(retry.data['id'],legacy.pk)
                self.assertFalse(Prediction.objects.filter(pk=duplicate.pk).exists())
                second=save({'result':dryspot,'from_name':'brush','to_name':'image','label':'Dryspot'})
                self.assertEqual(second.status_code,201,second.data)
                self.assertNotEqual(second.data['id'],legacy.pk)
                self.assertEqual(Prediction.objects.get(pk=legacy.pk).result,exposure)
                self.assertTrue(Prediction.objects.filter(pk=other.pk).exists())
                self.assertEqual(Prediction.objects.get(pk=mixed.pk).result,exposure+dryspot)
                self.assertEqual(save({'result':[]}).status_code,400)
                self.assertEqual(save({'result':exposure+dryspot}).status_code,400)
                self.assertEqual(save({'result':exposure,'from_name':'brush','to_name':'image','label':'Dryspot'}).status_code,400)
                self.assertEqual(save({'result':[],'from_name':'brush','to_name':'image','label':'Unregistered'}).status_code,400)
                empty=save({'result':[],'from_name':'brush','to_name':'image','label':'Dryspot'})
                self.assertEqual(empty.data['id'],second.data['id'])
                self.assertEqual(Prediction.objects.get(pk=legacy.pk).result,exposure)
                self.assertEqual(save({}).status_code,400)
                self.assertIn(save({'result':exposure},False).status_code,(401,403))
            finally:transaction.set_rollback(True)
