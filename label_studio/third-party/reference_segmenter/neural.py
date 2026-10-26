"""Persistent correction pairs and supervised fine-tuning of the installed U-Net."""
import json
import os
import threading
import shutil
from pathlib import Path

import cv2
import numpy as np
import torch
from torch.nn import functional as F
from PIL import Image
from .model import ReferenceUNet
from u_net_labeller.interface import specimen_input

GPU_LOCK = threading.Lock()


def device():
    return torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')


def load(path):
    checkpoint = torch.load(path, map_location='cpu', weights_only=True)
    model = ReferenceUNet(checkpoint['base_channels'])
    model.load_state_dict(checkpoint['model_state_dict'])
    return model.to(device()), checkpoint


def initial_weights():
    return Path(__file__).resolve().parents[1] / 'u_net_labeller/best.pt'


def save_pair(directory, rgb, mask, name):
    if rgb.shape[:2] != mask.shape or min(mask.shape) < 16:
        raise ValueError('학습 이미지와 마스크 크기가 일치해야 합니다.')
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    temporary = directory / (name + '.tmp.npz')
    np.savez_compressed(temporary, image=np.asarray(rgb, dtype=np.uint8), mask=np.asarray(mask > 0, dtype=np.uint8))
    os.replace(temporary, directory / (name + '.npz'))


def read_pairs(directory):
    pairs=[]
    for path in sorted(Path(directory).glob('*.npz')):
        with np.load(path, allow_pickle=False) as data:
            pairs.append((data['image'], data['mask']))
    if not pairs:
        raise ValueError('저장된 이미지·마스크 학습 쌍이 없습니다.')
    return pairs


def train(checkpoint_path, pairs, steps=40, batch_size=8, seed=42, callback=None, start_from_scratch=False, learning_rate=1e-4, validation_pairs=None, validation_interval=100):
    """Warm-start from current checkpoint, retaining full spatial masks."""
    torch.set_num_threads(4)
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    checkpoint_path = Path(checkpoint_path)
    if not pairs or any(rgb.shape != (64,64,3) or mask.shape != (64,64) for rgb,mask in pairs):
        raise ValueError('학습에는 직접 수정한 64×64 이미지·마스크 패치만 사용할 수 있습니다.')
    if start_from_scratch or not checkpoint_path.exists():
        model=ReferenceUNet(32).to(device())
        old={'base_channels':32, 'steps':0, 'initialization':'random'}
    else:
        model, old = load(checkpoint_path)
        if old.get('training_scope') != 'correction_patches_only':
            raise ValueError('전체 이미지로 학습한 모델입니다. 패치 전용 모델로 초기화해야 합니다.')
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    gray_pairs = [(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY), mask) for rgb, mask in pairs]
    losses=[]
    best_score=-1.;best_state=None;best_step=None;history=[]
    for step in range(steps):
        xs, ys = [], []
        for _ in range(batch_size):
            image,mask=gray_pairs[int(rng.integers(len(gray_pairs)))]
            a=image;b=mask
            k=int(rng.integers(4));a=np.rot90(a,k);b=np.rot90(b,k)
            if rng.random()<.5:a=np.fliplr(a);b=np.fliplr(b)
            xs.append(a.copy());ys.append(b.copy())
        inputs=torch.from_numpy(np.stack(xs)[:,None].astype(np.float32)/255).to(device())
        targets=torch.from_numpy(np.stack(ys)[:,None].astype(np.float32)).to(device())
        optimizer.zero_grad(set_to_none=True)
        logits=model(inputs)
        probability=logits.sigmoid()
        dice=1-((2*(probability*targets).sum((1,2,3))+1)/(probability.sum((1,2,3))+targets.sum((1,2,3))+1)).mean()
        loss=.5*F.binary_cross_entropy_with_logits(logits,targets)+.5*dice
        if not torch.isfinite(loss):raise ValueError('학습 손실이 유효하지 않습니다.')
        loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1);optimizer.step()
        losses.append(float(loss.detach()))
        if callback and (step+1)%10==0:callback(step+1,losses[-1])
        if validation_pairs and ((step+1)%validation_interval==0 or step+1==steps):
            model.eval();tp=fp=fn=0
            for rgb,mask in validation_pairs:
                pred=predict_tiled(model,rgb,.5)>0;truth=mask>0
                tp+=int((pred&truth).sum());fp+=int((pred&~truth).sum());fn+=int((~pred&truth).sum())
            score=2*tp/max(1,2*tp+fp+fn)
            history.append({'step':step+1,'validation_tiled_dice':score})
            if score>best_score:
                best_score=score;best_step=step+1
                best_state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
            if callback:callback(step+1,{'validation_tiled_dice':score,'best_step':best_step})
            model.train()
    if best_state is not None:model.load_state_dict(best_state)
    checkpoint={'architecture':'grayscale_unet','base_channels':old['base_channels'],
                'normalization':'uint8 / 255','model_state_dict':model.cpu().state_dict(),
                'threshold':.5,'steps':old.get('steps',0)+steps,'pairs':len(pairs),
                'parameters':sum(p.numel() for p in model.parameters()),'loss':float(np.mean(losses[-10:])),
                'initialization':old.get('initialization','pretrained'),
                'selected_step':best_step if best_step is not None else old.get('steps',0)+steps,
                'validation_history':history, 'training_scope':'correction_patches_only', 'patch_size':64,
                'inference_stride':32, 'validation_mode':'tiled_full_image'}

    checkpoint_path.parent.mkdir(parents=True,exist_ok=True)
    temporary=checkpoint_path.with_suffix('.tmp.pt');torch.save(checkpoint,temporary)
    if checkpoint_path.exists():
        backup=checkpoint_path.with_suffix('.previous.pt')
        backup_tmp=checkpoint_path.with_suffix('.previous.tmp.pt')
        shutil.copyfile(checkpoint_path,backup_tmp);os.replace(backup_tmp,backup)
    os.replace(temporary,checkpoint_path)
    return {k:v for k,v in checkpoint.items() if k!='model_state_dict'}


