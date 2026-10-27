# 프로젝트 문서 목차

## 전체 작업 흐름

[루트 개요](../README.md) → [사용자 가이드](USER_GUIDE.md) → [운영](OPERATIONS.md) → [구조](ARCHITECTURE.md).

## 실행 코드

| 위치 | 설명 |
| --- | --- |
| [label_studio](../label_studio/README.md) | 이미지 빌드, 마운트, 의존성 |
| [draft_preview](../label_studio/draft_preview/README.md) | 라벨 탭, 초안, 저장 격리, 합치기 |
| [patches](../label_studio/patches/README.md) | 공식 코드와 압축 번들 패치 |
| [overrides](../label_studio/overrides/README.md) | 실제 브라우저에 제공되는 번들 |
| [third-party](../label_studio/third-party/README.md) | 확장 모듈 탐색 |
| [mask_cleanup](../label_studio/third-party/mask_cleanup/README.md) | 밝기 제거와 매직 브러시 |
| [tree_export](../label_studio/third-party/mask_cleanup/tree_export/README.md) | 폴더 구조 유지 내보내기 |
| [gaussian_mask](../label_studio/third-party/gaussian_mask/README.md) | Gaussian 차이 마스킹 |
| [pseudo_core](../label_studio/third-party/gaussian_mask/pseudo_core/README.md) | 재사용 알고리즘 사본 |
| [u_net_labeller](../label_studio/third-party/u_net_labeller/README.md) | 256px U-Net 추론 |
| [reference_segmenter](../label_studio/third-party/reference_segmenter/README.md) | 64px 패치 학습과 클래스별 예측 |
| [scripts](../scripts/README.md) | P3 전용 준비 스크립트 |

각 Python 코드 폴더의 `CODE_MAP.md`는 현재 파일에서 추출한 클래스·함수 시그니처를 담습니다. 테스트 파일도 포함하여 어떤 검증 코드를 찾아야 하는지 확인할 수 있습니다. 시그니처는 설명을 위한 참조이며 실행 시 전체 구현을 원본 `.py`에서 확인하세요.

## 데이터 준비와 보관

[전처리 전체](../__pseudo_labeller/README.md), [추출](../__pseudo_labeller/00_extract/README.md), [ROI](../__pseudo_labeller/01_crop/README.md), [pseudo 생성](../__pseudo_labeller/02_pseudo_labeller/README.md), [YOLO ZIP](../__pseudo_labeller/03_yolo_formatting/README.md), [전처리 데이터](../__pseudo_labeller/__data/README.md), [Local Files](../files/README.md), [서버 데이터](../label_studio/data/README.md), [산출물](../outputs/README.md).

[재귀 폴더 탐색 기록](DIRECTORY_INVENTORY.md)은 문서화 범위와 접근 불가 경로를 설명합니다. `.git` 내부와 `__pycache__`는 구현 문서 대상에서 제외했습니다.
