# Label Studio · 이미지 마스크 라벨링 작업 환경

이 저장소는 **Label Studio 1.23.1**을 기반으로 시편 이미지의 브러시 마스크 작성·보정·학습·내보내기를 지원하는 Docker 확장 프로젝트입니다. 공식 Label Studio 소스 전체가 아니라, 설치 이미지에 적용하는 Python/JavaScript 확장과 패치, 데이터 전처리 도구를 관리합니다.

## 폴더 구조

```text
Label_Studio/
├── docker-compose.yml             # 서버, GPU, 데이터·코드·번들 마운트
├── label_studio/
│   ├── Dockerfile                 # Debian/Python 3.12 + LS 1.23.1 + CUDA PyTorch
│   ├── draft_preview/             # 작성자·초안·사용자별 저장, 마스크 합치기
│   ├── patches/                   # 공식 서버 및 편집기 번들 패치
│   ├── overrides/                 # 실제 서비스에 마운트하는 프런트엔드 번들
│   ├── third-party/
│   │   ├── mask_cleanup/          # 밝기 후처리·매직 브러시
│   │   │   └── tree_export/       # 원본 폴더 구조를 유지하는 ZIP
│   │   ├── gaussian_mask/         # 가우시안 차이 기반 마스크
│   │   │   └── pseudo_core/       # 오프라인 알고리즘 사본
│   │   ├── u_net_labeller/        # 256×256 패치 U-Net 추론
│   │   ├── reference_segmenter/   # 클래스별 64×64 참고 패치 학습
│   │   └── dark_line/             # 현재 비어 있는 이전 경로
│   └── data/                      # SQLite, 업로드, 이력, 학습 모델
├── files/                         # Local Files 데이터셋: images/masks/tasks/config
├── __pseudo_labeller/
│   ├── 00_extract/                # 노출 조건별 mono 원본 추출
│   ├── 01_crop/                   # 시편 ROI 추출·경계 평가
│   ├── 02_pseudo_labeller/        # Gaussian pseudo 마스크·YOLO polygon
│   ├── 03_yolo_formatting/        # Roboflow용 YOLO ZIP
│   └── __data/                    # 전처리 단계별 데이터
├── scripts/                       # P3 데이터 검증·태스크 생성·비교 탭 등록
├── outputs/                       # 업무 산출물
└── docs/                          # 전체 사용법·운영·코드 탐색 안내
```

하위 폴더의 README와 CODE_MAP에는 파일 역할, 주요 함수, 입력·출력, 적용 및 검증 방법을 정리했습니다. 데이터의 시편·촬영 조건별 반복 디렉터리는 상위 데이터 문서에서 설명합니다.

## 주요 기능

| 기능 | 동작 | 상세 문서 |
| --- | --- | --- |
| 정밀 수동 편집 | 브러시·지우개 0.2~30px, 0.1px 이미지 좌표 격자, 사각 도장, 펜 입력 | [패치](label_studio/patches/README.md) |
| 매직 브러시 | 클릭한 밝기와 연결된 영역을 지우거나 선택 마스크에 추가 | [밝기 도구](label_studio/third-party/mask_cleanup/README.md) |
| 가우시안 마스킹 | 원본−블러 차이와 Otsu로 마스크 생성, 전체/박스 범위 적용 | [Gaussian](label_studio/third-party/gaussian_mask/README.md) |
| U-Net pseudo 라벨링 | 256px 패치를 중첩 추론하고 원본 해상도로 합성 | [U-Net](label_studio/third-party/u_net_labeller/README.md) |
| 참고 마스크 학습 | 클래스별 64px 수정 패치를 공유 모델에 누적 학습 | [Reference Segmenter](label_studio/third-party/reference_segmenter/README.md) |
| 마스크 합치기 | 여러 저장 탭을 라벨별로 합쳐 별도 MERGE 탭 생성 | [합치기·저장](label_studio/draft_preview/README.md) |
| 사용자별 저장 | 다른 작성자의 라벨 보존, 본인 작업 탭·초안 분리, 변경 전 이력 보관 | [사용자 격리](label_studio/draft_preview/README.md) |
| 폴더 구조 유지 Export | 최신 저장 라벨로 PNG 마스크와 원본 이미지 ZIP 생성 | [트리 Export](label_studio/third-party/mask_cleanup/tree_export/README.md) |
| 오프라인 데이터 준비 | 원본 추출 → ROI → pseudo 마스크 → LS/YOLO 변환 | [전처리](__pseudo_labeller/README.md) |

