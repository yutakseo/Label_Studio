# 코드 참조 · 01_crop

현재 소스에서 추출한 모듈·클래스·함수 목록입니다. 함수의 동작·사용 순서는 [README](README.md)를 참고하고, 실제 구현은 파일 링크에서 확인하세요. 테스트 파일은 검증 항목 탐색용입니다. 비공개 함수도 디버깅 경로를 찾을 수 있도록 포함했습니다.

## [__init__.py](__init__.py)

ROI detection, quality assessment, geometry, and masked-image export.

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [auto_roi_group.py](auto_roi_group.py)

Group-level ROI candidates, continuous scoring, and fallback exports.

- `normalize_image(image: np.ndarray, size: int) -> np.ndarray`

- `analysis_args(args, original_shape: tuple, shape: tuple)`

- `frame_features(image: np.ndarray, args, modes=('std', 'fft')) -> dict`

- `fuse_features(features: list[dict]) -> dict`

- `columns_for(features: dict, mode: str, args, coarse: list | None=None) -> list`

- `soft_fit(points: list, width: int, args) -> dict`

- `make_candidate(top: dict, bottom: dict, shape: tuple, args, method: str, **metadata) -> dict | None`

- `candidate_from_columns(columns: list, shape: tuple, args, method: str) -> tuple`

- `parallel_candidate(path: list, features: dict, args, method: str) -> dict | None`

- `endpoints(candidate: dict, width: int) -> np.ndarray`

- `candidate_from_endpoints(values: np.ndarray, features: dict, args, method: str, **metadata) -> dict | None`

- `score_candidate(candidate: dict, features: dict, args, anchors: list[np.ndarray]) -> float`

- `consensus_candidate(anchors: list[np.ndarray], features: dict, args) -> tuple`

- `hough_candidates(image: np.ndarray, features: dict, args, coarse: list) -> list`

- `pixel_resize_transform(source_shape: tuple, target_shape: tuple) -> np.ndarray`

- `register_template(template: np.ndarray, image: np.ndarray, values: np.ndarray, args) -> tuple | None`

- `build_group(normalized: list[np.ndarray], shape: tuple, args) -> dict`

- `scale_candidate(candidate: dict, shape: tuple, analysis_shape: tuple) -> dict`

- `finalize_group(group: dict, args) -> dict`

- `safe_read(path: Path)`

- `compatible_template(first: dict, second: dict) -> bool`

- `run_batch(images: list[Path], args, report, overrides: dict, ground_truth: dict) -> None`

## [auto_roi_local_std.py](auto_roi_local_std.py)

Core ROI extraction, geometry, masking, and batch export implementation.

### `class CsvReport`

- `__init__(self, args)`
- `__enter__(self)`
- `write(self, row)`
- `__exit__(self, *_)`

- `result_identity(image_path: Path, mode: str, args, reference_path: Path | None=None) -> dict`

- `record_skipped(report: CsvReport, path: Path, modes: tuple, args, reason: str, reference_path: Path | None=None, image: np.ndarray | None=None) -> None`

- `parse_extensions(value: str) -> set[str]`

- `imread(path: Path) -> np.ndarray | None`

- `imwrite(path: Path, image: np.ndarray) -> None`

- `iter_images(source: Path, output: Path, extensions: set[str], prefix: str | None, exposure: str | None='10000us')`

- `reference_jobs(images: list[Path], exposure: str) -> tuple[list, list]`

- `odd_at_most(value: int, limit: int) -> int`

- `gray_float(image: np.ndarray) -> np.ndarray`

- `std_row_score(g: np.ndarray, kernel: int, x0: int, x1: int) -> np.ndarray`

- `fft_row_score(g: np.ndarray, x0: int, x1: int, window_size: int, stride: int, min_frequency: float, max_frequency: float) -> np.ndarray`

- `gabor_kernels(size: int, wavelengths: tuple[float, ...]) -> tuple`

