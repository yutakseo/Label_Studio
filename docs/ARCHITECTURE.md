# 구성과 코드 흐름

## 실행 계층

```text
브라우저
  ├─ 공식 편집기 번들: overrides/167.js, 358.js, runtime.js
  ├─ 미들웨어가 주입하는 패널: /draft-preview.js, /mask-merge/panel.js 등
  └─ fetch + 로그인 쿠키 + CSRF
       ↓
Label Studio 1.23.1 / Django
  ├─ 공식 API: 태스크·프로젝트·어노테이션·예측
  ├─ 확장 API: preview / learn / predictions/save / tree-export
  ├─ 공식 API 패치: 작성자·사용자별 저장·초안 접근 통제
  └─ DB + data/ + files/ + 모델 체크포인트
```

Dockerfile은 공식 이미지의 서버·웹 자산을 Debian/Python 3.12 환경으로 복사하고, 고정 버전 Label Studio 및 CUDA 12.6용 PyTorch 2.7.1을 설치합니다. glibc 환경은 NVIDIA 드라이버 라이브러리 로딩을 위한 선택입니다.

`install.py`는 빌드 때 공식 설정·URL·미들웨어·직렬화 코드를 수정합니다. 런타임에 확장 폴더를 마운트하는 것만으로 최초 설치를 대체할 수 없습니다. Compose는 소스 디렉터리뿐 아니라 호스트 번들도 마운트하므로 이미지 내부 번들보다 `overrides`가 우선합니다.

## URL 구성

`draft_preview.install`은 ROOT_URLCONF를 `draft_preview.merge_urls`로 지정합니다. 여기서 Reference Segmenter와 합치기 URL을 먼저 선언하고, `mask_cleanup.urls`를 통해 다른 확장 및 공식 `core.urls`로 연결합니다.

| 경로 | 처리 코드 | 주요 역할 |
| --- | --- | --- |
| `/draft-preview.js` | draft_preview/middleware.py | 탭·초안 UI 스크립트 |
| `/mask-merge/preview` | draft_preview/merge_views.py | 라벨별 합집합·PNG 미리보기 |
| `/mask-merge/tasks/<pk>/annotations` | MergeAnnotationAPI | 별도 MERGE 어노테이션 생성 |
| `/mask-cleanup/preview` | mask_cleanup/views.py | 밝기 기준 마스크 후처리 |
| `/gaussian-mask/preview` | gaussian_mask/views.py | Gaussian 후보 생성 |
| `/u-net-labeller/preview` | u_net_labeller/views.py | U-Net 추론 |
| `/reference-segmenter/learn` | reference_segmenter/views.py | action=train/predict/status/mask: 학습·전체 추론·상태·초기 마스크 |
| `/reference-segmenter/preview` | 같은 파일 | 이전 dark-line 규칙 검출 API, 현재 패널 추론과 구분 |
| `/reference-segmenter/predictions/save` | ReferencePredictionSaveAPI | 클래스별 예측 탭 갱신 |
| `/api/projects/<pk>/tree-export` | mask_cleanup/tree_export/views.py | 프로젝트 전체 ZIP |

미리보기 API는 결과를 계산하지만 최종 어노테이션을 저장하지 않습니다. 저장은 별도 API 호출입니다. 사용자 권한과 CSRF 검증은 각 Django view 및 상속한 공식 API 흐름을 따릅니다.

## 마스크 데이터

BrushLabels 결과의 핵심 구조입니다. 실제 RLE는 SDK 인코더가 만든 정수 배열입니다.

```json
{
  "id": "region-id",
  "type": "brushlabels",
  "from_name": "brush",
  "to_name": "image",
  "original_width": 256,
  "original_height": 256,
  "image_rotation": 0,
  "value": {"format": "rle", "brushlabels": ["Exposure"], "rle": []}
}
```

위 빈 `rle`는 구조 설명용이며 유효한 마스크가 아닙니다. RLE는 디코딩 후 RGBA의 alpha 채널을 사용합니다. `from_name`, `to_name`, 라벨 이름은 프로젝트 XML과 일치해야 합니다. 저장 해상도는 원본 이미지 기준입니다.

## 저장 경계

- **Annotation**: 사용자가 제출한 편집 가능한 결과. 일반 사용자 작업 탭은 재사용하며 MERGE는 별도 탭입니다.
- **AnnotationDraft**: 자동 저장 상태. 본인 초안만 노출·수정하며, 일반 Export 입력으로 사용하지 않습니다.
- **Prediction**: U-Net 또는 Reference Segmenter 후보. 검수 후 수동 결과로 저장할 수 있습니다.
- **Revision JSON**: DB 변경·삭제 직전에 보관하는 이전 상태. 자동 복원 UI는 구현되어 있지 않습니다.
- **참고 패치 NPZ/체크포인트**: DB와 분리된 공유 모델 데이터. 프로젝트·이미지 컨트롤·라벨 단위로 구분합니다.

`mask_original`은 비교 전용 prediction이며 일반 Export 직렬화에서 제외됩니다. 트리 Export는 prediction 전체를 제외하고 최신 저장 annotation 하나를 선택합니다.

## 기존 코드와 현재 경로

`reference_segmenter/processing.py`의 dark-line 규칙, `learning.py`의 prototype 방식, `bootstrap.py`의 전체 이미지 학습은 현재 64px 패치 학습과 구분해서 읽어야 합니다. 파일이 존재한다는 사실만으로 현재 UI에서 사용되는 기능은 아닙니다. `dark_line/`은 현재 비어 있고 Dockerfile은 `reference_segmenter`를 사용합니다.
