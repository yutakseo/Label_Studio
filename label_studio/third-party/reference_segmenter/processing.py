"""Curved dark-line candidates, filtered by centerline length and thickness."""
import math
import uuid

import cv2
import numpy as np
from label_studio_sdk.converter.brush import mask2rle

MAX_PIXELS = 16_000_000
DEFAULTS = {"blur_size": 101, "adaptive_size": 51, "offset": 4, "min_contrast": 10,
            "close_size": 5, "min_area": 20, "min_path_length": 30,
            "min_elongation": 4.0, "max_width": 20, "edge_margin": 8}


def skeletonize(mask, max_iterations):
    """Morphological centerline approximation; direction-independent and CPU bounded."""
    current = mask.copy()
    skeleton = np.zeros_like(mask)
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    for _ in range(max_iterations):
        if not cv2.countNonZero(current):
            break
        eroded = cv2.erode(current, kernel, borderType=cv2.BORDER_CONSTANT, borderValue=0)
        opened = cv2.dilate(eroded, kernel)
        skeleton |= cv2.subtract(current, opened)
        current = eroded
    return skeleton, current


def detect(gray, options=None, bbox=None):
    p = {**DEFAULTS, **(options or {})}
    limits = {"blur_size": (3, 501), "adaptive_size": (3, 501), "offset": (0, 100),
              "min_contrast": (1, 255), "close_size": (1, 31), "max_width": (1, 200),
              "min_area": (1, MAX_PIXELS), "min_path_length": (1, 10000), "edge_margin": (0, 100)}
    for key, (low, high) in limits.items():
        if type(p[key]) is not int or not low <= p[key] <= high:
            raise ValueError(f"{key}: {low}~{high} 정수가 필요합니다.")
    if any(p[k] % 2 == 0 for k in ("blur_size", "adaptive_size", "close_size")):
        raise ValueError("배경 블러·적응형 창·틈 연결 크기는 홀수여야 합니다.")
    if (type(p["min_elongation"]) not in (int, float) or not math.isfinite(p["min_elongation"])
            or not 1 <= p["min_elongation"] <= 1000):
        raise ValueError("최소 길이/두께 비는 1~1000이어야 합니다.")
    if (not isinstance(gray, np.ndarray) or gray.dtype != np.uint8 or gray.ndim != 2
            or gray.size == 0 or gray.size > MAX_PIXELS):
        raise ValueError("최대 1600만 픽셀의 8비트 그레이스케일 이미지가 필요합니다.")
    height, width = gray.shape
    roi = np.ones(gray.shape, dtype=np.uint8) * 255
    if bbox is not None:
        if (not isinstance(bbox, list) or len(bbox) != 4 or any(type(v) is not int for v in bbox)
                or not (0 <= bbox[0] < bbox[2] <= width and 0 <= bbox[1] < bbox[3] <= height)):
            raise ValueError("검출 범위는 이미지 안의 정수 [x1,y1,x2,y2]여야 합니다.")
        roi[:] = 0
        roi[bbox[1]:bbox[3], bbox[0]:bbox[2]] = 255
    # Fill the specimen silhouette so dark internal lines remain eligible, while
    # black exterior padding and its border cannot become candidate lines.
    seed = (gray > 5).astype(np.uint8) * 255
    seed = cv2.morphologyEx(seed, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    contours, _ = cv2.findContours(seed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid = np.zeros_like(gray)
    if contours:
        cv2.drawContours(valid, [max(contours, key=cv2.contourArea)], -1, 255, cv2.FILLED)
    weights = valid.astype(np.float32) / 255
    kernel = (p["blur_size"], p["blur_size"])
    numerator = cv2.GaussianBlur(gray.astype(np.float32) * weights, kernel, 0)
    denominator = cv2.GaussianBlur(weights, kernel, 0)
    background = np.divide(numerator, denominator, out=np.zeros_like(numerator), where=denominator > 1e-6)
    difference = np.clip(background - gray.astype(np.float32), 0, 255).astype(np.uint8)
    difference[valid == 0] = 0
    if p["edge_margin"]:
        size = p["edge_margin"] * 2 + 1
        valid = cv2.erode(valid, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size)))
    allowed = (valid > 0) & (roi > 0)
    candidates = cv2.adaptiveThreshold(difference, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, p["adaptive_size"], -p["offset"])
    candidates[(difference < p["min_contrast"]) | ~allowed] = 0
    # A small round kernel closes short gaps in every direction without forcing
    # curves to run horizontally. Preserve the original width in the output.
    candidates = cv2.morphologyEx(candidates, cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (p["close_size"], p["close_size"])))
    candidates[~allowed] = 0
    count, components, stats, _ = cv2.connectedComponentsWithStats(candidates, connectivity=8)
    skeleton, thick_cores = skeletonize(candidates, p["max_width"] + 2)
    lengths = np.bincount(components[skeleton > 0], minlength=count)
    oversized = set(np.unique(components[thick_cores > 0]))
    keep = np.zeros(count, dtype=np.uint8)
    for index in range(1, count):
        area = stats[index, cv2.CC_STAT_AREA]
        length = int(lengths[index])
        thickness = area / max(length, 1)
        if (index not in oversized and area >= p["min_area"] and length >= p["min_path_length"]
                and thickness <= p["max_width"] and length / max(thickness, 1) >= p["min_elongation"]):
            keep[index] = 255
    mask = keep[components]
    return mask, background.clip(0, 255).astype(np.uint8), difference, {
        "components": int(np.count_nonzero(keep)), "pixels": int(np.count_nonzero(mask)),
        "candidates": int(count - 1)}


def brush_result(mask, from_name, to_name, label):
    if any(not isinstance(v, str) or not v.strip() or len(v) > 512 for v in (from_name, to_name, label)):
        raise ValueError("대상 이미지와 브러시 라벨을 선택하세요.")
    return [{"id": uuid.uuid4().hex[:10], "type": "brushlabels", "from_name": from_name,
             "to_name": to_name, "original_width": mask.shape[1], "original_height": mask.shape[0],
             "image_rotation": 0, "value": {"format": "rle", "brushlabels": [label], "rle": mask2rle(mask)}}]
