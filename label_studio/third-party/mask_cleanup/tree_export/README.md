# 폴더 구조 유지 Export

프로젝트의 **Export → 폴더 구조 유지 · PNG 마스크 + 원본 (ZIP)**에서 라벨을 선택하고 **트리 구조 ZIP 다운로드**를 누릅니다. 아래 기본 Export 버튼은 기존 형식용입니다.
범위는 현재 프로젝트 전체이며 데이터 매니저의 필터/선택 행은 적용하지 않습니다.
먼저 Update/Submit으로 편집 내용을 저장하세요.

```text
20260922_(4)case01_20/
  images/case01/01/000/10000us/a.png
  masks/case01/01/000/10000us/a.png
_annotations/task-616.json
export-manifest.json
```

- `files/<데이터셋>/[하위 폴더/]images/...`의 폴더 및 원본 이미지 이름을 유지합니다.
- 대응하는 `masks/...`에 선택한 라벨의 8비트 PNG를 저장합니다(배경 0, 마스크 255).
- PNG가 아닌 원본도 이미지는 그대로 복사하며, 대응 마스크 확장자는 `.png`입니다.
- 같은 라벨의 여러 브러시 영역은 합집합으로 저장합니다. 프로젝트의 데이터는 변경하지 않습니다.
- 태스크마다 취소되지 않은 저장된 어노테이션 중 `updated_at`, ID 순으로 최신 한 개를 사용합니다.
- `_annotations` JSON에도 생성·수정 시각과 작성자·마지막 저장자 ID를 보존합니다.
- 초안/예측은 제외합니다. 저장된 어노테이션이 없으면 태스크를 건너뛰고 manifest에 기록합니다.
- 선택한 라벨이 없는 저장 결과는 빈 마스크로 저장합니다. 선택하지 않은 라벨도 `_annotations` JSON에 보존됩니다.
- 중복 경로, 지원하지 않는 URL, 파일 누락, 크기 불일치 등은 전체 다운로드를 중단하고 태스크 ID와 오류를 표시합니다.
- 원본 폴더의 `imports`, ZIP, 기존 masks 및 기타 보조 파일은 복사하지 않습니다. 프로젝트의 이미지와 수정된 마스크 트리를 재구성합니다.
- 동일 상대경로 이미지가 여러 태스크에 있으면 자동 덮어쓰기하지 않습니다.
- 기존 ExportAPI의 프로젝트 접근 권한을 따릅니다. ZIP은 서버 임시 파일에서 생성하며 응답 완료 후 닫힙니다.

마운트된 확장이므로 Python URL 변경 최초 적용 시 `docker compose restart label-studio`가 필요합니다.
JS만 수정한 경우 강력 새로고침으로 반영됩니다.

테스트: `docker exec -w /label-studio/label_studio label-studio python -m unittest mask_cleanup.tree_export.test_archive -v`

## 구현과 다중 라벨 결과

`views.TreeExportAPI`는 공식 ExportAPI의 접근 권한을 사용하고, `archive.py`는 로컬 URL을 안전한 파일 경로로 해석하고 annotation 선택·RLE 병합·파일 검증·ZIP 작성을 수행합니다. `panel.js`는 프로젝트 Export UI에 라벨 선택과 다운로드 흐름을 붙입니다. [CODE_MAP](CODE_MAP.md)에 전체 함수·테스트 목록이 있습니다.

여러 라벨을 가진 MERGE annotation도 입력으로 사용할 수 있습니다. PNG 한 장에는 사용자가 고른 **한 라벨**만 이진 마스크로 저장합니다. 다른 라벨은 `_annotations`에 보존되며, 모든 클래스의 PNG가 필요하면 라벨별로 다시 Export합니다. 다중 클래스 ID PNG를 자동 생성하는 기능은 아닙니다.
