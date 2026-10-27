# 라벨 탭·초안·사용자별 저장·마스크 합치기

공식 API와 편집기에 사용자별 작업 저장 규칙을 연결합니다. `panel.js`는 작성자·초안·수정 시각과 탭 선택을 보정하고, `user_isolation.py`는 서버 권한·저장·이력을 담당합니다. 전체 함수 목록은 [CODE_MAP](CODE_MAP.md)을 참고하세요.

## 파일과 코드 흐름

| 파일 | 역할 |
| --- | --- |
| `install.py` | 미들웨어·ROOT_URLCONF·Export 필터 설치 |
| `middleware.py` | 프로젝트 HTML에 탭/합치기 패널 주입, 이력 signal 설치 |
| `panel.js` | 사용자 이름 조회, 탭 제목/시간/초안 표시, 최신 저장 결과 선택 |
| `user_isolation.py` | 타인 결과 편집 시 본인 작업 탭 연결, 초안 격리, 변경 전 JSON 보관 |
| `export_filter.py` | 일반 Export에서 비교 전용 `mask_original` 예측 제거 |
| `merge_urls.py` | 합치기·Reference·기존 확장 URL 연결 |
| `merge_panel.js` | 소스 선택, 미리보기, 저장 전 원본 재검사 |
| `mask_merge.py` | RLE 검증, 라벨 그룹별 합집합, 결과 RLE 생성 |
| `merge_views.py` | 로그인/CSRF preview와 별도 MERGE 생성 API |

## 저장 규칙

다른 사용자의 라벨을 Update하면 본인 일반 작업 탭을 재사용하거나 새로 만들며, 타인 원본을 유지합니다. 다른 사용자의 라벨 삭제는 거부합니다. 작성자 미지정 라벨은 실제 결과 변경 시 작성자를 지정합니다. 초안은 본인 것만 노출·변경·삭제하며 타인의 저장 때문에 삭제되지 않도록 분리합니다.

`regular_annotations`는 task metadata의 `mask_merge_annotations`에 등록된 ID를 제외합니다. 따라서 일반 작업 저장이 MERGE 결과와 섞이지 않습니다. `MergeAnnotationAPI.keep_separate_annotation=True`는 합치기마다 별도 결과 생성을 유지합니다.

기존 annotation/draft가 갱신·삭제되기 전에 signal이 이전 DB 값을 `data/mask-revisions/<task>/<model>/<pk>/*.json`으로 씁니다. 보관 실패 시 예외를 전파하며, 자동 복원 UI는 없습니다.

## 합치기 계약

```python
results, union_mask, stats = merge_masks(
    sources=[annotation_a_results, prediction_b_results],
    from_name="brush", to_name="image", label=None,
)
```

`label=None`은 모든 라벨 유지입니다. 특정 문자열은 그 라벨만 선택합니다. 각 source는 저장 결과 배열이고 2~32개를 받습니다. 마스크마다 원본 크기·RLE·회전을 확인하고, 그룹별로 이진 OR를 계산합니다. 일반적인 단일 라벨 결과는 라벨당 하나의 출력 영역이 됩니다. 여러 라벨이 동시에 지정된 입력 영역은 라벨 집합을 하나의 그룹 키로 유지합니다.

결과는 새 region ID, 원본 크기와 `origin=manual`을 가집니다. 원본 source를 수정하지 않습니다. 반환 `union_mask`는 모든 라벨을 OR한 통계용 영상이며, 실제 저장은 `results`의 각 라벨 RLE입니다. `stats.pixels`는 겹침을 한 번만 세는 전체 합집합 픽셀 수입니다.

`POST /mask-merge/preview` 예시 구조:

```json
{"sources": [["실제 result 객체 배열로 교체"], ["실제 result 객체 배열로 교체"]],
 "from_name": "brush", "to_name": "image", "label": null}
```

위 source 문자열은 설명용 자리표시자이며 실행 요청에는 실제 결과 객체가 필요합니다. 응답은 `results`, `stats`, data URL `preview`입니다. preview는 구분 색을 순환 사용하며 겹친 픽셀에서는 마지막 색이 보입니다. 데이터에는 각 마스크를 보존합니다.

미리보기 후 저장 직전에 태스크와 선택 원본 result를 다시 조회합니다. 원본 변경 시 저장을 거부합니다. 저장은 `/mask-merge/tasks/<task>/annotations`로 결과를 생성하고 `task.meta.mask_merge_annotations[id].name="MERGE"`를 기록합니다.

## 제한 및 검증

동일 이미지/브러시 컨트롤, RLE, 회전 0, 최대 1600만 픽셀, 탭당 500개 결과를 검사합니다. 총 디코드 작업량과 라벨별 버퍼 크기에도 제한을 둡니다. 저장되지 않은 편집·초안은 병합 대상이 아닙니다.

```bash
docker exec label-studio python -m unittest draft_preview.test_merge draft_preview.test_merge_http
node label_studio/draft_preview/test_merge_panel.cjs
```

`test_user_tabs_api.py`는 DB 통합 검증이므로 별도 테스트 환경에서 사용합니다. Python 변경은 서버 재시작, 패널 변경은 브라우저 강력 새로고침, `install.py` 변경은 재빌드가 필요합니다.
