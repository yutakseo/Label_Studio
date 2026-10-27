# 코드 참조 · gaussian_mask

현재 소스에서 추출한 모듈·클래스·함수 목록입니다. 함수의 동작·사용 순서는 [README](README.md)를 참고하고, 실제 구현은 파일 링크에서 확인하세요. 테스트 파일은 검증 항목 탐색용입니다. 비공개 함수도 디버깅 경로를 찾을 수 있도록 포함했습니다.

## [__init__.py](__init__.py)

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [processing.py](processing.py)

Label Studio adapter for the unchanged pseudo_labeller mask maker.

- `generate(image, kernel_size, sigma, threshold, min_area, from_name, to_name, label, bbox=None)`

## [test_http.py](test_http.py)

### `class GaussianHttpTests(BaseTests)`

- `request(self, authenticated=True, csrf_bypass=True)`
- `test_preview_json(self)`
- `test_authentication_and_csrf(self)`
- `test_routes_and_html_injection(self)`
- `test_invalid_parameters(self)`

## [test_processing.py](test_processing.py)

### `class GaussianTests(unittest.TestCase)`

- `run_filter(self, array, threshold=None, kernel=101, sigma=10, area=0)`
- `test_uniform_image_has_no_mask(self)`
- `test_fill_holes_and_roundtrip(self)`
- `test_area_filter_and_fixed_threshold_equality(self)`
- `test_validation(self)`
- `test_matches_original_source_and_masks(self)`
- `test_bbox_matches_crop_and_does_not_leak(self)`
- `test_empty_bbox_result_and_invalid_boxes(self)`

## [urls.py](urls.py)

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [views.py](views.py)

- `script(request)`

- `thumbnail(image)`

- `preview(request)`

## JavaScript와 브라우저 검증

- [panel.js](panel.js): 브라우저 UI·처리 코드 또는 편집기 주입 코드.
- [tool.js](tool.js): 브라우저 UI·처리 코드 또는 편집기 주입 코드.
- [test_roi_apply.cjs](test_roi_apply.cjs): Node 검증 코드.

패널은 서버가 제공하거나 HTML에 주입하고, tool/patch 코드는 공식 편집기 번들에 포함합니다. 실제 적용 방식은 상위 README와 Dockerfile을 확인하세요.
