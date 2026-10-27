# 공식 서버·편집기 패치

Label Studio 1.23.1의 압축 번들과 Python 코드를 문자열 앵커로 수정합니다. 공식 TypeScript/React 소스 전체를 이 저장소에서 빌드하는 방식이 아닙니다. [CODE_MAP](CODE_MAP.md)에 패처 함수·검증 함수가 정리되어 있습니다.

## 패처와 적용 대상

| 패처 | 대상 | 변경 |
| --- | --- | --- |
| `brush_coordinates.py` | 358.js | 이미지 좌표 0.1px 격자 |
| `brush_size.py` | 358.js | 브러시·지우개 0.2~30px 크기 |
| `brush_grid.py` + `.js` | 358.js | 그리기·재표시·hit test·export 사각 도장 |
| `pen_input.py` + `.js` | 358.js | Pointer 펜 입력, 취소·포커스 해제 |
| `mask_merge_tool.py` + `.js` | 358.js | 툴바 합치기 버튼, 팝업 단축키 차단 |
| `annotation_author.py` | 358.js | 작성자 없는 가져온 라벨의 잘못된 Admin 표시 제거 |
| `latest_selection.py` | 167.js | 로딩 후 최신 저장 결과 선택 |
| `user_tabs.py` + `.js` | 358.js | 타인 라벨 편집·Update를 본인 작업 흐름에 연결 |
| `annotated_by.py` | data_manager/managers.py | 목록·필터의 작성자 추정 제거 |
| `annotation_ownership.py` | tasks/api.py | 실제 결과 변경 시 미지정 작성자 귀속 |
| `user_isolation.py` | label_studio 서버 루트 | 사용자별 저장·초안·삭제 통제 연결 |
| `tree_export_compat.py` | mask_cleanup/tree_export | 경로 호환·검증 오류 표시 |
| `tree_export_button.py` | 이전 tree_export panel | 과거 버튼 배치 패치, 현재 Dockerfile에서 실행하지 않음 |

## 적용

Dockerfile의 순서를 따릅니다. 어떤 패처는 앞서 주입한 도구 마커를 앵커로 사용하므로 빈 원본에 임의 순서로 전부 실행하면 실패할 수 있습니다. 현재 패치된 번들에 도구 내용을 갱신하는 예:

```bash
python label_studio/patches/mask_merge_tool.py label_studio/overrides/358.js
node --check label_studio/overrides/358.js
```

서버 대상 패처는 이미지 내부의 공식 파일을 변경하므로 Dockerfile 빌드 경로를 사용합니다. 호스트에는 공식 `tasks/api.py` 등이 없습니다. `overrides/358.js`를 마운트한 서비스는 이미지 내부 번들보다 이 파일을 사용합니다.

## 유지보수

대부분의 패처는 앵커가 정확히 한 번 존재하는지 검사하거나 마커를 찾아 기존 주입 블록을 교체합니다. `Unsupported ... anchor`는 버전/입력/적용 순서가 다른 신호입니다. 패치 실패를 무시하고 잘못된 번들을 배포하지 않습니다. 업스트림 버전을 올리면 앵커뿐 아니라 실제 편집·저장·Undo 동작까지 다시 확인해야 합니다.

```bash
node --test label_studio/patches/test_latest_selection.cjs label_studio/patches/test_pen_input.cjs label_studio/patches/test_user_tabs.cjs
```

수동 검수 항목은 확대 상태 좌표, 브러시/지우개 크기, 펜 누르기·떼기·취소, 타인 탭 수정 후 Update, 본인 탭 갱신, 최신 저장 탭 선택입니다.
