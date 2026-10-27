# U-Net 패치 pseudo 라벨링

원본을 리사이즈하지 않고 256×256 패치를 128픽셀 간격(50% 중첩)으로 추론합니다.
패치별 sigmoid 확률에 중앙을 강조하는 Hann 가중치를 곱해 누적하고,
가중치 합으로 나눈 후 마지막에 임계값을 적용합니다.
이미지 가장자리도 패치 중앙의 예측을 받도록 원본 주변 128픽셀을 반사 패딩합니다.
최종 마스크는 원본 크기로 잘라 BrushLabels RLE로 저장합니다.
입력은 Pillow 흑백 변환 후 `uint8 / 255`, 출력은 단일 채널 logits입니다.
이미지 테두리와 4방향으로 연결된 값 0의 검정 여백을 제외합니다. 시편 내부의 닫힌 검정 영역은 유지합니다. 시편의 외접 박스를 추출하고 박스 내부의 외부 여백은 가장 가까운 시편 픽셀로 채워 인공적인 검정 경계 없이 추론합니다. 이후 원본 좌표로 복원하고 외부 여백의 마스크만 0으로 만듭니다. 이 기능은 정확히 0인 여백을 대상으로 하며, 실제 시편의 값 0 영역이 영상 테두리까지 연결되면 여백으로 간주될 수 있습니다. 모델 자체의 오검출은 남을 수 있습니다.

## 학습 모델 연결

제공받은 학습 모델을 `model.py`에 포함했습니다. GroupNorm(8그룹), ReLU,
max pooling, bilinear 업샘플링(`align_corners=False`)을 원본과 동일하게 사용합니다.
학습 전용 loss import와 평가 지표 클래스는 추론에 필요하지 않아 포함하지 않습니다.

`best.pt`의 `grayscale_unet`, `base_channels`, 입력 정규화를 검사하고
`model_state_dict`를 `strict=True`로 로드합니다. 기본 임계값은 0.5이며
학습 대상 라벨은 `Exposure`입니다. 외부 모델/가중치 다운로드는 없습니다.
다른 모델은 CLI `--model-file`로 `build_model(checkpoint)` 팩토리를 제공할 수 있습니다.

## Label Studio에서 사용

```sh
docker compose up -d --build label-studio
```

실행 중인 편집 내용을 먼저 저장하세요. 이미지는 glibc 기반 Debian/Python 3.12에서 Label Studio 1.23.1과 CUDA 12.6용 PyTorch를 설치합니다. 기존 Alpine/musl 이미지는 NVIDIA 드라이버 라이브러리를 로드할 수 없어 사용하지 않습니다. Compose는 NVIDIA GPU 0을 컨테이너에 연결합니다.
태스크를 연 후 오른쪽 아래 **라벨링 도구 → U-Net pseudo 라벨링** → 대상 이미지·라벨 선택 → **미리보기** → **U-Net 탭에 저장**을 누릅니다. 창은 Label Studio의 현재 테마를 따릅니다. 미리보기에서 **원본 / 예측 마스크**를 전환해 비교할 수 있으며 하단의 저장·닫기 버튼은 항상 보입니다. 저장 후에도 미리보기와 완료 안내를 유지합니다.
새로고침 후 상단 **U-Net** 예측 탭에서 결과를 확인합니다. 다시 저장하면 해당 태스크의 U-Net 예측을 갱신합니다. 기존 수동 어노테이션과 다른 모델 예측은 유지합니다. 빈 마스크도 예측으로 저장할 수 있습니다.
라벨은 학습 대상(`Exposure`)에 맞게 선택하세요. Image + BrushLabels 설정, HTTP(S)로 브라우저에서 읽을 수 있는 이미지가 필요합니다.
외부 URL은 CORS 허용이 필요합니다. 최대 1600만 픽셀·32MB·회전 없는 단일 프레임을 지원합니다.
Compose 기본값은 `UNET_DEVICE=cuda:0`, `UNET_BATCH_SIZE=16`이며 동시 추론은 직렬 처리합니다. GPU 메모리가 부족하면 배치 크기를 8 또는 4로 낮추세요. 명시적으로 CUDA를 지정했는데 사용할 수 없으면 오류를 표시합니다. 모델 파일/가중치 교체 후 서버를 재시작하세요.

## CLI

```sh
python label_studio/third-party/u_net_labeller/interface.py original.png mask.png --batch-size 4
```

`--model-file`, `--weights`, `--threshold`, `--device`를 지정할 수 있습니다.
CLI 기본 장치는 `auto`로 GPU를 우선 선택합니다. `--device cuda:0`으로 GPU를 지정하거나 `--device cpu`로 CPU를 선택할 수 있습니다. CLI 기본 배치는 4이며 `--batch-size 16`으로 조절합니다.

## 검증

```sh
PYTHONPATH=label_studio/third-party python -m unittest u_net_labeller.test_interface -v
node --check label_studio/third-party/u_net_labeller/panel.js
```

좌표 복원·배치 잔여분·패딩·입출력 검증 및 CUDA와 CPU 결과 일치 테스트입니다. CUDA가 없는 환경에서는 GPU 테스트만 건너뜁니다. 실제 가중치 로딩과 GPU 64패치 추론도 확인했습니다. 예측 품질은 실제 영상과 정답 마스크로 별도 평가해야 합니다.

## 예측 수정

예측 탭은 읽기 전용입니다. 미저장 작업을 먼저 저장한 뒤 오른쪽 아래 **라벨링 도구 → U-Net 마스크 수정**을 누르면 해당 예측을 새 어노테이션으로 복사합니다. 새로고침 후 본인 이름의 새 어노테이션 탭을 선택해 브러시로 수정하고 Update로 저장하세요. 예측 원본과 기존 어노테이션은 유지됩니다. 버튼을 다시 누르면 새 복사본이 생성됩니다.

## 코드 탐색

- `interface.py`: 입력 검증, 외부 검정 여백 처리, 패치 좌표·반사 패딩·Hann 합성, 모델 캐시·CLI
- `model.py`: 체크포인트와 호환되는 grayscale U-Net 및 모델 생성
- `views.py`: 로그인·CSRF preview, 환경변수 장치/배치 설정과 직렬 추론
- `panel.js`: 이미지·라벨 선택, preview, U-Net prediction 저장·수정용 annotation 복사
- `install.py`: mask_cleanup URL/미들웨어에 U-Net 경로와 패널 등록
- `best.pt`: 운영 가중치, Git 제외 대상이며 새 환경에 별도 전달 필요

전체 함수와 테스트는 [CODE_MAP](CODE_MAP.md)을 참고하세요. `--help`로 현재 CLI 옵션을 조회할 수 있습니다. 본 모델 추론과 Reference Segmenter의 64px 온라인 학습은 모델·패치 크기·저장 경로가 서로 다릅니다.
