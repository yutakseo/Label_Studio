# 코드 참조 · mask_cleanup

현재 소스에서 추출한 모듈·클래스·함수 목록입니다. 함수의 동작·사용 순서는 [README](README.md)를 참고하고, 실제 구현은 파일 링크에서 확인하세요. 테스트 파일은 검증 항목 탐색용입니다. 비공개 함수도 디버깅 경로를 찾을 수 있도록 포함했습니다.

## [__init__.py](__init__.py)

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [install.py](install.py)

Enable the extension after Label Studio's settings initialization (including Sentry).

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [middleware.py](middleware.py)

### `class PanelMiddleware`

- `__init__(self, get_response)`
- `__call__(self, request)`

## [patch_editor.py](patch_editor.py)

Version-checked editor patch. Source fragments stay readable and tracked here.

- `patch_hotkeys(source)`

- `patch_gaussian(source)`

- `patch(source)`

## [processing.py](processing.py)

- `decode_checked(rle, expected)`: Bound decoding by image size and reject truncated/overflowing brush streams.

- `clean(image, results, threshold, label, to_name)`

## [test_http.py](test_http.py)

### `class HttpTests(unittest.TestCase)`

- `request(self, authenticated=True, csrf_bypass=True)`
- `test_preview_json(self)`
- `test_authentication_and_csrf(self)`
- `test_routes_and_html_injection(self)`

## [test_middleware.py](test_middleware.py)

### `class ExportMenuInjectionTests(unittest.TestCase)`

- `test_project_list_and_direct_project_entry_load_export_extension(self)`
- `test_login_api_and_unsuccessful_responses_are_unchanged(self)`

## [test_processing.py](test_processing.py)

### `class CleanupTests(unittest.TestCase)`

- `setUp(self)`
- `test_threshold_and_preservation(self)`
- `test_empty_region_and_relation_removed(self)`
- `test_dimension_mismatch(self)`
- `test_invalid_and_truncated_rle(self)`
- `test_threshold_bounds_and_zero(self)`

## [urls.py](urls.py)

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [views.py](views.py)

- `script(request)`

- `preview(request)`

## JavaScript와 브라우저 검증

- [panel.js](panel.js): 브라우저 UI·처리 코드 또는 편집기 주입 코드.
- [similar_erase.js](similar_erase.js): 브라우저 UI·처리 코드 또는 편집기 주입 코드.
- [similar_tool.js](similar_tool.js): 브라우저 UI·처리 코드 또는 편집기 주입 코드.
- [test_hotkeys.cjs](test_hotkeys.cjs): Node 검증 코드.
- [test_similar_erase.cjs](test_similar_erase.cjs): Node 검증 코드.

패널은 서버가 제공하거나 HTML에 주입하고, tool/patch 코드는 공식 편집기 번들에 포함합니다. 실제 적용 방식은 상위 README와 Dockerfile을 확인하세요.
