"""Incremental supervised foreground/background prototypes; no pretrained weights."""
import cv2
import numpy as np


def features(rgb):
    rgb = np.asarray(rgb, dtype=np.uint8)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
    mean = cv2.GaussianBlur(gray, (7, 7), 0)
    variance = np.maximum(cv2.GaussianBlur(gray * gray, (7, 7), 0) - mean * mean, 0)
    return np.dstack((rgb.astype(np.float32) / 255, gray - mean, mean, np.sqrt(variance)))


def update(state, rgb, mask):
    if rgb.shape != (64, 64, 3) or mask.shape != (64, 64):
        raise ValueError('참고 패치와 마스크는 64×64이어야 합니다.')
    x = features(rgb)
    if not np.any(mask) or np.all(mask):
        raise ValueError('패치에는 대상과 배경 픽셀이 모두 필요합니다.')
    state = dict(state or {})
    for label in (0, 1):
        values = x[(mask > 0) == bool(label)].astype(np.float64)
        old = state.get(str(label), {'n': 0, 'sum': [0.] * 6, 'square': [0.] * 6})
        state[str(label)] = {'n': old['n'] + len(values),
                            'sum': (np.array(old['sum']) + values.sum(0)).tolist(),
                            'square': (np.array(old['square']) + (values * values).sum(0)).tolist()}
    state['round'] = state.get('round', 0) + 1
    return state


def predict(state, rgb, threshold=.5):
    if not state or not all(str(c) in state for c in (0, 1)):
        raise ValueError('먼저 참고 마스크를 학습하세요.')
    if not np.isfinite(threshold) or not 0.01 <= threshold <= .99:
        raise ValueError('임계값은 0.01~0.99 범위입니다.')
    h, w = rgb.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    # Halo keeps local features identical across stripe boundaries; bounds peak memory.
    for y in range(0, h, 128):
        lo, hi = max(0, y - 3), min(h, y + 131)
        x = features(rgb[lo:hi])[y-lo:min(y+128,h)-lo]
        scores = []
        for c in (0, 1):
            data = state[str(c)]
            mean = np.array(data['sum']) / data['n']
            var = np.maximum(np.array(data['square']) / data['n'] - mean * mean, .0025)
            scores.append(-.5 * (((x - mean) ** 2 / var) + np.log(var)).sum(2))
        logit = scores[1] - scores[0]
        mask[y:y+len(x)] = (logit >= np.log(threshold / (1-threshold))).astype(np.uint8) * 255
    return mask
