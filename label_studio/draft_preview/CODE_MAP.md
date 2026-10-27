# 코드 참조 · draft_preview

현재 소스에서 추출한 모듈·클래스·함수 목록입니다. 함수의 동작·사용 순서는 [README](README.md)를 참고하고, 실제 구현은 파일 링크에서 확인하세요. 테스트 파일은 검증 항목 탐색용입니다. 비공개 함수도 디버깅 경로를 찾을 수 있도록 포함했습니다.

## [__init__.py](__init__.py)

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [export_filter.py](export_filter.py)

Exclude comparison-only original masks from every serialized export.

- `patch(path)`

## [install.py](install.py)

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [mask_merge.py](mask_merge.py)

Union of selected saved brush masks, without changing their source results.

- `merge_masks(sources, from_name, to_name, label=None)`

## [merge_urls.py](merge_urls.py)

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [merge_views.py](merge_views.py)

### `class MergeAnnotationAPI(AnnotationsListAPI)`

Keep standard creation permissions and ownership; persist the tab title separately.

- `perform_create(self, serializer)`

- `script(request)`

- `preview(request)`

## [middleware.py](middleware.py)

### `class DraftPreviewMiddleware`

- `__init__(self, get_response)`
- `__call__(self, request)`

## [test_merge.py](test_merge.py)

- `region(mask, **changes)`

### `class MergeTests(unittest.TestCase)`

- `merge(self, sources)`
- `test_union_overlap_multiple_regions_and_source_preservation(self)`
- `test_preserve_labels_and_overlap(self)`
- `test_unrelated_targets_and_non_brush_regions_are_excluded(self)`
- `test_empty_masks_are_valid(self)`
- `test_dimensions_rotation_and_malformed_stream_are_rejected(self)`
- `test_source_count_and_missing_label(self)`

## [test_merge_http.py](test_merge_http.py)

### `class MergeHttpTests(unittest.TestCase)`

- `request(self, authenticated=True, csrf_bypass=True, data=None)`
- `test_union_preview_and_route(self)`
- `test_multilabel_preview(self)`
- `test_auth_csrf_and_invalid_input(self)`

## [test_user_tabs_api.py](test_user_tabs_api.py)

### `class UserTabTests(unittest.TestCase)`

- `test_user_save_updates_existing_and_drafts_attach_to_same_tab(self)`
- `test_all_authors_update_saved_time_and_export_latest_mask(self)`

## [user_isolation.py](user_isolation.py)

Keep each annotator's saves separate and retain mask revision snapshots.

- `isolate_update(view, request, args, kwargs, update)`

- `protect_delete(annotation, user)`

- `draft_annotation(task_id, annotation_id, user)`

- `archive_revision(sender, instance, **kwargs)`: Archive the persisted revision before any save or deletion, fail closed.

- `install_revision_history()`

- `regular_annotations(task, user)`: Named MERGE outputs remain separate from the annotator's working tab.

- `save_user_annotation(view, serializer, extra_args)`

- `latest_user_drafts(queryset, user)`: Retain draft revisions on disk/DB while exposing one current draft per tab.

## JavaScript와 브라우저 검증

- [merge_panel.js](merge_panel.js): 브라우저 UI·처리 코드 또는 편집기 주입 코드.
- [panel.js](panel.js): 브라우저 UI·처리 코드 또는 편집기 주입 코드.
- [test_merge_panel.cjs](test_merge_panel.cjs): Node 검증 코드.

패널은 서버가 제공하거나 HTML에 주입하고, tool/patch 코드는 공식 편집기 번들에 포함합니다. 실제 적용 방식은 상위 README와 Dockerfile을 확인하세요.
