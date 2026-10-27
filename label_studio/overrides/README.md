# 서비스에 마운트하는 프런트엔드 번들

`167.js`, `358.js`, `runtime.js`는 Label Studio 1.23.1 웹 빌드 자산입니다. Compose가 각 파일을 컨테이너의 `/label-studio/web/dist/apps/labelstudio/`에 읽기 전용 마운트합니다.

| 파일 | 이 저장소에서의 역할 |
| --- | --- |
| `358.js` | 이미지 편집기, 브러시·지우개·펜·확장 도구·사용자 탭 패치 대상 |
| `167.js` | 데이터 매니저 태스크 로딩 후 최신 결과 선택 패치 대상 |
| `runtime.js` | 해당 웹 빌드의 청크 로딩 런타임 |

압축 번들을 손으로 재작성하지 않고 `patches/*.py`, `mask_cleanup/patch_editor.py`, `reference_segmenter/patch_editor.py`로 수정합니다. 패치 전 파일 백업과 적용 후 `node --check`를 수행합니다. 구체적인 순서는 Dockerfile과 [패치 문서](../patches/README.md)를 확인하세요.

이 폴더는 기존 Git 제외 대상입니다. 번들이 없는 새 환경에서는 [상위 문서](../README.md)의 이미지 자산 추출 절차를 사용합니다. Docker 재빌드는 호스트 파일을 자동 갱신하지 않습니다. JS 반영 후 브라우저를 강력 새로고침합니다. 새 Label Studio 버전의 청크 이름이 같더라도 코드 계약이 같다고 보장하지 않습니다.
