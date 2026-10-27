# 코드 참조 · 02_pseudo_labeller

현재 소스에서 추출한 모듈·클래스·함수 목록입니다. 함수의 동작·사용 순서는 [README](README.md)를 참고하고, 실제 구현은 파일 링크에서 확인하세요. 테스트 파일은 검증 항목 탐색용입니다. 비공개 함수도 디버깅 경로를 찾을 수 있도록 포함했습니다.

## [__init__.py](__init__.py)

Gaussian-difference pseudo-label generation package.

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [config.py](config.py)

Configuration models for pseudo-label generation.

### `class GaussianDifferenceConfig`

All settings needed to generate masks and YOLO segmentation labels.

- `validate(self) -> None`: Raise a helpful exception when a configuration value is invalid.

## [image_io.py](image_io.py)

OpenCV image I/O that supports non-ASCII Windows paths.

### `class ImageRepository`

Read and write images without relying on OpenCV's path encoding support.

- `read(path: Path) -> np.ndarray | None`
- `write(path: Path, image: np.ndarray) -> bool`

## [processing.py](processing.py)

Gaussian-difference mask creation and YOLO polygon conversion.

### `class GaussianDifferenceMaskMaker`

Create filled binary regions from local Gaussian-difference responses.

- `__init__(self, config: GaussianDifferenceConfig) -> None`
- `create(self, image: np.ndarray) -> np.ndarray`: Return a binary mask whose retained external contours are filled.
- `fill_regions(self, mask: np.ndarray) -> np.ndarray`: Fill retained contours, turning edge responses into solid regions.

### `class YoloSegmentationExporter`

Convert binary mask regions to normalized YOLO segmentation records.

- `__init__(self, config: GaussianDifferenceConfig) -> None`
- `create_labels(self, mask: np.ndarray) -> list[str]`

## [workflow.py](workflow.py)

Batch orchestration for pseudo-mask and YOLO-label generation.

### `class BatchResult`


### `class PseudoLabelGenerator`

Generate pseudo masks and matching YOLO segmentation files for a tree.

- `__init__(self, config: GaussianDifferenceConfig, image_repository: ImageRepository | None=None) -> None`
- `input_paths(self) -> list[Path]`
- `write_labelmap(self) -> None`
- `run(self) -> BatchResult`
- `_process_one(self, input_path: Path, result: BatchResult) -> None`
