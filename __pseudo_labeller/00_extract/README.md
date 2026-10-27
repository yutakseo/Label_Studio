# 노출 조건별 mono 이미지 추출

`extract_mono.py`는 입력 트리를 재귀 순회하여 부모 폴더 이름이 지정 노출명이고 파일명이 `mono_`로 시작하는 이미지들을 출력 트리에 복사합니다. 대소문자를 구분하지 않으며 bmp/jpeg/jpg/png/tif/tiff를 지원합니다. 상대 경로와 파일 메타데이터를 유지합니다.

```bash
python __pseudo_labeller/00_extract/extract_mono.py \
  --source /path/to/raw \
  --output /path/to/extracted \
  --exposure 10000us
```

source 생략 시 `__data/20260918_(0)raw`를 Unicode NFC 정규화 이름으로 찾습니다. 기본 출력은 `20260918_(1)extracted`입니다. 노출값은 파일명 일부가 아니라 **바로 위 폴더명**과 비교합니다.

`ExtractionConfig.validate`는 입력 폴더, 빈 노출/접두어, 입력=출력, 입력 내부 출력 경로를 거부합니다. `MonoExtractor.selectPaths/isTarget`은 선택, `copyOne`은 `shutil.copy2`, `extract`는 전체 처리를 담당합니다. 동일 출력 경로의 기존 파일은 복사로 덮어쓸 수 있으므로 별도 출력 폴더를 사용합니다.

라이브러리 사용과 전체 시그니처는 [CODE_MAP](CODE_MAP.md)을 참고하세요. 이 단계는 ROI·마스크를 생성하지 않습니다.
