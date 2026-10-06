# 멘토 가이드 직접 VLM 상태 추정 구현

이 디렉터리는 기존 `full_pipeline_v3`와 다른 **mentor-direct-v1** 실험이다.
기존 코드/캐시/모델을 덮어쓰지 않고, 원래 MLP로 대체했던 테스트 상태 추정에 실제 이미지 입력 VLM을 연결한다.

## 완료한 실행 결과

- R01/R04 각각 normal fit72 / normal calibration32, 테스트125/264관측, 모든 eligible 녹화 stride32.
- 같은597관측의 기본/정상참고 버전2개에서 **실제 VLM 추정1,194건**, 별도 MP4 end-to-end12건(버전별6건).
- 정상 PCA/전이 모델4개 scene-run fitting, 정상 특징 AE4개×10에포크 gradient 학습.
- 12개 offline 계약 테스트, 4scene-run 전체1,194관측 저장모델 replay에서 score 허용오차 및 alarm 일치 확인.
- 같은 조건 AUROC: phase 미사용 visual69.59%, 직접VLM+phase+process Full65.06%, 정상참고 추가 Full64.53%.
- 따라서 **모듈 실행은 완료했지만 성능 향상은 확인되지 않았다.** 기존 v3/advanced 기본 모델을 교체하지 않았다.
- 기존 승인 누적$4 안에서 비용 추정$1.0995. 실패/미확인 예약액은 유지했다. 실청구서 금액은 별도다.

상세 결과: [두 버전 비교](../../output/mentor_direct_comparison_20261005/COMPARISON.md),
[기본 버전 지표](../../output/mentor_direct_20261005/RESULTS.md),
[정상참고 버전 지표](../../output/mentor_direct_reference_20261005/RESULTS.md).
사람 state/phase 정답이 없어 VLM 추정 정확도는 미입증이다. R04의4phase 공간은 모두 fit했으나 R01의 phase0/1은8개미만이라 global fallback이다.

## 가장 중요한 차이

- 이전 v3: GPT 정상 객체·단계 초안 → CLIP 특징 → 학습한 MLP phase → 코드 규칙.
- 이 버전: GPT 정상 객체·단계 초안 → 실제 GDINO/ByteTrack + CLIP 특징 → **현재 전체 이미지·객체 crop·과거 이미지 입력 GPT의 phase/object state 추정** → **GPT의 직접 consistency 판단 + 정상 영상으로 추정한 전이 확률**.
- API 오류/미완성 응답에 MLP 결과를 대신 넣지 않는다. 검증된 실제 응답이 없으면 실행을 중단한다.
- GPT가 불확실하다고 답한 관측은 phase unknown/global visual fallback이다. 판단 불가는 정상 인증이 아니다.

## 가이드 1~13 대응

