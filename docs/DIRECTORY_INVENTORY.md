# 재귀 폴더 탐색 기록

2026-10-27 기준 작업 디렉터리를 `os.walk`로 재귀 순회했습니다. `.git`과 `__pycache__`는 제외했고 숨김 설정의 **내용**, SQLite 레코드, 이미지 픽셀, Excel 행은 문서화 목적으로 읽지 않았습니다. 아래 수치는 읽을 수 있는 디렉터리 항목을 기준으로 한 스냅샷이며 새 문서·운영 데이터 생성에 따라 달라집니다.

코드 폴더는 소스·기존 문서·설정·진입점·함수 목록을 확인했습니다. 데이터는 파일 경로와 확장자·트리 구조를 확인하고, 저장 계약은 생성/소비 코드를 근거로 설명했습니다. 모든 이미지나 모델을 열어 품질을 검수했다는 의미는 아닙니다.

접근 가능한 하위 디렉터리 **3,657개**, 파일 **6,232개**를 확인했습니다. 반복되는 촬영 조건·모델 이력 폴더는 관리 단위로 묶어 표시합니다.

| 관리 단위 | 디렉터리 수(해당 경로 포함) | 파일 수 | 주요 확장자 |
| --- | ---: | ---: | --- |
| `(root)` | 1 | 4 | .yml: 1, .md: 1, .xlsx: 1, (확장자 없음): 1 |
| `__pseudo_labeller` | 1 | 8 | .py: 3, .md: 2, (확장자 없음): 2, .ipynb: 1 |
| `__pseudo_labeller/00_extract` | 1 | 3 | .md: 2, .py: 1 |
| `__pseudo_labeller/01_crop` | 1 | 12 | .py: 8, .md: 4 |
| `__pseudo_labeller/02_pseudo_labeller` | 1 | 8 | .py: 5, .md: 2, (확장자 없음): 1 |
| `__pseudo_labeller/03_yolo_formatting` | 1 | 5 | .md: 2, .py: 2, (확장자 없음): 1 |
| `__pseudo_labeller/__data` | 1 | 3 | .md: 1, (확장자 없음): 1, .zip: 1 |
| `__pseudo_labeller/__data/20260918_(0)raw` | 879 | 1,135 | .png: 1110, (확장자 없음): 24, .lnk: 1 |
| `__pseudo_labeller/__data/20260918_(1)extracted` | 264 | 86 | .png: 86 |
| `__pseudo_labeller/__data/20260918_(2)cropped` | 266 | 87 | .png: 86, .csv: 1 |
| `__pseudo_labeller/__data/20260922_(3)labelled` | 529 | 174 | .txt: 88, .png: 86 |
| `__pseudo_labeller/__data/20260922_(4)labelstudio` | 530 | 184 | .png: 172, .json: 10, .md: 1, .xml: 1 |
| `docs` | 1 | 4 | .md: 4 |
| `files` | 1 | 1 | .md: 1 |
| `files/20260922_(4)case01_20` | 529 | 175 | .png: 172, .md: 1, .json: 1, .xml: 1 |
| `files/20261002_(4)case_14` | 21 | 9 | .png: 6, .md: 1, .json: 1, .xml: 1 |
| `files/20261010_case16_(4)label_studio` | 21 | 9 | .png: 6, .md: 1, .json: 1, .xml: 1 |
| `files/20261016_case(3)` | 6 | 31 | .png: 26, .json: 3, .md: 1, .xml: 1 |
| `files/20261020_생기원추가시편` | 201 | 91 | .png: 80, .json: 7, .md: 2, .xml: 2 |
| `files/P3_72_with_masks` | 8 | 510 | .png: 504, .json: 2, .xml: 1, .txt: 1, .html: 1 |
| `label_studio` | 1 | 2 | .md: 1, (확장자 없음): 1 |
| `label_studio/data` | 1 | 4 | (확장자 없음): 2, .md: 1, .sqlite3: 1 |
| `label_studio/data/backups` | 7 | 22 | .json: 20, .sqlite3: 2 |
| `label_studio/data/export` | 3 | 36 | .json: 32, .sqlite3: 2, .py: 2 |
| `label_studio/data/files` | 1 | 0 |  |
| `label_studio/data/mask-revisions` | 351 | 3,430 | .json: 3430 |
| `label_studio/data/media` | 2 | 0 |  |
| `label_studio/data/path-repair-backup-case3` | 2 | 6 | .json: 5, .xml: 1 |
| `label_studio/data/reference_segmenter` | 13 | 64 | .png: 40, .json: 11, .pt: 6, .lock: 4, .md: 3 |
| `label_studio/data/test_data` | 1 | 0 |  |
| `label_studio/draft_preview` | 1 | 16 | .py: 11, .md: 2, .js: 2, .cjs: 1 |
| `label_studio/overrides` | 1 | 4 | .js: 3, .md: 1 |
| `label_studio/patches` | 1 | 22 | .py: 13, .js: 4, .cjs: 3, .md: 2 |
| `label_studio/third-party` | 1 | 2 | .md: 1, (확장자 없음): 1 |
| `label_studio/third-party/dark_line` | 1 | 0 |  |
| `label_studio/third-party/gaussian_mask` | 2 | 16 | .py: 9, .md: 4, .js: 2, .cjs: 1 |
| `label_studio/third-party/mask_cleanup` | 2 | 24 | .py: 14, .md: 4, .js: 4, .cjs: 2 |
| `label_studio/third-party/reference_segmenter` | 1 | 28 | .py: 22, .md: 2, .js: 2, .cjs: 1, (확장자 없음): 1 |
| `label_studio/third-party/u_net_labeller` | 1 | 11 | .py: 7, .md: 2, .pt: 1, .js: 1 |
| `outputs` | 1 | 2 | .md: 1, .xlsx: 1 |
| `scripts` | 1 | 4 | .md: 2, .py: 2 |

## 접근 제한

- `label_studio/data/reference_segmenter/16/shared/673c4a99ba1400b89b36db850bc283a80cf08e2bce88940f5a0d4799208f6d5e`: 호스트 사용자 권한으로 내부를 열 수 없습니다. 구현과 기존 모델 문서로 저장 규칙을 설명했으며 내부 파일 수는 위 집계에서 제외했습니다.
- `label_studio/data/reference_segmenter/16/shared/c69240f6f64728945606747f772337e7a243404b479c32c841a749573b17f936`: 호스트 사용자 권한으로 내부를 열 수 없습니다. 구현과 기존 모델 문서로 저장 규칙을 설명했으며 내부 파일 수는 위 집계에서 제외했습니다.

## 문서 배치 기준

코드가 있는 14개 관리 폴더에 README와 CODE_MAP을 두었습니다. 빌드·번들·Local Files·서버 데이터·산출물은 각각 README로 설명합니다. 학습 체크포인트별·시편별·촬영 노출별 폴더는 자동 생성/외부 데이터이므로 README를 반복 생성하지 않고 상위 저장 계약을 안내합니다. 현재 빈 `label_studio/third-party/dark_line`은 상위 확장 목차에 명시했습니다.

원래 Git 제외 대상인 코드/데이터 경로의 문서도 버전 관리할 수 있도록 `.gitignore`에 Markdown 예외를 추가했습니다. 이미지·가중치·DB·기존 제외 소스의 추적 상태는 유지합니다. 문서에 비밀값과 실제 DB 행을 포함하지 않습니다.
