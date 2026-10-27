# pseudo_labeller 기반 가우시안 마스킹

`__pseudo_labeller/02_pseudo_labeller/processing.py`의 `GaussianDifferenceMaskMaker`를 그대로 호출합니다.
Docker 빌드 범위를 유지하기 위해 원본 `config.py`, `processing.py`를 `pseudo_core/`에 수정 없이 포함했습니다.
동등성 테스트는 원본 파일 해시와 9가지 이미지/설정 조합의 최종 픽셀을 비교합니다.
원본을 변경했다면 두 파일을 다시 복사하고 동등성 테스트를 실행하세요.

## 처리 과정

1. 원본 파일을 `cv2.imdecode(..., cv2.IMREAD_UNCHANGED)`로 읽습니다.
2. `cv2.GaussianBlur(image, (kernel, kernel), sigma)`를 적용합니다.
3. `int16` 원본−블러 차이를 계산합니다. 컬러는 채널별 차이를 평균한 뒤 절댓값을 취합니다.
4. Otsu 자동 임계값 또는 고정 임계값으로 이진화합니다. 고정 임계값은 OpenCV의 **초과(>)** 조건입니다.
5. 외곽 윤곽선을 추출하고 최소 면적 미만을 제외한 뒤 내부를 채웁니다.
6. 동일한 이진 마스크를 Label Studio BrushLabels RLE로 인코딩합니다.

기본값은 `gaussian_batch_processor.py`와 동일합니다: **커널 101 / σ 10 / Otsu / 최소 면적 0**.
튜닝 노트북의 추가 후처리(완성된 마스크에 재블러→Otsu)는 배치 처리에는 없으므로 적용하지 않습니다.

## 적용

저장소 루트에서 실행합니다. 컨테이너가 재생성되므로 편집 내용을 먼저 저장하세요.

```sh
python label_studio/third-party/mask_cleanup/patch_editor.py label_studio/overrides/358.js
docker compose up -d --build label-studio
```

브라우저를 강력 새로고침합니다.

## 툴바에서 현재 편집에 적용

1. Regions에서 교체할 브러시 마스크를 선택한 뒤 이미지 툴바의 **가우시안 마스킹 적용**(종 모양 곡선과 + 아이콘)을 누릅니다.
2. 라벨을 고르고 커널·시그마·임계값 방식·최소 윤곽 면적을 조절합니다.
3. **미리보기**로 원본/블러/차이 영상/최종 마스크를 비교합니다.
4. **현재 편집에 마스킹 적용**을 누릅니다. 선택한 영역의 ID·라벨을 유지하고 마스크 픽셀만 교체합니다. 선택하지 않았다면 선택 안내를 표시합니다.
5. **Undo/Redo**로 되돌리거나 **Update/Submit**으로 저장합니다.

태스크/어노테이션이 변경되면 적용을 거부합니다. 회전 및 다중 이미지에는 툴바 적용을 지원하지 않습니다.
우측 파란색 바로가기 버튼은 제거했습니다. 툴바의 종 모양 버튼으로 팝업을 엽니다.
검출 픽셀이 0이면 적용/저장하지 않습니다. 별도 복사본 저장은 기존 라벨들을 복사하지 않습니다.

## 범위

8비트 단일 이미지, 최대 1600만 픽셀/32MB, 단일 `$field` Image + BrushLabels를 지원합니다.
EXIF 회전·다중 프레임·per-region 라벨은 지원하지 않습니다. 외부 이미지에는 CORS 허용이 필요합니다.
픽셀 동등성은 같은 8비트 원본, OpenCV 버전, 파라미터를 사용했을 때를 기준으로 합니다.

차이가 큰 정상 경계·질감·잡음도 검출할 수 있습니다. 불량 여부는 미리보기에서 확인하세요.
`POST /gaussian-mask/preview`는 로그인·CSRF 검증 후 처리하며 DB에 쓰지 않습니다.

## 검증

```sh
docker build -t label-studio:gaussian-refactor-test label_studio
docker run --rm -v "$PWD/__pseudo_labeller:/reference:ro" --entrypoint python -w /label-studio/label_studio label-studio:gaussian-refactor-test -m unittest gaussian_mask.test_processing gaussian_mask.test_http -v
node --check label_studio/third-party/gaussian_mask/panel.js
node --check label_studio/overrides/358.js
```

## 박스 영역만 적용

마스크를 선택하고 가우시안 팝업을 열어 원본 이미지에서 드래그하면 적용 박스를 지정할 수 있습니다.
**미리보기 → 적용** 시 해당 박스의 잘라낸 원본에 기존 Gaussian/Otsu/윤곽 채우기를 수행합니다.
Otsu도 박스 내부의 차이값을 기준으로 결정하므로 전체 이미지 처리 결과와 다를 수 있습니다.
선택한 마스크의 ID·라벨과 박스 밖 픽셀은 보존하고, 박스 안은 검출 결과로 교체합니다.
검출이 0이면 박스 안의 기존 마스크를 비웁니다. 박스 해제를 누르면 전체 이미지 처리로 돌아갑니다.
박스는 편집 범위이며 RectangleLabels 어노테이션으로 저장하지 않습니다. Undo/Redo를 지원합니다.

## 코드 탐색

`processing.generate`는 입력·옵션·박스 범위를 검증하고 `pseudo_core`를 호출한 뒤 원본 크기의 RLE 및 비교 영상을 만듭니다. `views.py`는 로그인·CSRF·이미지 업로드를 처리합니다. `panel.js`는 preview·현재 선택 마스크 적용·새 저장 흐름을, `tool.js`는 공식 편집기에서 현재 영역의 ID·라벨과 박스 밖 픽셀을 유지하는 적용을 담당합니다.

[CODE_MAP](CODE_MAP.md), [알고리즘 사본](pseudo_core/README.md), [배치 원본](../../../__pseudo_labeller/02_pseudo_labeller/README.md)을 참고하세요. `pseudo_core` 수정은 원본과의 해시·픽셀 동등성 테스트로 확인하며, 원본 마운트 경로는 `/reference`입니다.