| 단계 | 구현 | 실제 기능과 제한 |
|---|---|---|
| 1 Normal videos | `data.py`, `model.fit` | 정상72 fit / 별도 정상32 cal, 녹화 분리. 이상 라벨 학습 사용 없음 |
| 2 VLM/LLM | `data.GRAMMARS` | 기존에 실제 GPT-5.4가 정상3영상×12이미지로 생성한 원본 grammar 재사용. 고정 SPECS 수정 없음. 사람 정답 검증 없음 |
| 3 GDINO+Tracking | `run.extract`, 기존 `ObjectExtractor` | 새 vocabulary로 전체 선택 프레임 새 검출·class별 ByteTrack 추적. 이전 객체 캐시 재사용 안 함 |
| 4 Object VLM encoder | `ObjectExtractor.step` | frozen CLIP ViT-B/16 full512 + 개별 crop512. 동시에 아래 GPT 경로가 상태 텍스트 추정 |
| 5 Process model | `model.fit_process` | 직접 VLM 정상 phase의 전이 count/확률 fitting. 정상 grammar와 과거 상태를 GPT에게 제공 |
| 6 Phase subspaces | `model.fit` | VLM이 직접 추정한 phase별 정상 PCA. 8개 미만 global fallback, 99% 분산 유지 |
| 7 Test video | `data.prepare`, `infer.py` | R01/R04 모든 strict-eligible 테스트 녹화. ZIP 프레임 및 MP4 입력 지원 |
| 8 Sampling | `data.prepare`, `infer.py` | 테스트 stride32. 과거2화면+3상태만 사용하며 미래 입력 없음 |
| 9 GDINO+Tracking | `run.extract`, `infer.py` | 학습과 같은 vocabulary/검출/추적 설정, 녹화마다 ID reset |
| 10 Crops/trajectories | `features.npz`, `detections.json` | 개별 crop, bbox, ID, 위치/크기/이동량 보존. GPT에는 confidence순 최대4crop 제공 |
| 11 VLM state | `semantics.assess` | **매 선택 관측 실제 GPT-4.1-mini 이미지/crop API**. phase, confidence, ID별 visible/state 추정. MLP proxy 없음 |
| 12 Visual score | `model.score_observation` | 해당 VLM phase의 정상 residual. frame/crop+geometry 각각 채점. unknown/부족한 공간 global fallback |
| 13 Semantic score | `semantics.assess`, `model.Process` | GPT가 normal spec와 past/current evidence의 일치/위반/판단불가를 직접 출력. 정상-fitted 전이 surprisal 보조 |
| 결합/위치 | `model.aggregate`, `infer.py` | normal-cal scale, visual80%+process20%, 정상cal q99. residual이 큰 객체 bbox 후보 출력, 검증된 defect mask 아님 |

9번에서 GPT가 필요 없다는 설명은 **객체 검출 자체**를 뜻한다. 이 버전은11/13번에서 실제 GPT를 호출한다. 전체 추론이 API-free라는 뜻이 아니다.

## 직접 추정의 정확한 의미

GPT-4.1-mini는 텍스트만 받는 LLM처럼 쓰는 것이 아니라 **이미지를 받는 멀티모달 VLM**으로 사용한다.
CLIP image encoder는 숫자 embedding `z`를, 이미지 입력 GPT는 semantic descriptor와 consistency를 담당한다.
외부 API의 내부 embedding을 꺼냈다고 주장하지 않는다. 각 모듈을 나눠 구성한 frozen VLM 경로다.

정상 grammar는 GPT-5.4 원본이며, 새로운 실행에서 비용을 들여 동일한 객체 목록을 재생성하지 않는다.
실제 API receipt와 grammar SHA가 원본을 증명한다. 사람 검토가 없으므로 **machine-proposed** 설정이지 공정 정답이 아니다.

## 학습 범위

1. 정상 CLIP full/crop 특징으로 PCA normal space fitting (에포크 없음).
2. 정상 VLM phase로 transition probability fitting (에포크 없음).
3. normal calibration으로 score scale/q99 threshold 추정 (에포크 없음).
4. 비교용 CLIP frame feature AE를 장면당10에포크 실제 gradient 학습.

멘토가 encoder freeze를 허용했으므로 CLIP/GDINO/GPT의 가중치는 수정하지 않는다.
AE는 학습 비교용이며 mentor Full에 포함하지 않는다. **GPT를 새로 학습했다고 표현하면 안 된다.**

SubspaceAD의 정상 PCA reconstruction residual 아이디어를 참고한다. 논문의 DINO patch feature/전체 pixel평가를 정확히 재현한 것은 아니다.

## 실행

프로젝트 workspace에서 기존 `.venv`와 로컬 pretrained model 캐시가 필요하다. API 키는 ignored `.env.local` 또는 환경변수에서만 읽는다.
로그/소스에 key를 출력하지 않는다. 기존 키 loader를 사용하며 새 키 생성/외부 업로드는 하지 않는다.

