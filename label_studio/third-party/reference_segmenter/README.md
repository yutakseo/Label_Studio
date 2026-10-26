# 참고 마스크 학습 · Reference Segmenter

사용자가 수정한 **64×64 패치만으로 학습하는 U-Net**입니다. 전체 이미지는 학습 데이터로 사용하지 않습니다.

## 사용 흐름

1. **참고 마스크 학습**을 열고 이미지·라벨을 선택합니다.
2. 현재 태스크에서 본인이 저장한 해당 라벨의 최신 마스크를 가져옵니다. 미저장 편집은 먼저 Update로 저장하세요.
3. 왼쪽 원본에서 64×64 ROI를 고르고 오른쪽 메인에서 마스크를 수정합니다.
4. **참고 마스크 학습**을 누르면 원본 패치·마스크 쌍을 저장하고, 저장된 수정 패치들만 사용해 U-Net을 20스텝 추가 학습합니다. 같은 사용자·태스크·좌표는 수정본으로 교체합니다. 다른 사용자의 패치는 함께 보존합니다.
5. **미리보기**로 전체 이미지에 대해 패치별 추론·합성을 수행합니다.
6. 원하면 **Reference Segmenter 탭 저장·갱신**을 누릅니다. 태스크에 기존 탭이 있으면 같은 ID의 결과를 갱신하고, 없을 때만 생성합니다. 동시 저장은 태스크 잠금으로 직렬화합니다. 기존 중복 탭은 하나로 합칩니다.

ROI 이동만으로는 학습 데이터에 저장되지 않습니다. 빨간 마스크 이외의 픽셀은 배경으로 학습됩니다.

## 학습과 추론

- 모델: grayscale U-Net, base_channels=32, 파라미터 7,849,025개. `model.ReferenceUNet`이 모델 호출 자체에서 입력/출력 `[N,1,64,64]`를 강제합니다. 256×256 입력은 첫 convolution 이전에 거부합니다.
- 학습 입력: 정확히 64×64 RGB 원본 패치 + 64×64 마스크. 다른 크기는 거부합니다.
- 전처리: RGB → 그레이스케일, uint8 / 255. 학습/추론 모두 리사이즈하지 않습니다.
- 증강: 90도 단위 회전·좌우 반전
- 손실: BCE + Dice, 최적화 AdamW
- 초기화: 패치 전용 새 모델은 무작위 초기화. 과거 전체 이미지로 학습한 체크포인트나 사전학습 가중치를 불러오지 않습니다.
- 이후 학습: 패치 전용 체크포인트에서 이어서 추가 학습합니다.
- 전체 이미지 추론: 64×64 패치, stride=32, 겹침 영역의 확률을 양의 Hann 가중치로 평균한 뒤 임계값 적용
- 가장자리: 반사 패딩 후 합성하고 원본 크기로 복원. 이미지 바깥과 이어진 검은 여백은 제외
- CPU/GPU: CUDA가 있으면 GPU 사용

전체 이미지의 저장 마스크는 패치 초기값을 가져오거나 검증에만 사용합니다. 검증에서는 역전파하지 않습니다. 학습 함수 자체가 64×64가 아닌 학습 쌍을 거부하며, API는 `corrections/`만 읽습니다.

## 데이터와 체크포인트

프로젝트 참여자가 모델과 학습 패치를 함께 사용합니다. 다른 프로젝트와는 분리되며, 저장 마스크 가져오기는 본인의 라벨만 조회합니다.

`data/reference_segmenter/<project>/shared/<hash>/` 아래 Image/BrushLabels/라벨 hash별로 분리합니다. 최초 접근 시 기존 개인 모델 중 체크포인트 수정 시간이 가장 최근인 모델과 해당 학습 데이터를 복사합니다. 기존 개인 폴더는 보존하며, 서로 다른 개인 모델의 가중치를 합치지 않습니다. 이후 학습은 공용 모델에 누적되고 파일 잠금으로 직렬화됩니다.

- `<hash>.samples/corrections/`: 활성 학습 데이터인 수정 패치·마스크
- `<hash>.samples/excluded_full_images/`: 과거에 수집한 전체 이미지. 현재 학습에서는 제외
- `<hash>.samples/validation/`: 검증용 전체 이미지·마스크
- `<hash>.pt`: 현재 패치 전용 모델
- `<hash>.previous.pt`: 직전 추가 학습 모델 백업
- `<hash>.json`: 수정 이력·학습 메타데이터
- `retraining/<timestamp>/`: 재학습 데이터 manifest, 보고서, 검증 마스크, 모델
- `evaluations/<timestamp>/`: 과거 평가 기록. 과거 모델은 현재 활성 모델과 다를 수 있음

현재 수정 패치 수는 패널에서 확인할 수 있습니다. 과거 전체 이미지 학습 모델을 교체하기 위해 이 패치들만으로 처음부터 재학습했습니다. 과거에 보고한 전체 이미지 혼합 학습 모델의 성능은 새 모델의 성능이 아닙니다.

과거 Gaussian 모델의 최초 53회 기록은 합계 통계만 보관해서 원본 패치를 복원할 수 없습니다. 현재는 원본 패치와 마스크를 NPZ로 보존합니다.

## 재학습 및 검증

```sh
# 활성/직전 가중치를 제거하고 corrections/의 패치만으로 처음부터 재학습
# 검증은 수정 패치와 태스크가 겹치지 않는 validation/ 이미지를 사용
# 예측/어노테이션 DB에는 쓰지 않음
docker exec label-studio python -m reference_segmenter.retrain --checkpoint /label-studio/data/reference_segmenter/16/shared/c69240f6f64728945606747f772337e7a243404b479c32c841a749573b17f936/c69240f6f64728945606747f772337e7a243404b479c32c841a749573b17f936.pt --steps 1500
```

검증 데이터로 가중치를 선택하므로 독립 테스트 성능으로 해석하면 안 됩니다. 이후 패널의 20스텝 추가 학습은 검증 점수를 매번 재산출하지 않습니다. 전체 이미지 학습을 하던 `bootstrap.py`는 이전 실행 기록용이며 패치 전용 학습 경로로 사용하지 않습니다.

```sh
node --check label_studio/third-party/reference_segmenter/panel.js
node --test label_studio/third-party/reference_segmenter/test_panel.cjs
docker exec label-studio python -m unittest reference_segmenter.test_neural reference_segmenter.test_learning reference_segmenter.test_processing reference_segmenter.test_http
```

홀수 크기·작은 이미지의 패치 복원, 이음새 없는 위치 복원, 전체 이미지의 학습 진입 거부, API의 패치 전용 데이터 로딩을 검증합니다.

## 배포

Dockerfile·Compose는 `reference_segmenter`를 사용합니다. `docker compose up -d --build label-studio`로 배포합니다. 호스트 번들을 마운트하는 경우 `python label_studio/third-party/reference_segmenter/patch_editor.py label_studio/overrides/358.js`를 실행합니다. 내부 DarkLine 식별자는 기존 번들 호환용입니다. 규칙 기반/Gaussian 코드는 회귀 검증용이고 패널 학습·예측에는 사용하지 않습니다.
