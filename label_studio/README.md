# Label Studio 실행 구성

이 폴더는 공식 소스 전체가 아니라 Docker 빌드 컨텍스트입니다. 공식 `manage.py`, `core/`, `tasks/`, `web/`는 빌드 이미지 안에 있습니다.

## 빌드 순서

1. 공식 `heartexlabs/label-studio:1.23.1`에서 서버·웹 자산을 가져옵니다.
2. Debian bookworm/Python 3.12에 Label Studio 1.23.1과 시스템 영상 라이브러리를 설치합니다.
3. CUDA 12.6용 PyTorch 2.7.1 및 확장을 설치합니다.
4. 도구 등록 → 브러시 좌표/크기/격자 → 펜 → 작성자/탭 → 서버 소유권/Export/초안 격리 순으로 패치합니다.
5. 기본 명령으로 `label-studio start --host 0.0.0.0 --port 8080`을 실행합니다.

설치 스크립트의 실제 순서는 [Dockerfile](Dockerfile)이 기준입니다. Dockerfile은 호스트 `files/`나 `data/`를 이미지에 복사하지 않습니다.

## 마운트

| 호스트 | 컨테이너 | 목적 |
| --- | --- | --- |
| `label_studio/data` | `/label-studio/data` | DB와 영속 데이터 |
| `files` | `/label-studio/data/files` | 원본 데이터셋 |
| `draft_preview` | `/label-studio/label_studio/draft_preview` | 저장·초안·합치기 확장, 읽기 전용 |
| `third-party/<확장>` | `/label-studio/label_studio/<확장>` | 5개 확장, 읽기 전용 |
| `overrides/{167,358,runtime}.js` | `/label-studio/web/dist/apps/labelstudio/` | 실제 배포 번들, 읽기 전용 |

`files`는 `create_host_path:false`로 설정되어 있으므로 미리 만들어야 합니다. 외부 원본 데이터셋은 이미지와 별개입니다. `.gitignore`에 의해 일부 코드·가중치·번들이 제외되므로 새 체크아웃에서는 해당 파일 존재 여부를 먼저 확인합니다.

## 새 환경의 번들 준비

현재 운영 호스트의 `overrides`를 보관해 옮기는 방식이 가장 직접적입니다. 호스트 번들이 없으면 현재 Dockerfile로 이미지를 빌드한 뒤, **Compose를 시작하기 전에** 이미지 내부의 패치된 자산을 추출할 수 있습니다.

```bash
docker compose build label-studio
mkdir -p label_studio/overrides
docker create --name label-studio-assets label-studio:local
docker cp label-studio-assets:/label-studio/web/dist/apps/labelstudio/167.js label_studio/overrides/167.js
docker cp label-studio-assets:/label-studio/web/dist/apps/labelstudio/358.js label_studio/overrides/358.js
docker cp label-studio-assets:/label-studio/web/dist/apps/labelstudio/runtime.js label_studio/overrides/runtime.js
docker rm label-studio-assets
```

`label-studio-assets`는 임시 이름으로, 충돌하지 않는 이름을 사용하세요. 이 절차는 현재 Dockerfile 패치를 추출하며 호스트에서 별도로 추가한 과거 수동 변경은 포함하지 않습니다. U-Net의 `best.pt`도 별도 전달이 필요합니다.

## 환경변수

| 이름 | Compose 값/의미 |
| --- | --- |
| `PYTHONPATH` | `/label-studio:/label-studio/label_studio` |
| `LABEL_STUDIO_BASE_DATA_DIR` | `/label-studio/data` |
| `LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED` | `true` |
| `LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT` | `/label-studio/data` |
| `UNET_DEVICE` | `cuda:0` |
| `UNET_BATCH_SIZE` | `16` |
| `NVIDIA_DRIVER_CAPABILITIES` | `compute,utility` |
| `LABEL_STUDIO_REVISION_DIR` | 미지정 시 `/label-studio/data/mask-revisions` |

[루트 문서](../README.md), [운영 절차](../docs/OPERATIONS.md), [패치](patches/README.md), [데이터](data/README.md), [확장](third-party/README.md)을 함께 참고하세요.
