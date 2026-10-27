# 코드 참조 · __pseudo_labeller

현재 소스에서 추출한 모듈·클래스·함수 목록입니다. 함수의 동작·사용 순서는 [README](README.md)를 참고하고, 실제 구현은 파일 링크에서 확인하세요. 테스트 파일은 검증 항목 탐색용입니다. 비공개 함수도 디버깅 경로를 찾을 수 있도록 포함했습니다.

## [gaussian_batch_processor.py](gaussian_batch_processor.py)

Create pseudo-segmentation masks and YOLO/Roboflow labels.

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [label_studio_formatting.py](label_studio_formatting.py)

Build a tree-preserving, pre-annotated Label Studio segmentation dataset.

- `class_names() -> list[str]`: Read the zero-based YOLO class map.

- `_bits_to_bytes(bits: str) -> list[int]`

- `encode_label_studio_rle(mask: np.ndarray) -> list[int]`: Encode a binary mask using Label Studio's RGBA RLE representation.

- `brush_result(mask_path: Path, class_name: str) -> dict[str, object]`: Convert one binary PNG mask to a single editable Label Studio brush mask.

- `build_dataset() -> tuple[int, int]`: Copy tree-preserved images and masks, then create editable brush tasks.

## [yolo_formatting.py](yolo_formatting.py)

Package images and YOLO Segmentation labels for Roboflow upload.

- `main() -> int`: Create the upload archive and return a process exit code.
