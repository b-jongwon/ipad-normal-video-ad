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
## E07 후속 공개 확인

2026-10-05 후속은 [추가 manifest](IMPROVEMENT_PUBLICATION_MANIFEST.json)에 allowlist와 SHA를 기록했다. source/numeric artifact78개와 수동 narrative 변경이며 새 raw/fixture 영상,weights,feature 배열,API key는 없다.

- 신규 기능 테스트10개 통과.
- memory/covariance32개 모델 finite/정상분할/normal quantile 확인.
- 6,558관측 직렬화 replay: relative+absolute tolerance 통과,경고값 모두 동일. 완전 bitwise 동일 아님.
- v3 live guard161관측: 이전 score 보존 tolerance 통과,normal certification0개.
- R01/R04 일부 DINO backbone 가중치 실제 변경 확인,best 정상 tune checkpoint.
- normal MP496관측 fit/cal +24관측 infer smoke. 실제 새 공장 holdout 아님.
- 공개 전체 Python73파일 syntax/JSON/Markdown link/기존 수치와 신규allowlist 검사 통과. secret 검출0개.
- 이전 모델보다 좋지 않았던 결과와 형식 검증에 실패한 유료 응답도 문서화. 기본 model 교체 없음.
