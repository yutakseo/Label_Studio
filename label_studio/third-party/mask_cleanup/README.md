# 밝기 후처리와 매직 브러시

## 저장 마스크의 밝기 후처리

**배경 마스크 후처리** 패널에서 저장 annotation/prediction과 이미지·라벨을 선택합니다. 밝기 임계값(초기 128)을 입력하고 미리보기에서 잔존 영역·제거 픽셀을 확인한 뒤 새 어노테이션으로 저장합니다. 기존 원본과 예측을 덮어쓰지 않습니다. 편집 중인 미저장 내용은 포함하지 않습니다.

Pillow `L` 밝기가 임계값 **미만**인 픽셀의 RGBA를 0으로 만듭니다. 해당 이미지·라벨 외의 결과는 유지하고, 비어진 영역과 연결 relation은 복사본에서 제거합니다. 제거 통계는 영역별 합이라 겹침을 중복 계산할 수 있습니다.

## 현재 편집의 매직 브러시

1. Regions에서 브러시 마스크 하나를 선택합니다.
2. 툴바의 매직 브러시에서 **지우기/마스킹**을 선택합니다.
3. 밝기 허용차(초기 15)와 최대 반경(초기 원본 1000px)을 조절하고 클릭합니다.
4. 원본 밝기로 4방향 연결된 유사 영역을 처리합니다. Undo로 되돌리고 Update로 저장합니다.

지우기는 마스크 위에서 시작해야 합니다. 마스킹은 선택한 기존 영역에 추가하며 영역이 없으면 일반 브러시로 먼저 만듭니다. 다른 영역·라벨은 변경하지 않습니다. 모드는 같은 브라우저에 보존됩니다. 반경은 원본 이미지 좌표 기준입니다. 연결 여부는 원본 밝기이므로 마스크 밖 배경을 거쳐 연결된 부분도 처리될 수 있습니다.

## 구현

| 파일 | 역할 |
| --- | --- |
| `processing.py` | `decode_checked` RLE 길이·데이터 검증, `clean` 밝기 제거 |
| `views.py` | 로그인·CSRF·multipart 이미지 preview |
| `panel.js` | 저장 소스 선택, 이미지 로드, 새 annotation 저장 |
| `similar_erase.js` | 브라우저 밝기 비교·연결 탐색 |
| `similar_tool.js` | 편집기 도구, RLE·Undo 이력 갱신 |
| `patch_editor.py` | 매직 브러시·가우시안 도구를 편집기 번들에 등록 |
| `install.py`, `middleware.py`, `urls.py` | 설정·패널·확장 URL 연결 |
| `tree_export/` | 별도 ZIP 내보내기 앱 |

[CODE_MAP](CODE_MAP.md)에 함수 목록이 있습니다. 매직 브러시는 서버 preview를 호출하지 않고 현재 편집을 수정합니다. 전체 밝기 후처리는 `/mask-cleanup/preview` 계산 후 공식 annotation API로 복사본을 만듭니다.

## 제한과 반영

최대 1600만 픽셀/32MB, 500개 결과, RLE·원본 크기 일치·회전 없는 단일 이미지입니다. 외부 이미지는 CORS가 필요합니다. 매직 브러시는 읽기 전용·잠긴 영역·Bitmask/Polygon을 지원하지 않습니다.

```bash
python label_studio/third-party/mask_cleanup/patch_editor.py label_studio/overrides/358.js
node --check label_studio/overrides/358.js
node --test label_studio/third-party/mask_cleanup/test_similar_erase.cjs label_studio/third-party/mask_cleanup/test_hotkeys.cjs
docker exec label-studio python -m unittest mask_cleanup.test_processing mask_cleanup.test_http mask_cleanup.test_middleware
```

처리 Python 변경은 서버 재시작, 도구 변경은 번들 재패치와 강력 새로고침입니다. [트리 Export](tree_export/README.md)와 [가우시안](../gaussian_mask/README.md)은 별도 기능입니다.
