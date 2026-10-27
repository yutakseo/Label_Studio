# 시편 ROI 추출·경계 품질 평가

전체 이미지에서 시편 영역을 찾아 마스킹/크롭/정렬 출력과 CSV를 생성하는 코드입니다. 기존 문서의 `src.roi`는 이전 저장소 구조이므로 현재는 다음 파일 진입점을 사용합니다.

```bash
python __pseudo_labeller/01_crop/auto_roi_local_std.py --help
python __pseudo_labeller/01_crop/auto_roi_local_std.py \
  --source /path/to/extracted --output /path/to/roi \
  --exposure 10000us --mode auto --image-output masked
```

CLI 기본 source/output은 과거 `data/0918`, `data/roied`이므로 현재 데이터에는 명시적으로 지정합니다. 시편 원본 좌표를 보존하려면 `masked`를 사용합니다. `crop`과 `rectified`는 좌표·크기를 바꿀 수 있으므로 원본 좌표 annotation과 혼용하지 않습니다. `gabor_boundary` 모드는 masked 출력 계약을 사용합니다.

## 모듈

| 파일 | 내용 |
| --- | --- |
| `auto_roi_local_std.py` | CLI, STD·FFT·Gabor 특성, 좌표/영상 I/O, 배치·CSV |
| `auto_roi_group.py` | 같은 시편/카메라/방향의 노출 그룹, 기준 노출, ROI 전이 |
| `roi_boundary.py` | Gabor/STD 경계 후보, 경로 선택, RANSAC, 복구 |
| `roi_boundary_quality.py` | YAML 설정, 독립 품질 판정 |
| `roi_annotations.py` | 수동 선·사각형 정답 파싱 |
| `prepare_roi_gt.py` | tune/validation 정답 manifest 준비 |
| `evaluate_roi_boundaries.py` | 경계 거리·보류 정답 평가 |

[CODE_MAP](CODE_MAP.md)에 클래스와 함수 목록이 있습니다. 추가 문서 [ROI_USAGE](ROI_USAGE.md), [ROI_BOUNDARY_USAGE](ROI_BOUNDARY_USAGE.md)는 알고리즘 배경 자료로 보존했습니다. 그 문서의 `src.roi`, Windows 작업 디렉터리, 외부 config 경로는 현재 구조에 맞게 치환해야 합니다. `ROI_PSEUDO_LABELS_USAGE.md` 등 이 폴더에 없는 과거 문서 참조는 현재 제공되지 않습니다.

## 주요 설정

`--mode`는 std/fft/gabor 계열과 auto/gabor_boundary 등 코드에 선언된 모드를 지원합니다. `--reference-exposure`, `--fusion-exposures`는 노출 그룹의 기준·보조 입력, `--roi-overrides`는 수동 보정, `--ground-truth`는 평가 정답, `--apply-ground-truth`는 정답을 실제 추출에 적용하는 별도 선택입니다.

`--boundary-config` YAML은 저장소 외부 설정일 수 있으므로 파일을 준비해야 합니다. 커널·경계 가중치·RANSAC·inlier·최대 기울기·복구 범위는 `--help`와 코드 기본값을 확인하세요. `--dry-run`, `--limit`으로 범위를 제한할 수 있습니다.

출력은 모드별 `crops/`, `roi_results.csv`, 선택적 debug 영상 등입니다. 새 출력 디렉터리에서 먼저 일부 이미지를 처리해 원본/결과·좌표를 확인한 뒤 전체 실행하세요. ROI 검출은 결함 분할 모델과 별개입니다.