## 빠른 시작

Docker Engine, Compose 플러그인과 NVIDIA Container Toolkit이 구성된 GPU 호스트를 기준으로 합니다. 현재 Compose는 GPU 0을 요청하며 서버 추론 장치를 `cuda:0`으로 지정합니다. CPU 전용 호스트에서는 GPU 예약을 제거하고 `UNET_DEVICE=cpu`로 변경해야 합니다.

```bash
# 저장소 루트에서 실행. bind mount 원본 폴더를 먼저 생성합니다.
mkdir -p files label_studio/data
docker compose up -d --build label-studio
docker compose ps
docker compose logs --tail=100 label-studio
```

`http://localhost:8080`에 접속해 계정을 만들고 프로젝트를 생성합니다. 초기 비밀번호를 코드에 지정하지 않습니다. 기존 데이터 볼륨을 사용하면 기존 계정·프로젝트를 유지합니다. Compose의 `overrides/*.js` 원본 파일이 있어야 합니다. 다른 환경에 Git으로 복제한 경우 [설치·마운트 안내](label_studio/README.md)를 먼저 확인하세요.

프로젝트 Labeling Interface에 데이터셋의 `label_config.xml`을 붙여 넣고 `tasks.json` 또는 분할된 `imports/tasks_*.json`을 가져옵니다. 동일 데이터는 UI Import와 Local Files Sync 중 한 방식으로 등록합니다. [데이터 연결](files/README.md)에 URL·저장소 설정 예시가 있습니다.

## 작업 순서

1. 태스크를 열고 저장 라벨 또는 모델 예측을 확인합니다.
2. 브러시·지우개·매직 브러시·가우시안 도구로 마스크를 보정합니다.
3. **Update/Submit**으로 저장합니다. 자동 저장 초안은 최종 저장 라벨과 다릅니다.
4. 필요하면 U-Net 예측이나 참고 패치 학습으로 후보를 만들고 수동 검수합니다.
5. 여러 클래스의 결과는 **마스크 합치기 → 모든 라벨 유지**로 묶어 MERGE 탭에 저장합니다.
6. **Export → 폴더 구조 유지**에서 내보낼 라벨을 선택해 ZIP을 다운로드합니다. PNG는 선택한 라벨의 이진 마스크이고, 전체 결과는 `_annotations` JSON에 보존됩니다.

## 개발 및 운영 문서

- [사용자 작업 안내](docs/USER_GUIDE.md): 저장·예측·합치기·Export 동작과 제약
- [운영 안내](docs/OPERATIONS.md): 재시작/재빌드/번들 패치, 백업, 오류 해결, 검증
- [구조와 데이터 흐름](docs/ARCHITECTURE.md): URL 연결, 코드 주입, 저장 경계
- [폴더 탐색 결과](docs/DIRECTORY_INVENTORY.md): 재귀 탐색 범위, 코드/데이터 현황, 접근 제한
- [문서 목차](docs/README.md): 하위 모듈 전체 문서

Python 확장을 수정하면 **서버 재시작**, 패널 JS를 수정하면 **브라우저 새로고침**, 편집기 도구를 수정하면 **마운트된 번들 패치**, Dockerfile·설치 스크립트·의존성을 수정하면 **재빌드**가 필요합니다. 화면만 갱신하면 서버가 이전 API 계약을 유지할 수 있습니다.

## 데이터 보관과 버전 관리

`label_studio/data/`와 `files/`는 별도로 백업합니다. DB만으로 원본 이미지·학습 패치·체크포인트를 복원할 수 없습니다. `.env`, SQLite, 원본 이미지, 모델 가중치, 생성 ZIP 등은 Git 관리 대상에서 제외합니다. 이 저장소의 일부 확장 코드와 번들도 기존 `.gitignore`에 의해 제외되어 있으므로 다른 호스트로 이전할 때 필요한 파일을 함께 전달해야 합니다.

상위 제품은 HumanSignal의 Label Studio이며, 이 문서는 현재 로컬 구성과 소스에 기반합니다. 공식 소스의 Poetry·Makefile·Nginx/PostgreSQL 설치 예시는 이 저장소에 해당 파일이 없어 포함하지 않았습니다.
