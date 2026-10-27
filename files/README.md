# Local Files 데이터셋

컨테이너에서 이 폴더는 `/label-studio/data/files`입니다. 로컬 파일 document root는 `/label-studio/data`이므로 URL의 `d` 값은 `files/`로 시작합니다.

```text
files/<dataset>/
├── images/<case>/<camera>/<direction>/<exposure>/image.png
├── masks/<같은 상대 경로>/image.png
├── tasks.json
├── imports/tasks_001.json          # 있는 데이터셋만
└── label_config.xml
```

데이터셋에 따라 comparisons, pred_masks, cl_issue_masks, masks_original, overlays_gt, manifest.json 같은 보조 파일이 있습니다. 현재 최상위에는 P3_72_with_masks 및 날짜·시편 단위 데이터셋이 있고, 일부는 검증용/인장시편용 하위 데이터셋을 포함합니다. 촬영 조건별 폴더는 상대 경로를 보존합니다.

## 연결

1. 데이터셋 XML을 프로젝트 Labeling Interface에 적용합니다.
2. UI에서 tasks.json 또는 분할 JSON을 한 번 가져오거나, Local Files Source Storage를 사용합니다.
3. Source Storage 경로는 `/label-studio/data/files/<dataset>`, 파일 필터는 `.*\.json$`, `use_blob_urls=false`로 설정합니다.
4. 하위 imports JSON과 전체 tasks.json이 함께 존재하면 같은 태스크가 중복되지 않도록 등록 대상을 제한합니다. UI Import와 Sync도 중복 사용하지 않습니다.

태스크 예시:

```json
{"data": {"image": "/data/local-files/?d=files/my_dataset/images/sample.png"}}
```

한글·공백 등은 URL 인코딩을 사용하고 경로 구분 `/`는 보존합니다. `__pseudo_labeller/label_studio_formatting.py`가 만드는 기본 URL은 자체 출력 폴더를 root로 가정할 수 있으므로 이 Compose에 옮기면 `files/<dataset>/images/...` 기준으로 확인해야 합니다.

`masks/` PNG가 존재하는 것만으로 편집기에 마스크가 표시되지는 않습니다. tasks.json에 RLE annotation/prediction 결과가 있어야 합니다. P3는 [전용 스크립트](../scripts/README.md)로 생성합니다.

## Export와 보존

[트리 Export](../label_studio/third-party/mask_cleanup/tree_export/README.md)는 `images`의 상대 폴더를 유지하고 대응 `masks`를 새로 계산합니다. 기존 masks·imports·보조 그림을 그대로 복사하지 않습니다. 모든 라벨 원본은 ZIP의 `_annotations` JSON에 보관합니다.

데이터셋 폴더 이름을 변경하면 기존 DB 태스크의 URL도 영향을 받습니다. 폴더 이동 시 URL·저장소 경로·Sync 기록을 함께 관리합니다. 원본 데이터는 DB와 별도로 백업하며 일반 이미지·JSON은 Git 제외 대상입니다.
