# 코드 참조 · 03_yolo_formatting

현재 소스에서 추출한 모듈·클래스·함수 목록입니다. 함수의 동작·사용 순서는 [README](README.md)를 참고하고, 실제 구현은 파일 링크에서 확인하세요. 테스트 파일은 검증 항목 탐색용입니다. 비공개 함수도 디버깅 경로를 찾을 수 있도록 포함했습니다.

## [__init__.py](__init__.py)

Dataset formatting utilities.

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [yolo_packaging.py](yolo_packaging.py)

Create Roboflow-compatible YOLO Segmentation ZIP archives.

### `class YoloPackagingConfig`

Locations and file types used when packaging a YOLO dataset.

- `validate(self) -> None`
- `find_labelmap(self) -> Path`: Return the preferred available class-ID-to-name mapping file.
- `classNames(self) -> tuple[str, ...]`: Return non-empty class names ordered by their zero-based IDs.

### `class PackagingResult`

Summary of a completed ZIP packaging operation.


### `class RoboflowYoloPackager`

Package images and polygon labels as a standard YOLO dataset ZIP.

- `__init__(self, config: YoloPackagingConfig) -> None`
- `image_paths(self) -> list[Path]`
- `label_path_for(self, image_path: Path) -> Path`: Map an image path to its label path, preserving the image tree.
- `package(self) -> PackagingResult`: Write ``data.yaml`` and flattened ``train/images`` and ``train/labels``.
- `dataYaml(self) -> str`: Create the class mapping required for YOLO format detection.
- `validateNames(image_paths: list[Path]) -> None`: Reject names that would collide after flattening the source tree.
- `duplicateNames(names: list[str]) -> set[str]`: Return values that occur more than once.
- `_missing_labels_message(missing_labels: list[Path]) -> str`