- `gabor_row_score(g: np.ndarray, x0: int, x1: int, kernel: int, wavelengths: tuple[float, ...]) -> np.ndarray`

- `normalize_score(score: np.ndarray) -> np.ndarray`

- `texture_row_scores(image: np.ndarray, modes: tuple[str, ...], args, x_bounds: tuple[int, int] | None=None) -> tuple`

- `boundary_evidence(row_score: np.ndarray, brightness_edge: np.ndarray | None=None, texture_gap: int=15, texture_window: int=60, weights: tuple=(0.45, 0.15, 0.4)) -> dict`

- `boundary_pair_candidates(row_score: np.ndarray, min_height_ratio: float, max_height_ratio: float, smooth_kernel: int=51, brightness_edge: np.ndarray | None=None, texture_gap: int=15, texture_window: int=60, weights: tuple=(0.45, 0.15, 0.4)) -> list[dict]`

- `pair_dp_states(valid: list[dict], height: int, continuity_weight: float, slope_weight: float, spacing: float, height_weight: float | None=None) -> tuple`

- `trace_pair_path(valid: list[dict], predecessors: list, last: tuple) -> list[dict]`

- `select_pair_path(columns: list[dict], height: int, continuity_weight: float, slope_weight: float=12.0) -> list[dict]`

- `detect_roi_y(row_score: np.ndarray, margin: int, min_height_ratio: float, x0: int, x1: int, reference: tuple[int, int] | None=None, max_height_ratio: float=0.55, smooth_kernel: int=51) -> dict`

- `fit_boundary_line(points: list[tuple[float, float]], min_span: float, residual_threshold: float=8.0, x_bounds: tuple[float, float] | None=None, max_rmse: float | None=None, min_inlier_ratio: float=0.55, max_gap_ratio: float=0.25, max_median_residual: float=8.0) -> dict`

- `fit_boundary_with_retries(points: list, bounds: tuple, args) -> dict`

- `reacquire_boundary(columns: list[dict], known: dict, side: str, points: list, h: int, args, bounds: tuple | None=None) -> dict`

- `reacquire_pair(columns: list[dict], top: dict, bottom: dict, shape: tuple, args) -> tuple`

- `pair_quality(top: dict, bottom: dict, shape: tuple) -> dict`

- `fitted_pair_reason(top: dict, bottom: dict, shape: tuple, args) -> str | None`

- `boundary_geometry_reason(top_line: dict, bottom_line: dict, shape: tuple, args) -> str | None`

- `rasterize_lines(result: dict, shape: tuple, args) -> None`

- `load_roi_overrides(path: Path | None, source: Path, reference_exposure: str | None) -> dict`

- `apply_roi_overrides(rois: dict, image_path: Path, shape: tuple, args, overrides: dict) -> None`

- `load_ground_truth(path: Path | None, source: Path, reference_exposure: str | None) -> dict`

- `evaluate_ground_truth(rois: dict, image_path: Path, shape: tuple, args, annotations: dict) -> None`

- `ground_truth_overrides(annotations: dict, modes: tuple) -> dict`

- `tilted_roi(coarse: dict, strip_rois: list[dict], shape: tuple[int, int], args, columns: list[dict] | None=None) -> dict`

- `detect_image_rois(image: np.ndarray, modes: tuple[str, ...], args) -> dict`

- `roi_pixel_mask(shape: tuple[int, int], roi: dict) -> np.ndarray`

- `mask_outside_roi(image: np.ndarray, roi: dict) -> np.ndarray`

- `rectification_geometry(shape: tuple[int, int], roi: dict) -> dict | None`

- `display_bgr(image: np.ndarray) -> np.ndarray`

- `draw_visualization(image: np.ndarray, roi: dict, mode: str, reference_note: str | None=None) -> np.ndarray`

- `comparison_tile(masked: np.ndarray, roi: dict, mode: str) -> np.ndarray`

