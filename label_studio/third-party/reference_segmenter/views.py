import io
import json
import base64
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from .processing import MAX_PIXELS, detect, brush_result
from core.permissions import all_permissions
from tasks.api import PredictionAPI
from tasks.models import Task, Prediction
from django.db import transaction
from django.db.models import Q
from .targets import model_key, validate_target, prediction_version, result_target
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError


class BlackLinePredictionAPI(PredictionAPI):
    """Any project viewer may delete this generated candidate, regardless of creator."""
    permission_required = all_permissions.tasks_view

    def get_queryset(self):
        return super().get_queryset().filter(
            Q(model_version__in=["Reference Segmenter", "Black line", "검은 줄", "검은줄"])
            | Q(model_version__startswith="Reference Segmenter · "),
            task__in=Task.objects.for_user(self.request.user),
        )


class ReferencePredictionSaveAPI(PredictionAPI):
    """Serialize saves on the task, preserving one stable prediction per class."""
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            task_id=int(request.data.get('task'))
        except (ValueError,TypeError):
            raise ValidationError({'task':'올바른 태스크를 지정하세요.'})
        task=get_object_or_404(Task.objects.for_user(request.user).select_for_update().filter(
            project__organization=request.user.active_organization),pk=task_id)
        result=request.data.get('result')
        if not isinstance(result,list):
            raise ValidationError({'result':'예측 결과 목록이 필요합니다.'})
        supplied=[request.data.get(k) for k in ('from_name','to_name','label')]
        targets={result_target(r) for r in result if isinstance(r,dict)}
        if any(supplied):
            if not all(isinstance(value,str) and value for value in supplied):
                raise ValidationError({'label':'이미지와 브러시, 클래스를 함께 지정하세요.'})
            target=tuple(supplied)
        elif len(targets)==1 and None not in targets:
            target=targets.pop()
        else:
            raise ValidationError({'result':'한 번에 한 클래스의 마스크만 저장하세요.'})
        if target:
            try: validate_target(task.project,target)
            except ValueError as exc: raise ValidationError({'label':str(exc)})
            if any(not isinstance(r,dict) or result_target(r)!=target for r in result):
                raise ValidationError({'result':'선택한 클래스와 예측 마스크가 다릅니다.'})
        version=prediction_version(target)
        predictions=Prediction.objects.filter(task=task,model_version=version).order_by('id')
        existing=predictions.first()
        # Adopt only legacy tabs containing this exact class. Never delete other classes.
        legacy=[]
        if target:
            legacy=[p for p in Prediction.objects.filter(task=task,model_version='Reference Segmenter').order_by('id')
                    if p.result and all(result_target(r)==target for r in p.result)]
            if existing is None and legacy: existing=legacy[0]
        payload={'task':task.pk,'project':task.project_id,'model_version':version,'result':result}
        serializer=self.get_serializer(instance=existing,data=payload)
        serializer.is_valid(raise_exception=True)
        saved=serializer.save()
        predictions.exclude(pk=saved.pk).delete()
        Prediction.objects.filter(pk__in=[p.pk for p in legacy if p.pk!=saved.pk]).delete()
        return Response(serializer.data,status=200 if existing else 201)


def thumbnail(image):
    image = image.copy()
    image.thumbnail((900, 650))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()


@never_cache
def script(request):
    return HttpResponse(Path(__file__).with_name("panel.js").read_text(), content_type="application/javascript")


@require_POST
@csrf_protect
def preview(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "로그인이 필요합니다."}, status=401)
    try:
        uploaded = request.FILES["image"]
        if uploaded.size > 32 * 1024 * 1024:
            raise ValueError("이미지는 최대 32MB까지 지원합니다.")
        with Image.open(io.BytesIO(uploaded.read())) as source:
            if source.width * source.height > MAX_PIXELS:
                raise ValueError("최대 1600만 픽셀까지 지원합니다.")
            if source.getexif().get(274, 1) != 1 or getattr(source, "n_frames", 1) != 1:
                raise ValueError("방향을 정규화한 단일 프레임 이미지를 사용하세요.")
            image = source.convert("RGB")
        gray = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2GRAY)
        options = json.loads(request.POST.get("options", "{}"))
        if not isinstance(options, dict):
            raise ValueError("검출 설정 형식이 잘못되었습니다.")
        bbox = json.loads(request.POST.get("bbox", "null"))
        mask, background, difference, stats = detect(gray, options, bbox)
        results = brush_result(mask, request.POST["from_name"], request.POST["to_name"], request.POST["label"])
        overlay = Image.composite(Image.new("RGB", image.size, (255, 65, 65)), image,
                                  Image.fromarray(((mask > 0) * 140).astype(np.uint8)))
        return JsonResponse({"results": results, "stats": stats, "bbox": bbox,
                             "background": thumbnail(Image.fromarray(background)),
                             "difference": thumbnail(Image.fromarray(difference)), "preview": thumbnail(overlay)})
    except (cv2.error, ValueError, KeyError, TypeError, OSError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)


