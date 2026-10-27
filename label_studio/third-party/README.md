# Label Studio 확장 모듈

이 폴더의 확장은 로컬 Django 앱과 브라우저 패널입니다. Dockerfile에서 설치하고 Compose에서 소스를 읽기 전용으로 마운트합니다. 일반적인 외부 ML backend 서비스와 달리 현재 서버 안에서 실행합니다.

| 폴더 | 사용자 기능 | 상세 |
| --- | --- | --- |
| [mask_cleanup](mask_cleanup/README.md) | 어두운 마스크 제거, 매직 브러시 | 밝기 후처리·연결 영역 편집 |
| [mask_cleanup/tree_export](mask_cleanup/tree_export/README.md) | 원본+마스크 ZIP | 프로젝트 전체·최신 저장 annotation |
| [gaussian_mask](gaussian_mask/README.md) | 가우시안 차이 후보 | 전체·ROI 박스, 현재 편집 적용 |
| [u_net_labeller](u_net_labeller/README.md) | U-Net pseudo 라벨링 | 256px 패치·Exposure 가중치 |
| [reference_segmenter](reference_segmenter/README.md) | 참고 마스크 학습 | 클래스별 64px 수정 패치·공유 모델 |
| `dark_line` | 현재 실행 코드 없음 | 빈 이전 경로, 현재 빌드 대상 아님 |

각 코드 폴더의 CODE_MAP은 Python 함수·클래스 목록을 제공합니다. 현재 UI의 학습 경로와 과거 규칙 기반 코드의 차이는 Reference 문서에 명시했습니다.

## 반영과 지원 범위

최초 설치 및 의존성·공식 설정 변경은 `docker compose up -d --build label-studio`로 반영합니다. 이미 마운트한 Python 변경은 서버 재시작, 패널 JS는 브라우저 새로고침, 툴바 JS는 호스트 편집기 번들 재패치가 필요합니다.

대부분의 영상 API는 단일 Image + RLE BrushLabels, 회전 없는 단일 프레임, 원본 크기 일치를 전제로 합니다. 밝기·가우시안·기본 U-Net API는 최대 1600만 픽셀과 32MB 이미지 제한을 사용합니다. 외부 이미지를 브라우저에서 읽는 기능은 CORS 허용이 필요합니다. 도구별 추가 제한은 해당 README를 따릅니다.

[전체 사용법](../../docs/USER_GUIDE.md), [URL/데이터 흐름](../../docs/ARCHITECTURE.md), [배포·테스트](../../docs/OPERATIONS.md).
