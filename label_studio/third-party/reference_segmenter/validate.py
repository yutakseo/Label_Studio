"""Evaluate immutable checkpoint snapshots against saved validation pairs; no DB writes."""
import argparse
import fcntl
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from . import neural


def metrics(rows):
    tp=sum(r['tp'] for r in rows);fp=sum(r['fp'] for r in rows);fn=sum(r['fn'] for r in rows)
    return {'tasks':len(rows),'dice':2*tp/max(1,2*tp+fp+fn),'iou':tp/max(1,tp+fp+fn),
            'precision':tp/max(1,tp+fp),'recall':tp/max(1,tp+fn),
            'macro_dice':float(np.mean([r['dice'] for r in rows])) if rows else None}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--checkpoint',type=Path,required=True)
    args=parser.parse_args()
    checkpoint=args.checkpoint;key=checkpoint.stem;directory=checkpoint.parent
    samples=directory/(key+'.samples')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output=directory/'evaluations'/stamp;output.mkdir(parents=True,exist_ok=False)
    with (directory/(key+'.lock')).open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        snapshot=output/'evaluated.pt';shutil.copyfile(checkpoint,snapshot)
        snapshot_metadata=torch.load(snapshot,map_location='cpu',weights_only=True)
        training_paths=list((samples/'corrections').glob('*.npz'))
        if snapshot_metadata.get('training_scope')!='correction_patches_only':
            training_paths+=list((samples/'train').glob('*.npz'))
        del snapshot_metadata
        trained_tasks={int(re.match(r'(?:user_\d+_)?task_(\d+)',p.stem)[1]) for p in training_paths}
        sample_names=[str(p.relative_to(samples)) for p in training_paths]
        validation=[]
        for path in sorted((samples/'validation').glob('*.npz')):
            with np.load(path,allow_pickle=False) as pair:
                validation.append((int(path.stem.split('_')[1]),pair['image'],pair['mask']>0))
    if not validation:raise ValueError('검증 데이터가 없습니다.')
    _,metadata=neural.load(snapshot)
    report={'evaluated_at_utc':stamp,'threshold':.5,'checkpoint_sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),
            'training_scope':metadata.get('training_scope','legacy_mixed'), 'patch_size':metadata.get('patch_size'),
            'steps':metadata.get('steps'),'training_pairs':metadata.get('pairs'),
            'training_samples':sample_names,'contaminated_validation_tasks':[t for t,_,_ in validation if t in trained_tasks],
            'clean_validation_tasks':[t for t,_,_ in validation if t not in trained_tasks],'models':{}}
    for name,weights in [('initial_300_steps',directory/'unet_initial/candidate.pt'),('current',snapshot)]:
        rows=[]
        for task,rgb,gt in validation:
            with neural.GPU_LOCK:
                if name=='initial_300_steps':
                    from u_net_labeller.interface import predict as legacy_predict
                    from u_net_labeller.model import UNet as LegacyUNet
                    baseline_checkpoint=torch.load(weights,map_location='cpu',weights_only=True)
                    baseline=LegacyUNet(baseline_checkpoint['base_channels']).to(neural.device())
                    baseline.load_state_dict(baseline_checkpoint['model_state_dict'])
                    mask=legacy_predict(Image.fromarray(rgb),baseline.eval(),device=neural.device(),threshold=.5,batch_size=8)
                else:
                    mask=neural.predict(weights,rgb,.5)
            pred=mask>0
            tp=int((pred & gt).sum());fp=int((pred & ~gt).sum());fn=int((~pred & gt).sum())
            row={'task':task,'tp':tp,'fp':fp,'fn':fn,'dice':2*tp/max(1,2*tp+fp+fn),'iou':tp/max(1,tp+fp+fn),
                 'precision':tp/max(1,tp+fp),'recall':tp/max(1,tp+fn),'used_for_training':task in trained_tasks}
            rows.append(row)
            Image.fromarray(mask).save(output/f'{name}_task_{task}_mask.png')
            print(name,json.dumps(row),flush=True)
        report['models'][name]={'all_original_validation':metrics(rows),
                               'clean_validation':metrics([r for r in rows if not r['used_for_training']]),'per_task':rows}
    (output/'report.json').write_text(json.dumps(report,indent=2))
    lines=['# U-Net 검증 결과','',f"현재 모델: {report['steps']} 스텝 · 임계값 0.5",'',
           '검증 기준은 초기 저장 마스크입니다. 학습과 이미지가 겹치는 태스크는 clean 집계에서 제외했습니다.',
           '초기 300스텝 모델은 기존 3장 검증으로 선택했으므로 완전히 독립된 테스트 결과는 아닙니다.',
           '동일 프로젝트 내 이미지 분리 결과이며 독립 시편 일반화 성능을 보장하지 않습니다.','',
           '| 범위 | 모델 | Dice | IoU | Precision | Recall |','|---|---|---:|---:|---:|---:|']
    for scope in ('all_original_validation','clean_validation'):
        for model in report['models']:
            m=report['models'][model][scope]
            lines.append(f"| {scope} ({m['tasks']}장) | {model} | {m['dice']:.4f} | {m['iou']:.4f} | {m['precision']:.4f} | {m['recall']:.4f} |")
    lines+=['',f"학습과 겹친 태스크: {report['contaminated_validation_tasks']}",f"겹치지 않는 태스크: {report['clean_validation_tasks']}",
            '',f"평가 체크포인트 SHA256: {report['checkpoint_sha256']}"]
    (output/'report.md').write_text('\n'.join(lines)+'\n')
    print('REPORT',output/'report.json',flush=True)
    print(json.dumps({name:{k:v for k,v in m.items() if k!='per_task'} for name,m in report['models'].items()}),flush=True)


if __name__=='__main__':main()