def predict_tiled(model,rgb,threshold=.5,batch_size=32):
    """64px patches, 32px stride, positive Hann blending; never resize the source."""
    if not np.isfinite(threshold) or not .01 <= threshold <= .99:
        raise ValueError('임계값은 0.01~0.99 범위입니다.')
    if type(batch_size) is not int or not 1 <= batch_size <= 128:
        raise ValueError('배치 크기는 1~128이어야 합니다.')
    gray=cv2.cvtColor(np.asarray(rgb,dtype=np.uint8),cv2.COLOR_RGB2GRAY).astype(np.float32)/255
    shape=gray.shape
    prepared=specimen_input(gray)
    if prepared is None:return np.zeros(shape,np.uint8)
    image,valid,(y1,y2,x1,x2)=prepared
    h,w=image.shape;margin=32;size=64
    padded=np.pad(image,((margin,margin),(margin,margin)),mode='reflect')
    ph,pw=padded.shape
    def starts(length):
        values=list(range(0,length-size+1,32))
        if values[-1]!=length-size:values.append(length-size)
        return values
    coordinates=[(y,x) for y in starts(ph) for x in starts(pw)]
    axis=np.hanning(size+2)[1:-1].astype(np.float32);weights=axis[:,None]*axis[None,:]
    total=np.zeros((ph,pw),np.float32);normalizer=np.zeros_like(total)
    model.eval();model_device=next(model.parameters(),torch.empty(0,device=device())).device
    with torch.inference_mode():
        for offset in range(0,len(coordinates),batch_size):
            positions=coordinates[offset:offset+batch_size]
            inputs=torch.from_numpy(np.stack([padded[y:y+size,x:x+size] for y,x in positions])[:,None]).to(model_device)
            logits=model(inputs)
            if logits.shape!=inputs.shape or not torch.isfinite(logits).all():
                raise ValueError('모델 출력은 유효한 [N,1,64,64] logits이어야 합니다.')
            outputs=logits.sigmoid().cpu().numpy()[:,0]
            for (y,x),probability in zip(positions,outputs):
                total[y:y+size,x:x+size]+=probability*weights
                normalizer[y:y+size,x:x+size]+=weights
    probabilities=total[margin:margin+h,margin:margin+w]/normalizer[margin:margin+h,margin:margin+w]
    crop=(probabilities>=threshold).astype(np.uint8)*255
    crop[~valid]=0
    result=np.zeros(shape,np.uint8);result[y1:y2,x1:x2]=crop
    return result


def predict(checkpoint_path,rgb,threshold=.5):
    model,metadata=load(checkpoint_path)
    if metadata.get('training_scope')!='correction_patches_only':
        raise ValueError('패치만으로 학습된 체크포인트가 필요합니다.')
    return predict_tiled(model,rgb,threshold)
