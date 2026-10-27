# 전처리 단계별 데이터

현재 폴더에는 raw, extracted, cropped, labelled, labelstudio 단계의 날짜별 데이터셋이 있습니다. 각 단계는 코드의 `input_root`/`output_root` 또는 실행기 상수와 대응합니다.

| 단계 | 일반적인 내용 | 생성 코드 |
| --- | --- | --- |
| `(0)raw` | 원본 시편·카메라·방향·노출 트리 | 외부 취득 |
| `(1)extracted` | 지정 노출 mono 이미지 | 00_extract |
| `(2)cropped` | crops·ROI CSV·진단 영상 | 01_crop |
| `(3)labelled` | masks 및 outputs/YOLO txt | gaussian_batch_processor |
| `(4)labelstudio` | images/masks/tasks/imports/XML | label_studio_formatting |
| YOLO ZIP | Roboflow 업로드용 패키지 | yolo_formatting |

이름의 날짜·단계는 현재 데이터의 관례이며 스크립트가 모든 날짜 폴더를 자동 선택하는 것은 아닙니다. 실행기 상수를 확인하세요. 촬영 조건 하위 디렉터리는 원본 상대 경로이므로 별도 코드를 담지 않습니다. 이 폴더는 서버에 직접 마운트되지 않습니다. 최종 데이터셋을 루트 `files/`에 두고 URL을 현재 Compose 기준으로 연결합니다.

원본과 결과를 구분해 보존하고 재실행은 새 출력 경로를 권장합니다. `.DS_Store`, `__pycache__`는 데이터 처리 산출물에 필요하지 않습니다.
