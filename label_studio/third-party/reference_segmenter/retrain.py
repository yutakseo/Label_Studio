"""Discard active learned weights, retrain saved correction patches only from random initialization."""
import argparse
import fcntl
import hashlib
import json
import os
import re
import shutil
from datetime import datetime,timezone
from pathlib import Path

import numpy as np
from . import neural
from .validate import metrics


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--checkpoint',type=Path,required=True)
    parser.add_argument('--steps',type=int,default=1500)
    args=parser.parse_args()
    checkpoint=args.checkpoint;directory=checkpoint.parent;key=checkpoint.stem
    samples=directory/(key+'.samples')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output=directory/'retraining'/stamp;output.mkdir(parents=True,exist_ok=False)
    marker=directory/(key+'.retraining')
    marker.write_text(json.dumps({'started':stamp,'output':str(output)}))
    try:
        with (directory/(key+'.lock')).open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            paths=sorted((samples/'corrections').glob('*.npz'))
            if not paths:raise ValueError('학습할 수정 패치가 없습니다.')
            training=[];manifest=[];task_ids=set()
            for path in paths:
                with np.load(path,allow_pickle=False) as data:
                    rgb,mask=data['image'],data['mask']
                    if rgb.shape!=(64,64,3) or mask.shape!=(64,64) or not np.isin(mask,[0,1]).all():raise ValueError('학습 데이터 형식 오류')
                    training.append((rgb,mask))
                    task_ids.add(int(re.match(r'(?:user_\d+_)?task_(\d+)',path.stem)[1]))
                    manifest.append({'file':str(path.relative_to(samples)),'shape':list(mask.shape),'foreground':int(mask.sum()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
            validation=[];validation_ids=[]
            for path in sorted((samples/'validation').glob('*.npz')):
                task=int(re.match(r'(?:user_\d+_)?task_(\d+)',path.stem)[1])
                if task in task_ids:continue
                with np.load(path,allow_pickle=False) as data:validation.append((data['image'],data['mask']))
                validation_ids.append(task)
            if not validation:raise ValueError('학습과 겹치지 않는 검증 데이터가 없습니다.')
            (output/'manifest.json').write_text(json.dumps({'training':manifest,'validation_tasks':validation_ids},indent=2))
            if checkpoint.exists():
                shutil.copy2(checkpoint,output/'before.pt')
            state_path=checkpoint.with_suffix('.json')
            if state_path.exists():shutil.copy2(state_path,output/'before.json')
            baseline=[]
            if checkpoint.exists():
                for task,(rgb,truth) in zip(validation_ids,validation):
                    pred=neural.predict(checkpoint,rgb) > 0;gt=truth > 0
                    baseline.append({'task':task,'tp':int((pred&gt).sum()),'fp':int((pred&~gt).sum()),'fn':int((~pred&gt).sum())})
                for row in baseline:
                    row['dice']=2*row['tp']/max(1,2*row['tp']+row['fp']+row['fn'])
                print('BASELINE',metrics(baseline),flush=True)
            print('TRAIN',len(training),'VALIDATION',validation_ids,'INITIALIZATION random',flush=True)
            info=neural.train(output/'scratch.pt',training,steps=args.steps,batch_size=8,
                              start_from_scratch=True,learning_rate=3e-4,validation_pairs=validation,
                              validation_interval=100,callback=lambda step,loss:print('step',step,'metric',loss,flush=True))
            rows=[]
            for task,(rgb,truth) in zip(validation_ids,validation):
                mask=neural.predict(output/'scratch.pt',rgb);gt=truth>0;pred=mask>0
                tp=int((pred&gt).sum());fp=int((pred&~gt).sum());fn=int((~pred&gt).sum())
                row={'task':task,'tp':tp,'fp':fp,'fn':fn,'dice':2*tp/max(1,2*tp+fp+fn)};rows.append(row)
                from PIL import Image
                Image.fromarray(mask).save(output/f'task_{task}_mask.png')
                print('validation',row,flush=True)
            report={'training_scope':'correction_patches_only','initialization':'random, no previous or pretrained weights loaded','training':info,
                    'validation_tasks':validation_ids,'before_validation_full_images':metrics(baseline),'validation_full_images':metrics(rows),'per_task':rows,
                    'note':'Validation images also selected the best training checkpoint; not an independent test.'}
            (output/'report.json').write_text(json.dumps(report,indent=2))
            if checkpoint.exists():
                backup=checkpoint.with_suffix('.previous.pt')
                temporary=backup.with_suffix('.tmp.pt');shutil.copy2(checkpoint,temporary);os.replace(temporary,backup)
            temporary=checkpoint.with_suffix('.tmp.pt');shutil.copyfile(output/'scratch.pt',temporary);os.replace(temporary,checkpoint)
            state_path=checkpoint.with_suffix('.json')
            state=json.loads(state_path.read_text()) if state_path.exists() else {}
            state['neural']=info
            state['retraining_report']=str(output/'report.json')
            temporary=state_path.with_suffix('.tmp');temporary.write_text(json.dumps(state));os.replace(temporary,state_path)
            print('REPORT',output/'report.json',flush=True)
            print('ACTIVE',checkpoint,flush=True)
    finally:
        marker.unlink(missing_ok=True)


if __name__=='__main__':main()