@require_POST
@csrf_protect
def learn(request):
    """Share model weights within an accessible project; keep annotation access personal."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': '로그인이 필요합니다.'}, status=401)
    import fcntl
    import os
    from django.conf import settings
    from .learning import update
    from . import neural
    try:
        task = Task.objects.for_user(request.user).get(pk=int(request.POST['task']))
        target = [request.POST[k] for k in ('from_name', 'to_name', 'label')]
        validate_target(task.project, target)
        key = model_key(target)
        from .storage import model_directory
        directory = model_directory(settings.BASE_DATA_DIR, task.project_id, key)
        path = directory / (key + '.json')
        action = request.POST.get('action', 'predict')
        if action not in ('train', 'predict', 'status', 'mask'):
            raise ValueError('지원하지 않는 작업입니다.')
        if (directory/(key+'.retraining')).exists() and action in ('train','predict'):
            raise ValueError('U-Net을 처음부터 재학습하고 있습니다. 완료 후 다시 실행하세요.')
        with (directory / (key + '.lock')).open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            state = json.loads(path.read_text()) if path.exists() else None
            if action == 'status':
                annotations = task.annotations.filter(completed_by=request.user, was_cancelled=False).order_by('-updated_at')
                sources = [{'id': a.pk, 'updated_at': a.updated_at.isoformat()} for a in annotations
                           if any(r.get('type') == 'brushlabels' and r.get('from_name') == target[0]
                                  and r.get('to_name') == target[1] and target[2] in r.get('value', {}).get('brushlabels', [])
                                  for r in (a.result or []))]
                sample_dir=directory/(key+'.samples')
                import re
                samples=[]
                for pair in sorted((sample_dir/'corrections').glob('*.npz')):
                    match=re.fullmatch(r'user_(\d+)_task_(\d+)_(\d+)_(\d+)\.npz',pair.name)
                    if match:
                        user_id,task_id,x,y=map(int,match.groups())
                        samples.append({'user_id':user_id,'task_id':task_id,'x':x,'y':y})
                paired=len(list((sample_dir/'corrections').glob('*.npz')))
                return JsonResponse({'round': (state or {}).get('round', 0), 'sources': sources,
                                     'label': target[2], 'model_key': key, 'samples': samples,
                                     'model': 'U-Net', 'training_pairs': paired, 'trained': (directory/(key+'.pt')).exists()})
            if action == 'mask':
                from mask_cleanup.processing import decode_checked
                annotation = task.annotations.filter(completed_by=request.user, was_cancelled=False,
                                                     pk=int(request.POST['annotation'])).first()
                if annotation is None:
                    raise ValueError('가져올 수 있는 저장된 마스크가 없습니다.')
                union = None
                work = 0
                for region in annotation.result or []:
                    value = region.get('value', {})
                    if (region.get('type') != 'brushlabels' or region.get('from_name') != target[0]
                            or region.get('to_name') != target[1] or target[2] not in value.get('brushlabels', [])):
                        continue
                    w, h = region.get('original_width'), region.get('original_height')
                    if (type(w) is not int or type(h) is not int or min(w, h) < 1 or w*h > MAX_PIXELS
                            or region.get('image_rotation', 0) != 0 or value.get('format') != 'rle'):
                        raise ValueError('회전 없는 원본 크기의 RLE 브러시 마스크만 지원합니다.')
                    work += w*h
                    if work > 64_000_000:
                        raise ValueError('마스크 영역이 너무 많습니다.')
                    rgba = decode_checked(value.get('rle'), w*h*4).reshape(h, w, 4)
                    if union is None:
                        union = np.zeros((h, w), np.uint8)
                    if union.shape != (h, w):
                        raise ValueError('마스크 크기가 서로 다릅니다.')
                    union |= (rgba[:, :, 3] > 0).astype(np.uint8) * 255
                if union is None:
                    raise ValueError('선택한 라벨의 브러시 마스크가 없습니다.')
                buffer = io.BytesIO()
                Image.fromarray(union).save(buffer, format='PNG')
                return JsonResponse({'mask': 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode()})
            uploaded = request.FILES['image']
            if uploaded.size > 32 * 1024 * 1024:
                raise ValueError('이미지는 최대 32MB입니다.')
            with Image.open(uploaded) as image:
                if image.width * image.height > MAX_PIXELS or image.getexif().get(274, 1) != 1 or getattr(image, 'n_frames', 1) != 1:
                    raise ValueError('방향이 정규화된 단일 이미지, 최대 1600만 픽셀을 지원합니다.')
                rgb = np.array(image.convert('RGB'))
            if action == 'train':
                uploaded_mask = request.FILES['mask']
                if uploaded_mask.size > 65536:
                    raise ValueError('패치 마스크가 너무 큽니다.')
                with Image.open(uploaded_mask) as image:
                    if image.size != (64, 64):
                        raise ValueError('마스크는 64×64이어야 합니다.')
                    mask = np.array(image.convert('L')) > 127
                if rgb.shape != (64, 64, 3):
                    raise ValueError('참고 이미지는 64×64이어야 합니다.')
                sample_dir=directory/(key+'.samples')
                x,y=int(request.POST.get('patch_x',0)),int(request.POST.get('patch_y',0))
                if not 0 <= x <= 100000 or not 0 <= y <= 100000:
                    raise ValueError('패치 좌표가 잘못되었습니다.')
                neural.save_pair(sample_dir/'corrections',rgb,mask,f'user_{request.user.pk}_task_{task.pk}_{x}_{y}')
                pairs=[]
                for part in ('corrections',):
                    if list((sample_dir/part).glob('*.npz')):
                        pairs.extend(neural.read_pairs(sample_dir/part))
                with neural.GPU_LOCK:
                    info=neural.train(directory/(key+'.pt'),pairs,steps=20)
                if np.any(mask) and not np.all(mask):
                    state = update(state, rgb, mask)
                else:
                    state = dict(state or {});state['round']=state.get('round',0)+1
                state['neural']={k:v for k,v in info.items() if k!='model_state_dict'}
                temporary = path.with_suffix('.tmp')
                temporary.write_text(json.dumps(state))
                os.replace(temporary, path)
                return JsonResponse({'round': state['round'], 'training_pairs': info['pairs'], 'steps': info['steps']})
            threshold=float(request.POST.get('threshold','.5'))
            if not np.isfinite(threshold) or not .01 <= threshold <= .99:
                raise ValueError('임계값은 0.01~0.99 범위입니다.')
            checkpoint=directory/(key+'.pt')
            with neural.GPU_LOCK:
                if not checkpoint.exists():
                    raise ValueError('먼저 참고 마스크 패치를 학습하세요.')
                mask = neural.predict(checkpoint,rgb,threshold)
            state=state or {'round':0}
        results = brush_result(mask, *target)
        overlay = Image.composite(Image.new('RGB', (rgb.shape[1], rgb.shape[0]), (255, 65, 65)),
                                  Image.fromarray(rgb), Image.fromarray((mask > 0).astype(np.uint8) * 140))
        buffer = io.BytesIO()
        Image.fromarray(mask).save(buffer, format='PNG')
        return JsonResponse({'round': state['round'], 'results': results,
                             'pixels': int(np.count_nonzero(mask)), 'preview': thumbnail(overlay),
                             'mask': 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode()})
    except Task.DoesNotExist:
        return JsonResponse({'error': '접근할 수 없는 태스크입니다.'}, status=404)
    except (ValueError, KeyError, TypeError, OSError, RuntimeError, Image.DecompressionBombError, cv2.error) as exc:
        return JsonResponse({'error': str(exc)}, status=400)
