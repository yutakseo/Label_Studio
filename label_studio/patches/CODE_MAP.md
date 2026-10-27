# 코드 참조 · patches

현재 소스에서 추출한 모듈·클래스·함수 목록입니다. 함수의 동작·사용 순서는 [README](README.md)를 참고하고, 실제 구현은 파일 링크에서 확인하세요. 테스트 파일은 검증 항목 탐색용입니다. 비공개 함수도 디버깅 경로를 찾을 수 있도록 포함했습니다.

## [annotated_by.py](annotated_by.py)

Restore author-only attribution; editing/importing metadata is not authorship.

- `patch(source)`

## [annotation_author.py](annotation_author.py)

Do not identify imported annotations without a known author as Admin.

- `patch(source)`

## [annotation_ownership.py](annotation_ownership.py)

Assign an unowned imported annotation only after its labeling result changes.

- `patch(source)`

## [brush_coordinates.py](brush_coordinates.py)

Snap brush and eraser strokes to a 0.1 image-pixel grid.

- `patch(source)`

## [brush_grid.py](brush_grid.py)

Use square grid stamps for live drawing, redraw/hit testing, and export.

- `patch(source)`

## [brush_size.py](brush_size.py)

Allow brush and eraser sizes from 0.2 to 30 in half-pixel steps.

- `patch(source)`

## [latest_selection.py](latest_selection.py)

Select the latest saved mask after Data Manager finishes loading a task.

- `patch(source)`

## [mask_merge_tool.py](mask_merge_tool.py)

Register the merge action beside the native segmentation tools.

- `patch(source)`

## [pen_input.py](pen_input.py)

Route pen coordinates directly through the image editor's drawing handlers.

- `patch(source)`

## [tree_export_button.py](tree_export_button.py)

Show tree export on project pages even without a Settings navigation link.

- `patch(source)`

## [tree_export_compat.py](tree_export_compat.py)

Allow dataset names without dates and show export validation details.

- `patch(path, replacements)`

## [user_isolation.py](user_isolation.py)

Install per-user annotation saves, private drafts, and revision history.

- `replace_once(source, old, new)`

- `patch_api(source)`

- `patch_models(source)`

- `patch_middleware(source)`

- `install(root)`

## [user_tabs.py](user_tabs.py)

Fork another annotator's local working result only when Update is pressed.

- `patch(source)`

## JavaScript와 브라우저 검증

- [brush_grid.js](brush_grid.js): 브라우저 UI·처리 코드 또는 편집기 주입 코드.
- [mask_merge_tool.js](mask_merge_tool.js): 브라우저 UI·처리 코드 또는 편집기 주입 코드.
- [pen_input.js](pen_input.js): 브라우저 UI·처리 코드 또는 편집기 주입 코드.
- [user_tabs.js](user_tabs.js): 브라우저 UI·처리 코드 또는 편집기 주입 코드.
- [test_latest_selection.cjs](test_latest_selection.cjs): Node 검증 코드.
- [test_pen_input.cjs](test_pen_input.cjs): Node 검증 코드.
- [test_user_tabs.cjs](test_user_tabs.cjs): Node 검증 코드.

패널은 서버가 제공하거나 HTML에 주입하고, tool/patch 코드는 공식 편집기 번들에 포함합니다. 실제 적용 방식은 상위 README와 Dockerfile을 확인하세요.
