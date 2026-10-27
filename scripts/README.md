# P3 데이터 준비 스크립트

범용 프로젝트 CLI가 아니라 `files/P3_72_with_masks`와 `P3-Masking`을 대상으로 하는 작업 스크립트입니다. 전체 함수는 [CODE_MAP](CODE_MAP.md)을 참고하세요.

## prepare_p3_tasks.py

manifest의 파일 목록·capture 수, images/masks 파일 집합, SHA-256, 256×256 크기, GT 픽셀 수를 확인합니다. RGBA는 alpha, grayscale L은 픽셀 값을 사용해 `>0` 이진 마스크로 변환합니다. `__pseudo_labeller/label_studio_formatting.py`의 RLE 인코더를 재사용합니다.

출력은 편집 가능한 Exposure annotation을 담은 `tasks.json`과 `label_config.xml`입니다. 이미지 URL은 `files/P3_72_with_masks/images/...`입니다. 기존 출력 파일을 덮어쓰므로 입력·경로를 확인한 뒤 실행합니다.

```bash
python scripts/prepare_p3_tasks.py
```

NumPy와 Pillow가 필요하며 원본 데이터셋과 manifest가 있어야 합니다. 생성 후 프로젝트 XML 적용과 tasks Import를 수행합니다. 이 스크립트 자체는 DB에 연결하지 않습니다.

## add_p3_original_comparison.py

**DB를 변경합니다.** 컨테이너 Django 환경에서 `P3-Masking` 프로젝트의 태스크를 조회하고 72개인지 확인합니다. 파일명으로 원본 결과를 대응시켜 `model_version=mask_original` prediction을 update_or_create하고 total_predictions를 맞춥니다.

이 비교 탭은 일반 Export에서 제외됩니다. 저장된 사용자 annotation은 유지합니다. 먼저 DB 백업과 대상 프로젝트를 확인하세요. 호스트 scripts 폴더는 Compose에 마운트되어 있지 않아 stdin으로 전달할 수 있습니다.

```bash
docker exec -i label-studio python < scripts/add_p3_original_comparison.py
```

프로젝트명·태스크 수·파일명이 다른 데이터에 그대로 사용하지 않습니다. import 시점에 실행되는 코드이므로 단순 모듈 탐색용 import도 DB 작업을 수행합니다.
