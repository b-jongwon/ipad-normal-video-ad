# 이번 GitHub 업데이트의 확인 기록

날짜:2026-10-05. 기존 실험 결과를 문서화/공개한 작업이다. 이 문서 작성 중 새로운 신경망 학습이나 유료 API 호출은 하지 않았다.

## 공개할 코드에서 다시 실행한 테스트

| 실행 모듈 | 검사 수 | 결과 |
|---|---:|---|
| `local_experiments.tests.test_protocol` | 4 | 통과 |
| `local_experiments.full_pipeline.tests` | 12 | 통과 |
| `local_experiments.advanced_pipeline.tests` | 11 | 통과 |
| `local_experiments.pipeline_audit.tests` | 6 | 통과 |
| 합계 | **33** | 통과 |

기존 로컬 `.venv`의 Python을 사용하되 작업 경로는 GitHub에 올릴 checkout이었다. 새 컴퓨터 fresh install 또는 실제 이상 탐지 정확도의33개 평가가 아니다. Matplotlib 관련 dependency deprecation warning은 있었지만 테스트 실패는 없었다.

## 파일·수치 감사

- Python60개 소스 AST parsing 통과.
- JSON syntax와 Markdown 상대 파일 링크 검사 통과.
- README의 기존v3 18개 method AUROC/FPR와 고도화all16 11개 method AUROC/AP/alarmFPR/F1을 원본표와 대조,29행 일치.
- 초기 CSV248행,epoch0 반복 제외support176행,summary44개 확인. 평균을support에서 재계산해 일치 확인.
- 기존v3 72행/18구성,주고도화580행/208head,추가48행/24head의 원본 검사 결과 확인.
- 생성한 training_history CSV의 고유232head 확인. epoch별 normal fit/tune loss와 LR 포함.
- raw stress16건/oracle99건/AI참고48프레임의 원본 최종기록 확인.
- 일반 OpenAI/GitHub secret 형태 검사에서 key pattern 발견 없음. 원 API키/개인 메모장/환경파일/캐시/원데이터를 새 공개하지 않음.
- 새로 추가한 dataset-derived JPG/MP4,ZIP,weights/NPY/NPZ/safetensors 없음. 성능PNG는 수치 기반 그래프만 허용.
- 원본 복사 항목은 [manifest](PUBLICATION_MANIFEST.json)의 local SHA256과 대조. Git text 줄바꿈 정규화 때문에 다른 checkout의 byte SHA는 달라질 수 있음.

이 감사는 자격증명/금지파일의 일반 패턴·범위 검사이지 모든 종류 secret를 수학적으로 증명한 보안감사가 아니다. 기존 비공개 시절 이미지/시연/Release를 자동 삭제하지 않았고, 별도 공개 재배포 조건 확인이 필요하다.

공개 상태 및 원격 커밋/README blob도 push 후 별도로 확인한다. 커밋SHA는 자기참조 문서에 고정하지 않고 Git 이력과 원격 확인 receipt에 기록한다.
