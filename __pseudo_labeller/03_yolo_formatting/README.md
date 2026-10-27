# Roboflow용 YOLO Segmentation ZIP

`YoloPackagingConfig`와 `RoboflowYoloPackager`가 이미지·polygon txt·클래스 매핑을 하나의 ZIP으로 묶습니다. [CODE_MAP](CODE_MAP.md)에 전체 메서드가 있습니다.

```python
import sys
from pathlib import Path
from importlib import import_module
sys.path.insert(0, str(Path("__pseudo_labeller").resolve()))
yolo = import_module("03_yolo_formatting")
config = yolo.YoloPackagingConfig(
    image_root=Path("input_images"),
    label_root=Path("generated_labels"),
    output_zip=Path("outputs/dataset.zip"),
)
result = yolo.RoboflowYoloPackager(config).package()
print(result.image_count, result.label_count)
```

입력 이미지 상대 경로와 라벨 상대 경로가 같고 라벨 확장자만 `.txt`여야 합니다. class mapping은 `labelmap.txt`, 없으면 `classes.txt`에서 읽고 줄 순서를 0부터 클래스 ID로 사용합니다.

ZIP은 `data.yaml`, `train/images`, `train/labels`, 빈 `valid/images`, `valid/labels`를 포함합니다. **학습/검증 split을 자동 생성하지 않습니다.** 출력 내부는 파일명을 평탄화하므로 서로 다른 입력 폴더의 동일 파일명·동일 txt 이름은 대소문자까지 정규화해 충돌을 거부합니다. 모든 이미지의 라벨 존재도 먼저 확인합니다. 이미지가 없으면 ZIP을 만들지 않고 0개 요약을 반환합니다.

실행기 `../yolo_formatting.py`의 CONFIG를 바꿔 사용할 수 있습니다. 기존 output ZIP을 덮어쓸 수 있으므로 출력 경로를 확인하세요. Label Studio 폴더 구조 유지 Export와는 다른 포맷입니다.
