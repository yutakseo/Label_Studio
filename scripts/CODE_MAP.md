# 코드 참조 · scripts

현재 소스에서 추출한 모듈·클래스·함수 목록입니다. 함수의 동작·사용 순서는 [README](README.md)를 참고하고, 실제 구현은 파일 링크에서 확인하세요. 테스트 파일은 검증 항목 탐색용입니다. 비공개 함수도 디버깅 경로를 찾을 수 있도록 포함했습니다.

## [add_p3_original_comparison.py](add_p3_original_comparison.py)

Run inside Label Studio: add the preserved P3 masks as comparison predictions.

모듈 초기화·설정·재노출 또는 파일 패치용 top-level 코드입니다. import 자체가 설정·파일·DB 변경을 수행할 수 있으므로 실행 전에 원본을 확인하세요.

## [prepare_p3_tasks.py](prepare_p3_tasks.py)

Build editable Label Studio tasks from the P3 images and GT alpha masks.

- `main()`
