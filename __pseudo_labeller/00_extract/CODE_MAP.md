# 코드 참조 · 00_extract

현재 소스에서 추출한 모듈·클래스·함수 목록입니다. 함수의 동작·사용 순서는 [README](README.md)를 참고하고, 실제 구현은 파일 링크에서 확인하세요. 테스트 파일은 검증 항목 탐색용입니다. 비공개 함수도 디버깅 경로를 찾을 수 있도록 포함했습니다.

## [extract_mono.py](extract_mono.py)

Extract mono images captured at one exposure while preserving the source tree.

### `class ExtractionConfig`

Paths and selection rules for one extraction run.

- `validate(self) -> None`: Raise an exception when the extraction configuration is unsafe.

### `class ExtractionResult`

Summary of copied files.


### `class MonoExtractor`

Copy matching mono images without changing relative paths or filenames.

- `__init__(self, config: ExtractionConfig) -> None`
- `selectPaths(self) -> list[Path]`: Return sorted images matching both exposure and mono constraints.
- `isTarget(self, path: Path) -> bool`: Return whether a path is a mono image at the configured exposure.
- `extract(self) -> ExtractionResult`: Copy selected images and preserve their paths relative to the source.
- `copyOne(self, source_path: Path) -> None`: Copy one source image with its metadata and relative directory tree.

- `normalizeName(name: str) -> str`: Normalize a name so macOS decomposed Hangul compares reliably.

- `findDataset(data_root: Path, dataset_name: str) -> Path`: Find a dataset by Unicode-normalized directory name.

- `parseArgs(arguments: Optional[Sequence[str]]=None) -> argparse.Namespace`: Parse command-line options.

- `createConfig(arguments: argparse.Namespace) -> ExtractionConfig`: Create a validated extraction configuration from CLI arguments.

- `main(arguments: Optional[Sequence[str]]=None) -> int`: Run extraction and return a process exit code.
