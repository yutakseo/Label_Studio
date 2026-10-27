import io
import json
import os
import unittest
from types import SimpleNamespace

os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings.label_studio')
import django
django.setup()
from django.test import RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import resolve
from PIL import Image
from .views import preview
from . import test_processing as fixtures


class DarkLineHttpTests(unittest.TestCase):
    def request(self, authenticated=True, csrf=True, options=None):
        buffer=io.BytesIO();Image.fromarray(fixtures.DarkLineTests().image()).save(buffer,format='PNG')
        r=RequestFactory().post('/reference-segmenter/preview',{'image':SimpleUploadedFile('source.png',buffer.getvalue(),'image/png'),
            'options':json.dumps(fixtures.OPTIONS if options is None else options),'from_name':'brush','to_name':'image','label':'Exposure'})
        r.user=SimpleNamespace(is_authenticated=authenticated);r._dont_enforce_csrf_checks=csrf
        return r

    def test_panel_cache_invalidation(self):
        from .views import script
        from .middleware import PanelMiddleware
        from django.http import HttpResponse
        response=script(RequestFactory().get('/reference-segmenter/panel.js?v=old'))
        self.assertIn('no-store',response['Cache-Control'])
        self.assertIn("+ 새 라벨 추가".encode(),response.content)
        middleware=PanelMiddleware(lambda request:HttpResponse('<html><body></body></html>'))
        html=middleware(RequestFactory().get('/projects/16/data'))
        self.assertRegex(html.content.decode(),r'/reference-segmenter/panel\.js\?v=[0-9a-f]{12}')

    def test_preview_and_route(self):
        r=preview(self.request());self.assertEqual(r.status_code,200)
        data=json.loads(r.content);self.assertEqual(data['stats']['components'],1)
        self.assertEqual(data['results'][0]['original_width'],320)
        self.assertTrue(data['difference'].startswith('data:image/png;base64,'))
        self.assertEqual(resolve('/reference-segmenter/preview').func,preview)

    def test_auth_csrf_and_invalid_parameters(self):
        self.assertEqual(preview(self.request(authenticated=False)).status_code,401)
        self.assertEqual(preview(self.request(csrf=False)).status_code,403)
        self.assertEqual(preview(self.request(options={'blur_size':20})).status_code,400)
        self.assertEqual(preview(self.request(options=[])).status_code,400)


if __name__ == '__main__':
    unittest.main()

