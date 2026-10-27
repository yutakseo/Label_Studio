# 서버 영속 데이터

Compose에서 `/label-studio/data`로 마운트합니다. **이 폴더는 실행 데이터이며 소스가 아닙니다.** 구조만 설명하고 DB 레코드·환경변수 값은 이 문서에 복사하지 않습니다.

| 위치 | 내용 |
| --- | --- |
| `label_studio.sqlite3` 및 WAL/SHM | 계정·프로젝트·태스크·annotation·prediction·초안 |
| `.env` | 인스턴스 설정·비밀값, 공개/커밋 대상 아님 |
| `media/upload/` | UI Import로 업로드한 파일 |
| `export/` | 과거 내보내기 파일·작업 결과 |
| `mask-revisions/<task>/...` | annotation/draft 변경·삭제 전 JSON |
| `reference_segmenter/<project>/...` | 클래스별 모델·수정 패치·평가 자료 |
| `backups/`, `path-repair-backup-case3/` | 이전 백업·경로 수정 작업 산출물 |
| `test_data/` | 현재 테스트용 자리 |
| `files/` | 호스트 files가 덮어 마운트되는 위치, 실제 원본은 루트 files |

## 참고 모델 저장 구조

현재 공유 경로는 `reference_segmenter/<project>/shared/<hash>/`입니다. hash는 BrushLabels 이름·이미지 이름·라벨의 조합으로 계산합니다. 디렉터리 안에는 `<hash>.pt`, `.previous.pt`, `.json`, `.samples/corrections/`, `.samples/validation/` 등이 있습니다. 이전 사용자 ID 폴더와 과거 학습·평가 결과도 남아 있을 수 있습니다. 현재 학습은 `corrections`의 64px 수정 패치만 사용합니다.

구체적인 채택·잠금·재학습 규칙은 [Reference 문서](../third-party/reference_segmenter/README.md)를 참고하세요. 탐색 당시 일부 공유 하위 폴더는 호스트 사용자 권한으로 열 수 없어 내부 파일을 확인하지 못했습니다. [탐색 기록](../../docs/DIRECTORY_INVENTORY.md)에 이를 구분합니다.

## 운영

DB만 지우거나 폴더 일부를 바꾸면 원본 URL·모델 메타데이터와 불일치할 수 있습니다. 변경 전 일관된 백업을 만들고, 보관 정책에 따라 이력·모델·export를 정리합니다. 보존 기간 자동 정리 기능은 이 폴더의 존재만으로 제공되지 않습니다. [백업 및 복구](../../docs/OPERATIONS.md)를 따르세요.
