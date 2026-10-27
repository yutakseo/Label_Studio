# Gaussian pseudo 생성 코어 사본

Docker 빌드 컨텍스트가 `label_studio/`이므로 저장소 밖의 `__pseudo_labeller/02_pseudo_labeller`를 직접 import하지 않습니다. 그곳의 `config.py`, `processing.py`를 이 패키지에 포함해 동일 알고리즘을 사용합니다.

- `GaussianDifferenceConfig`: 커널·시그마·임계값·윤곽 면적 등 설정과 검증
- `GaussianDifferenceMaskMaker`: GaussianBlur → 원본 차이 → Otsu/고정 threshold → 윤곽 내부 채움
- `YoloSegmentationExporter`: 원본 배치 처리용 polygon 생성 클래스도 사본에 포함

[상위 확장](../README.md)은 생성 결과를 Label Studio RLE로 감쌉니다. 패키지 설정 클래스 기본값(커널 21 등)과 웹 API/배치 실행기 기본값(커널 101, σ10, 최소 면적 0)은 다를 수 있으므로 호출자가 넘기는 값을 확인하세요.

원본 알고리즘을 바꾸면 두 파일을 동기화하고 `gaussian_mask.test_processing`의 원본 해시·픽셀 동등성 테스트를 실행합니다. 테스트는 원본을 `/reference/02_pseudo_labeller`에서 읽을 수 있으며 [운영 문서](../../../../docs/OPERATIONS.md)에 마운트 명령이 있습니다. 함수·클래스 목록은 [CODE_MAP](CODE_MAP.md)을 참고하세요.