- `roi_csv_row(image: np.ndarray, image_path: Path, mode: str, result: dict, args, reference_path: Path | None=None) -> dict`

- `save_outputs(image: np.ndarray, image_path: Path, rois: dict, args, reference_path: Path | None=None, report: CsvReport | None=None) -> list[str]`

- `run_reference_batch(images: list[Path], modes: tuple[str, ...], args, report: CsvReport, overrides: dict | None=None, ground_truth: dict | None=None) -> None`

- `build_parser() -> argparse.ArgumentParser`

- `main() -> None`

- `run_independent_batch(images: list[Path], modes: tuple, args, report: CsvReport, overrides: dict, ground_truth: dict | None=None) -> None`

## [evaluate_roi_boundaries.py](evaluate_roi_boundaries.py)

Evaluate automatic ROI boundaries, excluding manual replacement leakage.

- `boundary_metrics(prediction: dict, spec: dict) -> dict`

- `prediction_from_row(row: dict) -> dict | None`

- `evaluate_report(report: Path, annotations: dict, mode: str, min_iou: float, max_under: float, max_p95: float) -> tuple[list, dict]`

- `main()`

## [prepare_roi_gt.py](prepare_roi_gt.py)

Create an unannotated review manifest from a completed ROI report.

- `prepare_rows(report: Path, mode: str, validation_count: int, selection: str='review') -> list[dict]`

- `main()`

## [roi_annotations.py](roi_annotations.py)

Manual ROI line and quadrilateral parsing in original image coordinates.

- `line_annotation(spec: dict) -> dict`

- `load_json_ground_truth(path: Path, source: Path, reference_exposure: str | None) -> dict`

## [roi_boundary.py](roi_boundary.py)

Gabor ROI boundary-pair detection with explicit false-pass prevention gates.

- `robust_unit(values: np.ndarray) -> np.ndarray`

- `positive_unit(values: np.ndarray) -> np.ndarray`

- `interval_means(profile: np.ndarray, starts: np.ndarray, ends: np.ndarray) -> np.ndarray`

- `features(image: np.ndarray, config: dict) -> dict`

- `peak_locations(profile: np.ndarray, count: int, config: dict, allowed: np.ndarray | None=None) -> list[int]`

- `make_columns(feature: dict, config: dict) -> list`

- `path_for(columns: list, height: int, config: dict) -> list`

- `fit_line(points: list, width: int, config: dict) -> dict`

- `recover_side(feature: dict, known: dict, side: str, expected_height: float, config: dict) -> dict`

- `fit_pair(path: list, feature: dict, config: dict, method: str) -> dict | None`

- `candidate_score(candidate: dict, feature: dict, config: dict, anchors: list) -> float`

- `detect_candidates(feature: dict, config: dict) -> tuple`

- `outside_check(candidate: dict, feature: dict, config: dict) -> dict`

- `full_frame(shape: tuple) -> dict`

- `consensus_anchor(candidates: list, feature: dict, config: dict) -> np.ndarray | None`

- `finalize(candidates: list, feature: dict, config: dict, anchors: list, total: int, args) -> dict`

- `save_debug(image: np.ndarray, feature: dict, columns: list, result: dict, path, config: dict, automatic: dict | None=None) -> None`

- `run_batch(images: list, args, report, overrides: dict, ground_truth: dict) -> None`

## [roi_boundary_quality.py](roi_boundary_quality.py)

Native-pixel review gates; no single scalar score can override these checks.

- `load_config(path: Path | None=None) -> dict`

- `line_values(result: dict, width: int) -> np.ndarray`

- `ambiguity(candidate: dict, candidates: list, width: int, config: dict) -> dict`

- `fit_reasons(fit: dict, side: str, config: dict) -> list[str]`

- `assess(candidate: dict, candidates: list, shape: tuple, config: dict, outside: dict, consensus_count: int, consensus_total: int) -> dict`
