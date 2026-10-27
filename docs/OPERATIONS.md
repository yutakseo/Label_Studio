# 설치·반영·백업·검증

이 문서의 명령은 저장소 루트 기준입니다. 실행 중인 작업이 있다면 저장한 후 재시작·재빌드합니다.

## 실행

```bash
docker compose up -d --build label-studio
docker compose ps
docker compose logs --tail=100 label-studio
curl -I http://localhost:8080/
```

로그인하지 않은 `/` 요청은 로그인 화면으로 302 이동할 수 있습니다. GPU 0 연결, 포트 8080, 원본 데이터 경로는 `docker-compose.yml`이 기준입니다. GPU 메모리 부족 시 `UNET_BATCH_SIZE`를 16에서 8 또는 4로 낮추고 컨테이너를 재생성합니다. CPU 사용은 장치 환경변수 변경과 Compose GPU 예약 제거가 함께 필요합니다.

## 변경 종류별 반영

| 변경 | 필요한 작업 |
| --- | --- |
| 마운트된 Python view/처리 로직 | `docker compose restart label-studio` |
| `/panel.js` 등 별도 제공 JS | 브라우저 강력 새로고침 |
| 툴바·브러시·펜·편집기 코드 | 해당 패처로 `overrides/358.js` 또는 `167.js` 갱신 후 강력 새로고침 |
| Dockerfile·의존성·install.py·공식 API 패치 | `docker compose up -d --build label-studio` |
| Compose 장치·환경·마운트 | Compose로 컨테이너 재생성 |

예를 들어 모든 라벨 합치기는 UI가 `label:null`을 보내고 새 서버가 이를 받아야 합니다. UI만 갱신되고 서버가 구버전이면 `대상 이미지와 브러시 라벨을 선택하세요` 오류가 납니다. 새 Python 코드가 마운트되어 있어도 이미 import한 프로세스는 재시작해야 합니다.

편집기 패치의 예입니다. 변경한 도구에 해당하는 패처만 실행하며, 전체 초기 설치 순서는 Dockerfile을 따릅니다.

```bash
python label_studio/patches/mask_merge_tool.py label_studio/overrides/358.js
python label_studio/third-party/reference_segmenter/patch_editor.py label_studio/overrides/358.js
node --check label_studio/overrides/358.js
```

`overrides/358.js`가 이미지 내부 번들을 가리기 때문에 Docker 재빌드만으로 호스트 번들이 갱신되지는 않습니다. 패처는 1.23.1의 앵커를 검사합니다. 지원하지 않는 번들 오류가 나면 압축 문자열을 임의 교체하기 전에 버전과 원본 번들을 확인하세요.

## 백업과 복구

백업 대상은 `label_studio/data/` 전체와 `files/`, 배포에 필요한 로컬 확장·번들입니다. 데이터 폴더에는 DB·업로드·수정 이력·학습 패치·모델이 함께 있습니다. 코드 저장소와 모델 파일만 보관하는 것은 DB 백업이 아닙니다.

단순한 파일 백업은 서비스를 중지해 SQLite와 모델 파일이 일관된 상태일 때 수행합니다. 아래 명령은 충분한 여유 공간이 있는 별도 백업 경로를 지정한 뒤 실행합니다.

```bash
docker compose stop label-studio
# /backup은 예시입니다. 실제 백업 위치로 변경하세요.
tar -czf /backup/label-studio-data.tar.gz label_studio/data files
docker compose start label-studio
```

복구는 서비스를 중지하고 일관된 백업 세트를 원래 경로에 복원한 다음 권한·파일 URL을 점검하고 시작합니다. 데이터셋 이름을 바꾸면 태스크 URL·Local Files 저장소 경로·동기화 기록을 함께 이전해야 합니다. 수정 이력 JSON은 자동 복원 기능이 아니라 이전 DB 상태의 기록입니다.

## 검증 명령

일반 단위 테스트는 아래처럼 실행합니다. 실제 DB를 사용하는 `test_user_tabs_api`, `test_prediction_save` 등은 먼저 테스트 소스를 읽고 별도 테스트 DB·데이터 디렉터리에서 실행하세요.

```bash
docker exec label-studio python -m unittest draft_preview.test_merge draft_preview.test_merge_http
node label_studio/draft_preview/test_merge_panel.cjs
node --test label_studio/patches/test_latest_selection.cjs label_studio/patches/test_pen_input.cjs label_studio/patches/test_user_tabs.cjs
node --test label_studio/third-party/mask_cleanup/test_similar_erase.cjs label_studio/third-party/gaussian_mask/test_roi_apply.cjs label_studio/third-party/reference_segmenter/test_panel.cjs
docker exec label-studio python -m unittest mask_cleanup.test_processing mask_cleanup.test_http mask_cleanup.tree_export.test_archive u_net_labeller.test_interface
```

가우시안 원본 동등성 테스트는 전처리 소스가 `/reference`에 있어야 합니다. 로컬 경로는 `__pseudo_labeller`입니다.

```bash
docker compose run --rm --no-deps -v "$PWD/__pseudo_labeller:/reference:ro" --entrypoint python label-studio -m unittest gaussian_mask.test_processing gaussian_mask.test_http
```

Python·Node 테스트 통과는 브라우저의 실제 마스크 품질 검수를 대신하지 않습니다. 본 문서 갱신만을 위해 재학습·DB 변경 테스트나 서비스 재시작을 실행할 필요는 없습니다.

## 자주 발생하는 문제

| 증상 | 확인 항목 |
| --- | --- |
| 이미지가 보이지 않음 | `/data/local-files/?d=files/...`, 마운트, 원본 파일, URL 인코딩 |
| 새로운 도구가 보이지 않음 | 호스트 overrides 번들 패치 여부와 브라우저 캐시 |
| 새 옵션에서 기존 검증 오류 | Python 서버 재시작 여부 |
| CUDA unavailable | NVIDIA 런타임·드라이버·Compose GPU 예약·UNET_DEVICE |
| CUDA OOM | 배치 크기와 동시 작업, 이미지 크기 |
| 미리보기 403 | 로그인 세션·CSRF 쿠키·동일 출처 |
| 원본은 표시되는데 도구 실패 | 외부 이미지 CORS, 회전, 프레임 수, 픽셀·파일 크기 제한 |
| Export에 수정 내용이 없음 | Update/Submit 여부, 최신 annotation 선택, 새 ZIP 다운로드 여부 |
| 백업/학습 디렉터리 Permission denied | 파일 소유자·실행 사용자·마운트 권한 |
