"""Train from the latest saved masks; task-disjoint validation and prediction publishing."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import numpy as np
from PIL import Image


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--project',type=int,required=True)
    parser.add_argument('--user',type=int,required=True)
    parser.add_argument('--steps',type=int,default=300)
    parser.add_argument('--publish',action='store_true')
    args=parser.parse_args()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings.label_studio')
    import django
    django.setup()
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from tasks.models import Task, Prediction
    from mask_cleanup.processing import decode_checked
    from . import neural
    from .learning import predict as gaussian_predict
    from .processing import brush_result
    target=['brush','image','Exposure']
    key=hashlib.sha256(json.dumps(target).encode()).hexdigest()
    directory=Path(settings.BASE_DATA_DIR)/'reference_segmenter'/str(args.project)/str(args.user)
    directory.mkdir(parents=True,exist_ok=True)
    run=directory/'unet_initial'
    run.mkdir(exist_ok=True)
    user=get_user_model().objects.get(pk=args.user)
    tasks=list(Task.objects.for_user(user).filter(project_id=args.project).order_by('id'))
    base=Path(settings.BASE_DATA_DIR).resolve()
    def image_for(task):
        url=urlparse(task.data['image'])
        if url.path!='/data/local-files/':raise ValueError('로컬 파일 경로만 학습 데이터로 읽습니다.')
        path=(base/parse_qs(url.query)['d'][0]).resolve()
        if not path.is_relative_to(base):raise ValueError('허용된 데이터 경로 밖입니다.')
        with Image.open(path) as image:
            if image.width*image.height>16_000_000 or image.getexif().get(274,1)!=1 or getattr(image,'n_frames',1)!=1:raise ValueError('지원하지 않는 이미지입니다.')
            return np.array(image.convert('RGB'))
    pairs=[];manifest=[]
    for task in tasks:
        annotation=task.annotations.filter(completed_by=user,was_cancelled=False).order_by('-updated_at').first()
        if annotation is None:continue
        matched=[r for r in annotation.result or [] if r.get('type')=='brushlabels' and r.get('from_name')==target[0] and r.get('to_name')==target[1] and target[2] in r.get('value',{}).get('brushlabels',[])]
        if not matched:continue
        rgb=image_for(task);h,w=rgb.shape[:2];mask=np.zeros((h,w),np.uint8)
        for r in matched:
            if (r['original_width'],r['original_height'])!=(w,h) or r.get('image_rotation',0)!=0:raise ValueError('원본과 마스크 크기가 다릅니다.')
            mask|=(decode_checked(r['value']['rle'],w*h*4).reshape(h,w,4)[:,:,3]>0).astype(np.uint8)
        pairs.append((rgb,mask));manifest.append({'task':task.pk,'annotation':annotation.pk,'shape':[h,w],'pixels':int(mask.sum())})
        print('dataset',manifest[-1],flush=True)
    if len(pairs)<4:raise ValueError('검증을 분리하려면 저장된 마스크가 있는 태스크가 4개 이상 필요합니다.')
    indices=np.random.default_rng(42).permutation(len(pairs));nv=max(1,len(pairs)//4);valid=set(indices[:nv].tolist())
    for i,(rgb,mask) in enumerate(pairs):
        neural.save_pair(directory/(key+'.samples')/('validation' if i in valid else 'train'),rgb,mask,'task_'+str(manifest[i]['task']))
        manifest[i]['split']='validation' if i in valid else 'train'
    (run/'manifest.json').write_text(json.dumps(manifest,indent=2))
    checkpoint=directory/(key+'.pt')
    candidate=run/'candidate.pt'
    # Always start bootstrap from the original installed segmentation weights.
    if candidate.exists():candidate.unlink()
    training=[p for i,p in enumerate(pairs) if i not in valid]
    with neural.GPU_LOCK:
        info=neural.train(candidate,training,steps=args.steps,callback=lambda step,loss:print('step',step,'loss',round(loss,5),flush=True))
    state=json.loads((directory/(key+'.json')).read_text())
    def evaluate(fn):
        tp=fp=fn_count=0;individual=[]
        for i in sorted(valid):
            rgb,mask=pairs[i];out=fn(rgb)>0;gt=mask>0
            a=int((out&gt).sum());b=int((out&~gt).sum());c=int((~out&gt).sum());tp+=a;fp+=b;fn_count+=c
            individual.append({'task':manifest[i]['task'],'dice':2*a/max(1,2*a+b+c)})
        return {'dice':2*tp/max(1,2*tp+fp+fn_count),'iou':tp/max(1,tp+fp+fn_count),'precision':tp/max(1,tp+fp),'recall':tp/max(1,tp+fn_count),'tasks':individual}
    metrics={}
    for name,fn in [('gaussian',lambda rgb:gaussian_predict(state,rgb)),('pretrained_unet',lambda rgb:neural.predict(neural.initial_weights(),rgb)),('finetuned_unet',lambda rgb:neural.predict(candidate,rgb))]:
        metrics[name]=evaluate(fn);print(name,json.dumps(metrics[name]),flush=True)
    import shutil
    selected=candidate if metrics['finetuned_unet']['dice']>=metrics['pretrained_unet']['dice'] else neural.initial_weights()
    temporary=checkpoint.with_suffix('.tmp.pt');shutil.copyfile(selected,temporary);os.replace(temporary,checkpoint)
    report={'training':info,'validation':metrics,'selected':selected.name,'manifest':manifest,
            'legacy_rounds':state.get('round',0),'note':'Legacy 53 patch images were not retained; training uses saved annotations. Validation is task-disjoint within this project, not an independent specimen study.'}
    (run/'report.json').write_text(json.dumps(report,indent=2))
    if args.publish:
        for task in tasks:
            rgb=image_for(task);mask=neural.predict(checkpoint,rgb)
            results=brush_result(mask,*target)
            prediction=Prediction.objects.create(task=task,project_id=task.project_id,model_version='Reference Segmenter',result=results)
            Image.fromarray(mask).save(run/('task_'+str(task.pk)+'_mask.png'))
            print('prediction',task.pk,prediction.pk,'pixels',int(np.count_nonzero(mask)),flush=True)
    print('REPORT',run/'report.json',flush=True)


if __name__=='__main__':main()