```powershell
& '.\.venv\Scripts\python.exe' -m local_experiments.mentor_pipeline.tests
& '.\.venv\Scripts\python.exe' -m local_experiments.mentor_pipeline.run --prepare-only
& '.\.venv\Scripts\python.exe' -m local_experiments.mentor_pipeline.run --extract-only
# 유료 이미지 추론. 승인 누적 $4 ledger를 넘으면 중단한다.
& '.\.venv\Scripts\python.exe' -m local_experiments.mentor_pipeline.run --paid --workers 3
# 별도 동일조건 비교: 정상FIT3이미지와 원본 summary/uncertainties 추가.
& '.\.venv\Scripts\python.exe' -m local_experiments.mentor_pipeline.run --normal-reference --paid --workers 2
# 모든 accepted response가 있으면 아래 명령은 API 없이 재평가 가능.
& '.\.venv\Scripts\python.exe' -m local_experiments.mentor_pipeline.run
# 새 raw inference: 실제 API 호출, test labels 읽지 않음.
& '.\.venv\Scripts\python.exe' -m local_experiments.mentor_pipeline.infer --scene R01 --clip 01 --limit 6 --paid --out 'output/mentor_direct_20261005/raw_smoke_R01'
# 작은 MP4 입력의 실제 end-to-end 직접 VLM smoke (원본FPS 주장 아님).
& '.\.venv\Scripts\python.exe' -m local_experiments.mentor_pipeline.smoke --paid
# 두 버전 모두 완료한 뒤 수치/정상cal/직접응답/녹화 bootstrap 검증.
& '.\.venv\Scripts\python.exe' -m local_experiments.mentor_pipeline.compare_runs
```

출력: `local_experiments/runs/mentor_direct_20261005`에 private weights/features/accepted responses,
`output/mentor_direct_20261005`에 결과 지표와 숫자 보고서.
정상참고 이미지 버전은 별도 `mentor_direct_reference_20261005` 경로다.
이 디렉터리의 소스는 versioned 코드이며 결과 숫자는 실행 완료 후에만 생성한다.

## 실험 해석 주의

- 같은 새로운 normal-fit/cal/stride32 조건의 global/phase/semantic ablation끼리 비교한다.
- 기존 v3의 R01~R04 stride4 평균72.08, advanced의16장면 평균73.10과 직접 우열 비교하지 않는다.
- AUROC는 정확도가 아니다. frame FPR과 지속경보 FPR은 별도로 출력한다.
- 32프레임 사이의 이상/중간 동작은 관측되지 않을 수 있다. sampling만으로 skipped_step을 선언하지 말라고 프롬프트에 명시했다.
- normal fit/cal은 각 녹화의24/16균등 위치, test는stride32라 전이 관측 간격이 같지 않다. 전이 surprisal은 시간간격을 정규화하지 않은 pilot 보조항이며 cadence의 영향을 받을 수 있다.
- 영상 입력에서 정상참고 버전 모델/프롬프트를 쓰려면 `infer --normal-reference`를 추가한다. API model state는 매 관측 직접 새로 추정한다.
- 좁은 normal fit/cal, 과거 확인한 테스트, 사람 phase/bbox/ID/defect GT 없음 때문에 범용성·설명 정확도·현장 성공은 미입증이다.
- 원본 FPS가 없으므로 frames를 초 단위로 바꾸거나 시간당 false alarm/실시간30FPS를 주장하지 않는다.
- 더 충실하게 모듈을 구현했다고 성능이 높아진다고 보장하지 않는다.

## 보안/비용

6개의 과거 completed receipt에서 확인된 사용량만 정산하고 실패/미확인 예약액은 유지한다.
매 API 호출 전 UTF-8 text/schema byte 상한 + 실제 이미지 patch token 상한 + output600 cap을 예약한다.
completed usage가 있으면 해당 호출의 예약을 사용량 추정액으로 정산한다. 실패 응답은 자동 재시도하지 않는다.
응답이 없는 연결 실패만 `--recover-transport-once`로 한 번의 명시적 환경 복구가 가능하다.
기존 실패/예약액과 별도 recovery receipt를 보존하며 HTTP/API 응답 오류나 잘못된 상태 추정에 무조건 재시도하지 않는다.
기존 key를 재사용하며 정상/테스트 공개 IPAD 이미지·crop을 OpenAI API로 전송한다. `store=false`이며 no-training privacy 보증과 혼동하지 않는다.

참조: [OpenAI 이미지 입력](https://developers.openai.com/api/docs/guides/images-vision),
[GPT-4.1-mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini),
[Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs),
[SubspaceAD](https://arxiv.org/abs/2602.23013).
