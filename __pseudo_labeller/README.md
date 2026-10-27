# 오프라인 이미지 전처리·pseudo 라벨 파이프라인

Label Studio 서버와 별도로 실행하는 데이터 준비 코드입니다. 일부 실행기에 과거 Windows 절대 경로가 남아 있으므로 실행 전 입력·출력 설정을 현재 환경으로 바꿉니다. 서버의 온라인 참고 패치 학습과는 다른 파이프라인입니다.

```text
원본 → 00_extract → mono/노출 조건 추출
     → 01_crop → 시편 ROI
     → 02_pseudo_labeller → Gaussian 이진 마스크 + YOLO polygon
     ├─ label_studio_formatting.py → images/masks/tasks/XML
     └─ 03_yolo_formatting → Roboflow YOLO ZIP
```

## 실행기

| 파일/폴더 | 역할 | 설정 |
| --- | --- | --- |
| [00_extract](00_extract/README.md) | 노출명·mono 접두어로 원본 복사 | CLI source/output/exposure |
| [01_crop](01_crop/README.md) | STD/FFT/Gabor/경계 기반 ROI | CLI, 선택 YAML |
| `gaussian_batch_processor.py` | pseudo 마스크·YOLO 배치 생성 | 파일 상단 CONFIG |
| [02_pseudo_labeller](02_pseudo_labeller/README.md) | 재사용 설정·처리·I/O·배치 클래스 | GaussianDifferenceConfig |
| `gaussian_for_parameter_tuning.ipynb` | 파라미터 비교용 노트북 | 셀별 경로·처리 확인 |
| `label_studio_formatting.py` | RLE·tasks·10개 단위 분할 import·XML | SOURCE_IMAGES/MASKS/LABELMAP, OUTPUT_ROOT |
| `yolo_formatting.py` | YOLO 패키지 실행 | CONFIG |
| [03_yolo_formatting](03_yolo_formatting/README.md) | ZIP 생성 구현 | YoloPackagingConfig |
| [__data](__data/README.md) | 단계별 원본·산출물 | 스크립트 설정에 대응 |

## 환경

독립 dependency lock/requirements 파일은 이 폴더에 없습니다. 코드 import 기준으로 NumPy·OpenCV·Pillow, ROI의 SciPy·scikit-image·PyYAML 등이 필요하며 노트북에는 실행 환경이 추가로 필요합니다. 서버 Docker 환경과 버전이 다르면 픽셀 결과도 달라질 수 있습니다.

숫자로 시작하는 패키지는 일반 `from 02_pseudo_labeller import ...` 구문 대신 `importlib.import_module`을 사용합니다. 루트 실행기들은 자체 폴더가 Python 경로에 들어가도록 파일 경로로 실행할 수 있습니다.

```bash
python __pseudo_labeller/00_extract/extract_mono.py --help
python __pseudo_labeller/01_crop/auto_roi_local_std.py --help
# 아래 명령은 파일 상단 경로 설정을 수정한 다음 실행
python __pseudo_labeller/gaussian_batch_processor.py
python __pseudo_labeller/label_studio_formatting.py
python __pseudo_labeller/yolo_formatting.py
```

## Label Studio 연결 시 확인

formatter 기본 출력은 자기 데이터셋 root를 Local Files root로 사용하는 안내를 생성합니다. 현재 Compose는 `/label-studio/data`가 root이므로 데이터셋을 `files/<dataset>`에 놓고 tasks URL에 `files/<dataset>/images/...` 접두어가 있는지 확인합니다. 생성 README의 고정 태스크 수보다 실제 생성 JSON 수를 기준으로 합니다.

같은 원본의 이미지·마스크 상대 경로와 크기가 일치해야 합니다. 노트북 후처리와 배치 처리의 차이를 구분하세요. 웹 Gaussian은 `gaussian_mask/pseudo_core`에 코드 사본을 가지므로 변경 시 동기화가 필요합니다. 자세한 함수 목록은 [CODE_MAP](CODE_MAP.md)을 참고하세요.
