"""Union of selected saved brush masks, without changing their source results."""
import uuid

import numpy as np
from label_studio_sdk.converter.brush import mask2rle

from mask_cleanup.processing import MAX_PIXELS, decode_checked


def merge_masks(sources, from_name, to_name, label):
    if not all(isinstance(v, str) and v for v in (from_name, to_name, label)):
        raise ValueError("대상 이미지와 브러시 라벨을 선택하세요.")
    if not isinstance(sources, list) or not 2 <= len(sources) <= 32:
        raise ValueError("합칠 마스크 탭을 2~32개 선택하세요.")
    shape = None
    union = None
    regions = 0
    work = 0
    for source in sources:
        if not isinstance(source, list) or len(source) > 500:
            raise ValueError("탭당 최대 500개 영역을 지원합니다.")
        matched = 0
        for item in source:
            if not isinstance(item, dict):
                raise ValueError("마스크 영역 형식이 잘못되었습니다.")
            value = item.get("value", {})
            if not isinstance(value, dict):
                raise ValueError("마스크 값 형식이 잘못되었습니다.")
            if (item.get("type") != "brushlabels" or item.get("from_name") != from_name
                    or item.get("to_name") != to_name or label not in value.get("brushlabels", [])):
                continue
            width, height = item.get("original_width"), item.get("original_height")
            if (type(width) is not int or type(height) is not int or min(width, height) < 1
                    or width * height > MAX_PIXELS):
                raise ValueError("이미지는 최대 1600만 픽셀까지 지원합니다.")
            if item.get("image_rotation", 0) != 0:
                raise ValueError("회전된 마스크는 지원하지 않습니다.")
            if value.get("format") != "rle":
                raise ValueError("RLE 브러시 마스크만 합칠 수 있습니다.")
            if shape is None:
                shape = (height, width)
                union = np.zeros(shape, dtype=bool)
            elif shape != (height, width):
                raise ValueError("서로 다른 크기의 마스크는 합칠 수 없습니다.")
            work += width * height
            if work > 256_000_000:
                raise ValueError("한 번에 처리할 영역이 너무 많습니다. 선택한 탭 수를 줄이세요.")
            rgba = decode_checked(value.get("rle"), width * height * 4).reshape(height, width, 4)
            union |= rgba[:, :, 3] > 0
            matched += 1
            regions += 1
        if not matched:
            raise ValueError("선택한 탭에 해당 이미지·라벨의 저장된 마스크가 없습니다.")
    mask = union.astype(np.uint8) * 255
    result = {"id": uuid.uuid4().hex[:10], "type": "brushlabels", "origin": "manual",
              "from_name": from_name, "to_name": to_name,
              "original_width": shape[1], "original_height": shape[0], "image_rotation": 0,
              "value": {"format": "rle", "brushlabels": [label], "rle": mask2rle(mask)}}
    return [result], mask, {"sources": len(sources), "regions": regions,
                            "pixels": int(np.count_nonzero(union))}