class LearningHttpTests(unittest.TestCase):
    def test_train_predict_status_and_access(self):
        import tempfile
        from unittest.mock import patch
        from django.test import override_settings
        from .views import learn, Task
        import numpy as np

        def upload(array):
            stream = io.BytesIO()
            Image.fromarray(array).save(stream, format='PNG')
            return SimpleUploadedFile('image.png', stream.getvalue(), 'image/png')

        def request(action, **extra):
            req = RequestFactory().post('/reference-segmenter/learn', dict(
                task='1', action=action, from_name='brush', to_name='image', label='Target', **extra))
            req.user = SimpleNamespace(is_authenticated=True, pk=10)
            req._dont_enforce_csrf_checks = True
            return req

        rgb = np.full((64, 64, 3), 220, np.uint8)
        rgb[:, 24:32] = 25
        mask = np.zeros((64, 64), np.uint8)
        mask[:, 24:32] = 255
        with tempfile.TemporaryDirectory() as directory, override_settings(BASE_DATA_DIR=directory), patch.object(Task.objects, 'for_user') as tasks, patch('reference_segmenter.neural.train', return_value={'pairs':1, 'steps':20}) as train_model, patch('reference_segmenter.neural.predict', return_value=mask) as predict_model:
            from unittest.mock import MagicMock
            from datetime import datetime, timezone
            from .processing import brush_result
            annotations = MagicMock()
            saved = SimpleNamespace(pk=7, updated_at=datetime.now(timezone.utc), result=brush_result(mask, 'brush', 'image', 'Target'))
            annotations.filter.return_value.order_by.return_value = [saved]
            annotations.filter.return_value.first.return_value = saved
            tasks.return_value.get.return_value = SimpleNamespace(pk=1, project_id=5, annotations=annotations, project=SimpleNamespace(parsed_label_config={'brush':{'type':'BrushLabels','to_name':['image'],'labels':['Target','Dryspot']}}))
            status = json.loads(learn(request('status')).content)
            self.assertEqual(status['round'], 0)
            self.assertEqual(status['sources'][0]['id'], 7)
            imported = learn(request('mask', annotation='7'))
            self.assertEqual(imported.status_code, 200)
            import base64
            decoded = np.array(Image.open(io.BytesIO(base64.b64decode(json.loads(imported.content)['mask'].split(',')[1]))))
            self.assertTrue(np.array_equal(decoded, mask))
            annotations.filter.return_value.first.return_value = None
            self.assertEqual(learn(request('mask', annotation='8')).status_code, 400)
            annotations.filter.return_value.first.return_value = saved
            import hashlib
            from pathlib import Path
            key=hashlib.sha256(json.dumps(['brush','image','Target']).encode()).hexdigest()
            unused=Path(directory)/'reference_segmenter/5/shared'/key/(key+'.samples')/'train'
            unused.mkdir(parents=True)
            np.savez_compressed(unused/'task_999.npz',image=np.zeros((256,256,3),np.uint8),mask=np.zeros((256,256),np.uint8))
            trained = learn(request('train', image=upload(rgb), mask=upload(mask)))
            self.assertEqual(trained.status_code, 200)
            self.assertEqual(json.loads(trained.content)['round'], 1)
            self.assertEqual(json.loads(trained.content)['steps'], 20)
            train_model.assert_called_once()
            from pathlib import Path
            Path(train_model.call_args.args[0]).touch()
            from pathlib import Path
            saved_pairs=list(Path(directory).rglob('*.npz'))
            saved_pairs=[p for p in saved_pairs if p.parent.name=='corrections']
            self.assertEqual(len(saved_pairs),1)
            self.assertEqual(len(train_model.call_args.args[1]),1)
            with np.load(saved_pairs[0]) as pair:
                self.assertTrue(np.array_equal(pair['image'],rgb))
                self.assertTrue(np.array_equal(pair['mask']>0,mask>0))
            result = learn(request('predict', image=upload(rgb)))
            self.assertEqual(result.status_code, 200)
            self.assertGreater(json.loads(result.content)['pixels'], 0)
            self.assertEqual(json.loads(learn(request('status')).content)['round'], 1)
            other = request('status'); other.user.pk = 11
            shared_status = json.loads(learn(other).content)
            self.assertEqual(shared_status['round'], 1)
            self.assertTrue(shared_status['trained'])
            annotations.filter.assert_called_with(completed_by=other.user, was_cancelled=False)
            other = request('train', image=upload(rgb), mask=upload(mask)); other.user.pk = 11
            self.assertEqual(learn(other).status_code, 200)
            self.assertEqual(len(train_model.call_args.args[1]), 2)
            self.assertEqual(json.loads(learn(request('status')).content)['round'], 2)
            other = request('predict', image=upload(rgb)); other.user.pk = 11
            self.assertEqual(learn(other).status_code, 200)
            self.assertEqual(predict_model.call_args.args[0], train_model.call_args.args[0])
            # Another defect class uses neither Target weights nor Target samples.
            fresh=request('status');fresh.POST=fresh.POST.copy();fresh.POST['label']='Dryspot'
            fresh_state=json.loads(learn(fresh).content)
            self.assertEqual(fresh_state['round'],0)
            self.assertEqual(fresh_state['training_pairs'],0)
            self.assertFalse(fresh_state['trained'])
            before_target=saved_pairs[0].read_bytes()
            dryspot_mask=255-mask
            fresh=request('train',image=upload(rgb),mask=upload(dryspot_mask));fresh.POST=fresh.POST.copy();fresh.POST['label']='Dryspot'
            self.assertEqual(learn(fresh).status_code,200)
            self.assertNotEqual(train_model.call_args.args[0],predict_model.call_args.args[0])
            self.assertEqual(len(train_model.call_args.args[1]),1)
            self.assertTrue(np.array_equal(train_model.call_args.args[1][0][1]>0,dryspot_mask>0))
            self.assertEqual(saved_pairs[0].read_bytes(),before_target)
            target_key=json.loads(learn(request('status')).content)['model_key']
            self.assertNotEqual(fresh_state['model_key'],target_key)
            self.assertEqual(json.loads(learn(request('status')).content)['training_pairs'],2)
            self.assertEqual(len(json.loads(learn(request('status')).content)['samples']),2)
            invalid=request('status');invalid.POST=invalid.POST.copy();invalid.POST['label']='Unregistered'
            self.assertEqual(learn(invalid).status_code,400)
            tasks.return_value.get.side_effect = Task.DoesNotExist
            self.assertEqual(learn(request('status')).status_code, 404)
        req = request('status'); req.user.is_authenticated = False
        self.assertEqual(learn(req).status_code, 401)
        req = request('status'); req._dont_enforce_csrf_checks = False
        self.assertEqual(learn(req).status_code, 403)
