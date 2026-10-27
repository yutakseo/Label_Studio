# 코드 참조 · tree_export

현재 소스에서 추출한 모듈·클래스·함수 목록입니다. 함수의 동작·사용 순서는 [README](README.md)를 참고하고, 실제 구현은 파일 링크에서 확인하세요. 테스트 파일은 검증 항목 탐색용입니다. 비공개 함수도 디버깅 경로를 찾을 수 있도록 포함했습니다.

## [__init__.py](__init__.py)

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [archive.py](archive.py)

- `source_path(url, upload_root)`

- `make_mask(results, width, height, from_name, to_name, label)`

- `write_archive(file, tasks, upload_root, field, from_name, to_name, label, project_id)`

## [test_archive.py](test_archive.py)

### `class Annotations`

- `__init__(self, annotation)`
- `filter(self, **kwargs)`
- `order_by(self, *args)`
- `first(self)`

### `class ExportTests(unittest.TestCase)`

- `result(self, pixels)`
- `test_union_and_empty(self)`
- `test_tree_and_manifest(self)`
- `test_dataset_name_without_date(self)`
- `test_nested_dataset_tree(self)`
- `test_rejects_traversal_and_remote(self)`
- `test_rejects_symlink_escape(self)`

## [views.py](views.py)

- `script(request)`

### `class TreeExportAPI(ExportAPI)`

Use the built-in export's project lookup and permissions.

- `get(self, request, *args, **kwargs)`

## JavaScript와 브라우저 검증

- [panel.js](panel.js): 브라우저 UI·처리 코드 또는 편집기 주입 코드.

패널은 서버가 제공하거나 HTML에 주입하고, tool/patch 코드는 공식 편집기 번들에 포함합니다. 실제 적용 방식은 상위 README와 Dockerfile을 확인하세요.
