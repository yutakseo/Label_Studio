# 코드 참조 · reference_segmenter

현재 소스에서 추출한 모듈·클래스·함수 목록입니다. 함수의 동작·사용 순서는 [README](README.md)를 참고하고, 실제 구현은 파일 링크에서 확인하세요. 테스트 파일은 검증 항목 탐색용입니다. 비공개 함수도 디버깅 경로를 찾을 수 있도록 포함했습니다.

## [__init__.py](__init__.py)

Curved dark-line masking extension for Label Studio.

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [bootstrap.py](bootstrap.py)

Train from the latest saved masks; task-disjoint validation and prediction publishing.

- `main()`

## [install.py](install.py)

Enable the extension's panel injection after settings are initialized.

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [learning.py](learning.py)

Incremental supervised foreground/background prototypes; no pretrained weights.

- `features(rgb)`

- `update(state, rgb, mask)`

- `predict(state, rgb, threshold=0.5)`

## [middleware.py](middleware.py)

### `class PanelMiddleware`

- `__init__(self, get_response)`
- `__call__(self, request)`

## [model.py](model.py)

Reference segmentation has a fixed 64x64 input/output contract.

### `class ReferenceUNet(UNet)`

Keep existing state-dict keys while rejecting all other spatial sizes.

- `forward(self, x)`

## [neural.py](neural.py)

Persistent correction pairs and supervised fine-tuning of the installed U-Net.

- `device()`

- `load(path)`

- `initial_weights()`

- `save_pair(directory, rgb, mask, name)`

- `read_pairs(directory)`

- `train(checkpoint_path, pairs, steps=40, batch_size=8, seed=42, callback=None, start_from_scratch=False, learning_rate=0.0001, validation_pairs=None, validation_interval=100)`: Warm-start from current checkpoint, retaining full spatial masks.

- `predict_tiled(model, rgb, threshold=0.5, batch_size=32)`: 64px patches, 32px stride, positive Hann blending; never resize the source.

- `predict(checkpoint_path, rgb, threshold=0.5)`

## [patch_editor.py](patch_editor.py)

Version-checked native dark-line action registration.

- `patch(source)`

## [processing.py](processing.py)

Curved dark-line candidates, filtered by centerline length and thickness.

- `skeletonize(mask, max_iterations)`: Morphological centerline approximation; direction-independent and CPU bounded.

- `detect(gray, options=None, bbox=None)`

- `brush_result(mask, from_name, to_name, label)`

## [retrain.py](retrain.py)

Discard active learned weights, retrain saved correction patches only from random initialization.

- `main()`

## [storage.py](storage.py)

Project-shared models, with atomic adoption of existing personal models.

- `model_directory(base, project_id, key)`

## [targets.py](targets.py)

Stable class identities shared by training and prediction storage.

- `model_key(target)`

- `configured_targets(project)`

- `validate_target(project, target)`

- `prediction_version(target)`

- `result_target(region)`

## [test_http.py](test_http.py)

### `class DarkLineHttpTests(unittest.TestCase)`

- `request(self, authenticated=True, csrf=True, options=None)`
- `test_panel_cache_invalidation(self)`
- `test_preview_and_route(self)`
- `test_auth_csrf_and_invalid_parameters(self)`

### `class LearningHttpTests(unittest.TestCase)`

- `test_train_predict_status_and_access(self)`

## [test_learning.py](test_learning.py)

### `class LearningTests(unittest.TestCase)`

- `test_roundtrip_and_incremental_learning(self)`
- `test_invalid_reference_and_untrained_model(self)`

## [test_multiclass_browser.py](test_multiclass_browser.py)

Offline browser flow: class registration, separate training, preview and save.

- `run()`

## [test_neural.py](test_neural.py)

### `class NeuralTests(unittest.TestCase)`

- `test_correction_training_checkpoint_and_inference(self)`
- `test_random_initialization_does_not_load_existing_weights(self)`
- `test_full_images_cannot_enter_training(self)`
- `test_64_pixel_tiles_reconstruct_odd_and_small_images_without_seams(self)`
- `test_reference_model_rejects_256_input_before_convolution(self)`

## [test_prediction_save.py](test_prediction_save.py)

DB checks always roll back; predictions are isolated by brush/image/class.

### `class PredictionSaveTests(unittest.TestCase)`

- `test_class_save_retry_legacy_adoption_and_access(self)`

## [test_processing.py](test_processing.py)

### `class DarkLineTests(unittest.TestCase)`

- `image(self)`
- `test_dark_direction_gap_connection_and_shape_filters(self)`
- `test_tight_winding_curve_and_rotation_are_preserved(self)`
- `test_long_vertical_and_diagonal_curves_are_eligible(self)`
- `test_roi_clips_output_and_preserves_original_resolution(self)`
- `test_black_padding_and_specimen_edges_are_not_lines(self)`
- `test_constant_and_black_images_are_empty(self)`
- `test_invalid_options_and_regions(self)`

## [test_storage.py](test_storage.py)

### `class SharedStorageTests(unittest.TestCase)`

- `test_adopts_existing_model_once_and_preserves_original(self)`

## [urls.py](urls.py)

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [validate.py](validate.py)

Evaluate immutable checkpoint snapshots against saved validation pairs; no DB writes.

- `metrics(rows)`

- `main()`

## [views.py](views.py)

### `class BlackLinePredictionAPI(PredictionAPI)`

Any project viewer may delete this generated candidate, regardless of creator.

- `get_queryset(self)`

### `class ReferencePredictionSaveAPI(PredictionAPI)`

Serialize saves on the task, preserving one stable prediction per class.

- `create(self, request, *args, **kwargs)`

- `thumbnail(image)`

- `script(request)`

- `preview(request)`

- `learn(request)`: Share model weights within an accessible project; keep annotation access personal.

## JavaScript와 브라우저 검증

- [panel.js](panel.js): 브라우저 UI·처리 코드 또는 편집기 주입 코드.
- [patch_editor.js](patch_editor.js): 브라우저 UI·처리 코드 또는 편집기 주입 코드.
- [test_panel.cjs](test_panel.cjs): Node 검증 코드.

패널은 서버가 제공하거나 HTML에 주입하고, tool/patch 코드는 공식 편집기 번들에 포함합니다. 실제 적용 방식은 상위 README와 Dockerfile을 확인하세요.
