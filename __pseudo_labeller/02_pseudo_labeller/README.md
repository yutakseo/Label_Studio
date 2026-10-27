# Gaussian 차이 pseudo 마스크·YOLO polygon

## 처리

`GaussianDifferenceMaskMaker.create`는 원본을 GaussianBlur한 결과와의 int16 차이에서 절댓값 영상을 만들고 Otsu 또는 고정 임계값으로 이진화합니다. 컬러 입력은 채널별 차이를 평균한 뒤 절댓값을 사용합니다. 외곽 윤곽선 중 최소 면적을 통과한 영역 내부를 채워 최종 마스크를 만듭니다.

`YoloSegmentationExporter.create_labels`는 마스크 윤곽을 선택적으로 근사하고 이미지 크기로 정규화한 polygon 좌표를 클래스 ID와 함께 출력합니다. 결함 의미를 학습하지 않는 규칙 기반 후보입니다.

## 재사용 예

저장소 루트에서 실행하는 Python 코드 예입니다.

```python
import sys
from pathlib import Path
from importlib import import_module

sys.path.insert(0, str(Path("__pseudo_labeller").resolve()))
pseudo = import_module("02_pseudo_labeller")
config = pseudo.GaussianDifferenceConfig(
    input_root=Path("input_images"),
    mask_output_root=Path("generated_masks"),
    label_output_root=Path("generated_labels"),
    class_id=0, class_name="Exposure",
    gaussian_kernel_size=101, gaussian_sigma=10,
    mask_threshold=None, min_contour_area=0,
    contour_approximation_ratio=0,
)
summary = pseudo.PseudoLabelGenerator(config).run()
print(summary.saved_masks, summary.saved_regions, summary.failures)
```

입력 폴더를 먼저 준비합니다. `None` threshold는 Otsu이며 고정 threshold는 초과(>) 조건입니다. 설정 클래스 기본값은 kernel=21/sigma=0/min_area=10/approx=0.002로, 위 배치 실행 예와 다릅니다.

## 모듈과 산출물

`config.py`는 불변 dataclass와 값 검증, `processing.py`는 영상·polygon 처리, `image_io.py`는 한글 경로를 포함한 OpenCV 파일 I/O, `workflow.py`는 재귀 입력/출력과 실패 목록을 담당합니다. [CODE_MAP](CODE_MAP.md) 참고.

입력 상대 경로를 유지해 마스크와 `.txt` 라벨을 씁니다. `labelmap.txt`, `classes.txt`도 생성합니다. 빈 후보는 빈 txt가 될 수 있습니다. 현재 write_labelmap은 하나의 class_name을 기록하므로 여러 클래스 ID를 합칠 때 매핑을 따로 검증해야 합니다. 파일이 이미 있으면 덮어쓸 수 있습니다.

웹 확장 사본은 [pseudo_core](../../label_studio/third-party/gaussian_mask/pseudo_core/README.md)이며 동기화·픽셀 동등성 검증이 필요합니다.
