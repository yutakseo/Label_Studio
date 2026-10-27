# 코드 참조 · u_net_labeller

현재 소스에서 추출한 모듈·클래스·함수 목록입니다. 함수의 동작·사용 순서는 [README](README.md)를 참고하고, 실제 구현은 파일 링크에서 확인하세요. 테스트 파일은 검증 항목 탐색용입니다. 비공개 함수도 디버깅 경로를 찾을 수 있도록 포함했습니다.

## [__init__.py](__init__.py)

Full-resolution U-Net pseudo labeling.

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [install.py](install.py)

Register alongside existing extensions, preserving their routes and scripts.

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [interface.py](interface.py)

Overlapping patch inference with weighted probability blending at source resolution.

- `resolve_device(device='auto')`

- `load_model(weights=None, model_file=None, device='auto')`: The factory must recreate the training model, including non-weight settings.

- `specimen_input(pixels)`: Exclude only exact-zero regions connected to the image border.

- `predict(image, model, *, device=None, batch_size=4, threshold=0.5, remove_black_padding=True)`

- `brush_results(mask, from_name, to_name, label)`

- `main()`

## [model.py](model.py)

Training-compatible grayscale U-Net for inference (no training dependencies).

### `class DoubleConv(nn.Sequential)`

- `__init__(self, incoming, outgoing)`

### `class UNet(nn.Module)`

- `__init__(self, base_channels=32)`
- `forward(self, x)`

- `build_model(checkpoint)`

## [test_interface.py](test_interface.py)

### `class PixelModel(torch.nn.Module)`

- `forward(self, x)`

### `class PatchTests(unittest.TestCase)`

- `test_full_resolution_positions_and_batch_tail(self)`
- `test_padded_edges_and_small_image(self)`
- `test_patch_edge_artifacts_are_downweighted(self)`
- `test_specimen_restoration_and_internal_black_pixels(self)`
- `test_angled_specimen_has_no_black_context(self)`
- `test_invalid_parameters(self)`
- `test_wrong_output_shape(self)`

### `class GpuTests(unittest.TestCase)`

- `test_cuda_patch_reconstruction_matches_cpu(self)`

## [urls.py](urls.py)

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [views.py](views.py)

- `runtime()`

- `script(request)`

- `preview(request)`

## JavaScript와 브라우저 검증

- [panel.js](panel.js): 브라우저 UI·처리 코드 또는 편집기 주입 코드.

패널은 서버가 제공하거나 HTML에 주입하고, tool/patch 코드는 공식 편집기 번들에 포함합니다. 실제 적용 방식은 상위 README와 Dockerfile을 확인하세요.
