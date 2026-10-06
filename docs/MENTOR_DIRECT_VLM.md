# 실제 이미지 입력 VLM으로 멘토 파이프라인을 수행한 실험

문서 갱신: **2026-10-06**. 실행 식별자는 시작 당시의 `mentor_direct_20261005`와 `mentor_direct_reference_20261005`를 유지한다.

## 1. 먼저 결론과 범위

이 실험은 **이전 v3에서 MLP가 담당하던 테스트 단계 추정을 실제 이미지 입력 VLM으로 교체**하고, 멘토가 제안한 객체 중심·단계별 정상 공간·공정 일치 판단을 함께 연결한 별도 경로다. 기존 v3/advanced/E07의 모델과 결과는 덮어쓰지 않았다.

완료한 것:

- R01/R04의 정상 영상으로 정상 기준 fitting 및 비교용 AE 학습.
- 모든 선택된 정상FIT/calibration/test 관측에서 실제 VLM 객체 상태·phase·공정 일치 여부 추론.
- 기존 원본 GPT grammar에 맞춰 GroundingDINO/ByteTrack/CLIP을 다시 실행.
- 기본/정상참고 두 버전, 각10방법×2장면으로 **40개 지표 행** 산출.
- 12개 offline 계약 검사, 저장 모델1,194관측 replay, 실제 MP4 입력12관측 실행 확인.

완료하지 않은 것:

- VLM 자체 fine-tuning, 모든16장면에 대한 이 경로 평가, 새로운 공장 일반화 검증.
- 사람이 확인한 phase/state/bbox 정답을 이용한 의미 정확도 평가.
- 검증된 결함 위치/분할 성능, 현장 장시간 오경보/실시간성 측정.
- 현재 결과보다 높은 성능을 내는 개선 모델의 확정.

**구현 완료와 정확도 입증은 다르다.** 동일조건 평균 AUROC는 global visual69.59%, 멘토Full65.06%, 정상참고Full64.53%였다. Full을 기본 배포 모델로 교체하지 않았다. 낮은 결과도 그대로 공개한다.

## 2. 이전 v3와 무엇이 달라졌나

| 항목 | 기존 `full_pipeline_v3` | 새 `mentor_pipeline` |
|---|---|---|
| 정상 객체·단계 후보 | GPT 초안 및 기존 검토 경로 | 실제 GPT-5.4 원본 grammar 재사용, 고정 SPECS 덮어쓰기 없음 |
| 현재 단계 추정 | CLIP 특징을 입력받은 phase MLP | 실제 현재 화면/crop/과거 화면을 입력받은 GPT-4.1-mini |
| 공정 순서 판단 | MLP phase에 코드 규칙 적용 | VLM 직접 consistency/위반 추정 + 정상에서 fitting한 전이 확률 |
| 수치 시각 특징 | frozen CLIP/DINO 경로 | frozen CLIP ViT-B/16 화면·개별crop |
| Full 결합 | v3의 visual/GRU/process 결합 | phase visual80% + process20% |
| 비교용 AE | v3 구성별 비교 | 정상 화면 특징10ep AE, **새 Full에는 미포함** |
| 실험 범위 | R01~R04, 기본 stride4 | R01/R04, 테스트 stride32, 작은 정상FIT/cal |

새 경로를 이전의72.08% 또는16장면 고도화73.09%와 직접 비교해 "더 좋아졌다/나빠졌다"고 판단하지 않는다. 표현, 분할, 샘플 수, 간격과 평가 장면이 다르다.

### LLM과 VLM의 실제 역할

여기서 GPT-4.1-mini는 텍스트만 처리하는 방식이 아니라 **이미지 입력 멀티모달 VLM**으로 사용한다. 입력은 정상 specification, 현재 전체 화면, 최대4개 현재 객체 crop, 과거2개 화면, 과거3개 상태 요약이다. 미래 테스트 화면이나 anomaly 정답을 넣지 않는다.

반환값은 현재 phase, 정성적 confidence, 각 공급된 crop ID의 visible/state, consistency, 위반 종류, 짧은 이유다. phase MLP의 예측을 답으로 대신 넣거나 프롬프트에 공급하지 않는다. API 실패에 조용히 MLP로 대체하지 않는다.

CLIP은 수치 embedding `z`를 담당한다. GPT는 의미 descriptor와 공정 일치 추정을 담당한다. **GPT API 내부 embedding을 추출했다거나 CLIP이 상태 문장을 생성했다고 주장하지 않는다.** 서로 다른 동결 모듈로 역할을 나눴다.

## 3. 데이터·샘플링·분할

| 장면 | 정상FIT | 정상calibration | Test | 두 버전 각각의 VLM 관측 |
|---|---:|---:|---:|---:|
| R01 | 72 | 32 | 125 | 229 |
| R04 | 72 | 32 | 264 | 368 |
| 합계 | 144 | 64 | 389 | **597** |

숫자는 **선택된 영상 시점 수**다. 정상72는 정상 영상72편이라는 뜻이 아니다. 원 GPT grammar에 사용한 정상3녹화에서24시점씩, 별도 정상2녹화에서16시점씩 선택했다. 정상FIT/calibration은 녹화 단위로 분리한다.

테스트는 해당R01/R04 strict-eligible 녹화의 ordinal32배수 시점이다. anomaly label의 값으로 표본을 선택하지 않는다. 두 버전은 같은597시점을 사용했다. 597×2=1,194번의 실제 직접 VLM 응답이지만, **독립1,194시점 데이터가 아니다.**

현재의 제한:

- 정상FIT/calibration은 녹화별 균등24/16시점이고 test는 stride32다. 관측 간격이 동일하지 않다.
- 원 IPAD 영상 FPS를 확인하지 못해32프레임을 몇 초라고 변환하지 않는다.
- 정상CAL32관측의 q99는 극단 분위수 추정에 작은 표본이다. 인접 관측의 상관성도 있다.
- 이 테스트는 이전 개발에서 이미 확인했다. **사후 탐색 결과이며 독립 최종 평가가 아니다.**

## 4. 멘토1~13단계에서 실제로 한 일

| 번호 | 목적 | 실제 구현 | 남은 제한 |
|---|---|---|---|
| 1 | 정상 영상으로 기준 확보 | `data.prepare`: normalFIT72/cal32, 녹화 분리 | 정상 분포 전체를 대표한다고 보장하지 않음 |
| 2 | 객체 vocabulary/정상 grammar | 실제 GPT-5.4 정상3녹화×12이미지 생성 원본 재사용, SHA 기록 | machine-proposed, human_verified=false |
| 3 | 관심 객체 검출·연결 | `run.extract`, `ObjectExtractor`: 새 vocabulary로 GDINO tiny + 종류별 ByteTrack | bbox/ID 의미 정확도 미검증 |
| 4 | 객체 중심 수치·의미 표현 | 화면512차원/개별crop512차원 CLIP, 별도 GPT descriptor | encoder 동결; GPT embedding 추출 아님 |
| 5 | 정상 공정 일치 모델 | 정상 VLM phase 전이 빈도·Laplace0.5 smoothing, grammar/past context | 실제 시간간격·phase 체류시간 모델 없음 |
| 6 | phase별 정상 공간 | 화면과 객체 종류별 normal PCA, 분산99%, phase표본8미만 global fallback | phase 분할 오류·support 부족에 민감 |
| 7 | 테스트 영상 입력 | ZIP 연속JPG 및 MP4 decoder | R01/R04만 평가, 새 공장 성능 아님 |
| 8 | 관측 비용 제어 | test stride32, 과거-only context | 짧은 이상/중간 단계가 관측에서 빠질 수 있음 |
| 9 | 추론 시 검출·추적 | 학습과 같은 vocabulary/설정, 녹화마다 reset | 추적기는 샘플링된 화면에서 갱신 |
| 10 | 개별crop/trajectory | bbox/ID/위치/크기/프레임당 이동 성분 보존 | 완전한 전체 프레임 trajectory 학습 아님 |
| 11 | 상태·phase 직접 추정 | `semantics.assess`: 매 선택 관측 실제 이미지/crop GPT API | 낮은 confidence는 unknown, confidence는 보정확률 아님 |
| 12 | 시각 이상 점수 | 해당phase 공간의 PCA reconstruction residual | phase unknown/공간 부족/usable crop 없음은 global/frame fallback |
| 13 | 의미·공정 이상 점수 | VLM의 직접 consistency/위반 + normal 전이 surprisal | 원인 설명·누락/순서 추정의 정답률 미입증 |
| 출력 | 점수·경고·후보 위치 | normalCAL scale/q99, 객체 residual bbox 후보 | verified defect mask/정상 인증이 아님 |

9번에서 vocabulary를 저장해두면 객체 검출에 GPT가 필요 없다는 것과, 11/13번에서도 GPT를 쓰지 않는다는 것은 다르다. **이 경로는 추론 시 실제 API를 호출한다.**

VLM prompt는 잘못된 검출명/box를 맹신하지 말 것, 보이지 않는 동작을 만들지 말 것, 미검출을 실제 객체 누락으로 단정하지 말 것, sparse sampling만으로 skipped_step을 선언하지 말 것을 명시한다. 이 안전 문구가 있다고 실제 판단이 모두 정확해지는 것은 아니다.

## 5. 직접 학습한 것과 에포크

| 구성 | fitting/학습 데이터 | 에포크 또는 가중치 변경 |
|---|---|---|
| GPT-5.4 grammar | 기존 정상 keyframe | 새로 학습하지 않고 실제 생성 결과 재사용 |
| GPT-4.1-mini state/consistency | 현재/과거 이미지와 정상 specification | **fine-tuning0ep**, 호출을 수행한 것 |
| GroundingDINO·CLIP | 사전학습 가중치 | 동결, 추가 gradient 학습 없음 |
| 정상 PCA | 장면별 정상FIT72 및 해당 객체/phase 표본 | 통계적 fitting, epoch 없음 |
| phase 전이 확률 | 정상FIT의 직접 VLM phase | 전이 빈도 추정, epoch 없음 |
| 점수 scale/threshold | 별도 정상CAL32 | 중앙값/scale/q99 추정, epoch 없음 |
| 비교용 Feature AE | 정상 화면 CLIP 특징 | 장면별10ep,2버전×2장면=4개head |

AE optimizer는 AdamW, learning rate0.001, weight decay0.0001, batch32, gradient clip1.0, seed0이다. 고정epoch10을 사용하며 테스트 점수로 epoch를 고르지 않았다. 정상CAL 손실은 진단용으로 기록하지만 이 AE 실행의 checkpoint 선택에 사용하지 않았다.

4개head×10ep를 "VLM40ep 학습"이라고 표현하면 안 된다. **Full은 normal PCA/process fitting이고 AE는 별도 비교 기준**이다. AE 에포크를 늘려도 지금 Full 점수는 바뀌지 않는다.

## 6. 점수 계산과 두 버전

정상CAL에서 각 원점수의 중앙값을 빼고 `max(std, IQR, 1e-6)`로 나눠 scale을 맞춘다.

```text
visual_global = 0.5 × scaled(frame_global) + 0.5 × scaled(object_global)
visual_phase  = 0.5 × scaled(frame_phase)  + 0.5 × scaled(object_phase)
process_raw   = 직접 VLM 위반 종류 수 + 0.25 × 정상 phase 전이 surprisal
mentor_full   = 0.8 × visual_phase + 0.2 × scaled(process_raw)
global_plus_process = 0.8 × visual_global + 0.2 × scaled(process_raw)
```

객체는 종류별 normal 공간으로 개별 채점하고 frame에서 max를 취한다. 객체 feature는512차원crop과6개geometry 성분의518차원이다. 객체 공간이나 usable crop이 없으면 화면 경로로 fallback한다. confidence가 낮거나 phase가unknown이면 전이를 끊는다. unknown은 정상 인증이 아니다.

위반 점수는 GPT에게0~100 anomaly score를 받아 그대로 쓰는 방식이 아니다. GPT는 consistent/violation/unobservable와 위반 종류를 반환하고, 코드가 이를 전이 보조항과 결합한다. 객체 state 텍스트도 기록하지만 별도의 상태 텍스트 embedding 거리 모델을 학습한 것은 아니다.

| 버전 | 같은 부분 | 추가 내용 |
|---|---|---|
| `mentor-direct-v1` | 정상 분할,검출,CLIP,PCA,전이,AE,테스트 시점 | normal grammar + 현재/과거 이미지·state |
| `mentor-direct-reference-v2` | v1과 같은 학습/평가 시점 및 설정 | 원본normal_summary/uncertainties + 정상FIT3참고 이미지 |

참고 이미지는 원본grammar evidence index0/18/30이며 정상FIT 녹화에 속한다. phase 태그는 GPT 약한 라벨이고 human GT가 아니다. 참조3장으로4phase를 모두 정확히 대표했다고 주장하지 않는다. 테스트의 미래 이미지를 참조로 사용하지 않는다.

## 7. 실제 수치 결과

### 같은 조건 AUROC

| 방법 | 기본R01 | 기본R04 | 기본 평균 | 정상참고 평균 |
|---|---:|---:|---:|---:|
| global visual | 68.66% | 70.51% | **69.59%** | **69.59%** |
| phase visual | 64.61% | 64.36% | 64.48% | 64.99% |
| process 단독 | 50.82% | 59.48% | 55.15% | 54.23% |
| global visual + process | 68.87% | 71.46% | **70.16%** | 별도CSV 참조 |
| mentor Full | 65.09% | 65.03% | **65.06%** | **64.53%** |
| 비교용10ep AE | 60.82% | 67.12% | 63.97% | 63.97% |

AUROC는 정상/이상의 점수 순위 품질이며 분류 정확도가 아니다. 장면별 같은 가중치 평균이다. raw 전체 행을 pooling한 점수와 혼동하지 않는다.

### normal q99에서 프레임 경고 지표

| 버전/방법 | 평균 AUROC | 정상 frame FPR | 이상 frame Recall | frame F1 |
|---|---:|---:|---:|---:|
| 기본 global visual | 69.59% | 50.08% | 58.04% | 37.68% |
| 기본 mentor Full | 65.06% | 18.85% | 27.62% | 24.44% |
| 정상참고 mentor Full | 64.53% | 40.36% | 50.12% | 28.89% |

CAL q99가 test 정상FPR1%를 보장하지 않았다. 오경보 감소만 보면 기본Full이 좋아 보일 수 있지만 미탐이 늘었다. raw score 순위와 한 threshold의 운영 절충을 분리해 해석한다. 지속경고/event 지표는 [기본 전체 지표](../output/mentor_direct_20261005/RESULTS.md)와 JSON/CSV에 별도 보존한다.

### 성능 저하 지점

- 기본 global visual69.59% → phase visual64.48%: **약5.10pp 감소**.
- 같은phase visual에 process 추가:64.48% →65.06%, 약0.58pp 증가.
- phase 없는 global visual에 process 추가:69.59% →70.16%, 약0.58pp 증가.
- 정상참고 Full은R04에서+2.14pp, R01에서−3.19pp였다. 평균은−0.53pp다.

따라서 **현재의 주된 저하 지점은 phase 분할**이다. 다만 원인이 단계 추정 오류인지 표본 부족인지 hard routing인지 하나로 확정하지 않았다. process의 작은 증가도 확실한 기여라고 주장하지 않는다.

녹화 단위 paired bootstrap500회에서 기본R04 Full−global의 차이는−5.47pp,95%CI[−9.67,−1.79]였다. 같은phase 경로에 process를 더한 차이의 CI는 두 장면 모두0을 포함한다. [10개 비교와95%CI](../output/mentor_direct_comparison_20261005/COMPARISON.md). 단일 생성/단일 추론과 개발 중 반복 확인한 테스트라는 제한이 남는다.

## 8. 단계 추정과 정상 공간이 충분했나

| 버전/장면 | phase unknown | phase0 | phase1 | phase2 | phase3 |
|---|---:|---:|---:|---:|---:|
| 기본R01 FIT | 44 | 5 | 4 | 11 | 8 |
| 기본R04 FIT | 0 | 8 | 12 | 17 | 35 |
| 정상참고R01 FIT | 0 | 1 | 5 | 51 | 15 |
| 정상참고R04 FIT | 0 | 12 | 15 | 8 | 37 |

R01 두 버전의phase0/1은8개 미만이어서 해당 화면phase 공간을 만들지 않고 global로fallback했다. R04의4개 화면phase 공간은 모두 fitting했다. 객체별phase support는 화면과 다르며 [scene_summary](../output/mentor_direct_20261005/scene_summary.json)에 기록되어 있다.

정상참고에서unknown이0이 되었다고 정확도가100%가 된 것은 아니다. R01은phase2에51관측이 집중되었다. **사람 정답 없이 confidence/phase 분포만으로 개선을 판정하면 안 된다.**

별도R04 raw preview에서 목표제품 대신 다른 배경 부품에 box가 붙는 사례를 확인했다. 이 사례만으로 detector 전체오류율을 계산할 수는 없지만, 실제 객체 추출의 의미 감사가 필요하다. bbox가 존재한다는 사실만으로 결함 위치를 찾았다고 주장하지 않는다.

## 9. 검증 범위와 실제 영상 입력

- **12개 offline contract**: 직접 이미지/crop/과거-only 입력, MLP proxy 미사용, schema ID 검증, 모순응답 거부, normal-only 전이fit, unknown/녹화 reset, 직접 위반의 점수 영향, 개별crop 보존, 고정fusion, nonfinite calibration 거부, 실패 예산 보존, 별도 프로세스entrypoint import.
- **4개 scene-run 수치 검사**: FIT/cal disjoint, finite score, normal q99 재계산, 학습seal hash, accepted VLM 응답 수, AE10epoch history.
- **전체1,194관측 serialized replay**: 저장 모델과 offline scoring의 허용오차 확인, threshold alarm 일치. 최대 absolute residual 차이는 약3.3e-6 이하다.
- **raw MP4 실행**: R04/testing/01 처음192원본 프레임으로 만든 동일 fixture에서 버전별6시점, decoder→GDINO/ByteTrack→CLIP→실제VLM→저장모델score 실행. anomaly label을 읽지 않았다.

fixture의25FPS는 MP4 생성 설정이며 원IPAD FPS가 아니다. 기본6시점 wall time약10.88초, 정상참고약14.90초였지만 작은 장면/하드웨어/API 지연 포함 smoke다. 전체현장FPS나 정확도 벤치마크로 사용하지 않는다.

새 실제 VLM 응답은 main1,194 + raw12 = **1,206건**이다. 검증 fixture/raw overlay는 데이터 픽셀이 있어 이번public Git에는 올리지 않는다. numeric summary만 공개한다.

## 10. 무엇을 더 해야 성능을 높일 수 있나

아래는 **계획과 가설**이다. 완료한 개선이나 보장된 향상이 아니다. 에포크 증가보다 입력/정상기준/시간정보 검증을 먼저 한다.

| 우선순위 | 현재 근거/문제 | 다음 비교 | 성공 판단 |
|---|---|---|---|
| 1 | bbox와phase 의미 정확도 미검증, R01 unknown44/72 | 기존 응답/영상 일부를 사람이 검수해 객체role·phase·상태 정답 작성. 잘못된 vocabulary/모호한 phase 정의 교정 | 객체검출/phase 정확도, unknown 비율과 잘못된 확신을 함께 측정 |
| 2 | sparse FIT/cal/test의 관측 간격 불일치 | 녹화마다 동일 stride로 FIT/cal/test 표본 구성, 작은 정상cycle부터 검증 | 정상 전이 오경보 감소와 동일조건 anomaly 지표 확인 |
| 3 | phase표본1~35개로 작은 정상 공간 | 더 다양한 정상 녹화/완전cycle 확보, phase별coverage/support 확대, normalCAL 별도 확대 | 추가 정상 데이터에 따른 성능·FPR 안정화 곡선 |
| 4 | hard phase 선택 오류가 visual score에 전파 | global을기준으로 유지하고 phase 추가/제거, 불확실 시global fallback, phase전환확인/soft routing을 별도 비교 | 동일조건 global 대비 이득 및 phase 오류에 대한 강건성 |
| 5 | CLIP full/crop embedding만으로 국소 불량 표현 제한 가능 | CLIP 의미 경로는 유지하고 frozen DINOv2 patch-PCA 또는 patch normal memory를 병렬 비교 | 같은 정상 분할/stride에서 AUROC/AP 및 가능한 위치지표 개선 |
| 6 | process는 간단한 전이count+위반수, context 짧음 | cycle/체류시간/지연 정상분포, frame-gap 인지, 부족한증거는abstain. 추적ID가 안정된 후 객체 temporal 비교 | 관측누락·정상속도편차를 불량으로 오판하지 않는지 확인 |
| 7 | visual/process80:20 고정, CAL32로q99 불안정 | 점수 scale과 불확실성 gating, 더 넓은normalCAL, 비용/경고 operating point 비교 | AUROC와FPR/Recall/지연·비용을 함께 보고 |
| 8 | 현재 Rtest는 반복 확인한 development 데이터 | 설정을고정한 뒤 untouched recording/새공정 정상적응 평가 | 새공정 성능과 정상데이터양/적응시간, 독립CI |

DINOv2 patch와 normal PCA 비교는 [SubspaceAD](https://arxiv.org/abs/2602.23013)가 실제 사용하는 frozen patch-feature 아이디어에 더 가까운 대조다. 지금 구현은 CLIP global/crop residual이므로 원논문을 정확히 재현했다고 표현하지 않는다. [공식 DINOv2 코드](https://github.com/facebookresearch/dinov2)에도 frozen feature와patch 표현이 제공된다. 이 산업영상에서 더 좋다는 결과는 직접 비교해야 한다.

멘토 파이프라인 유지가 목표라면 **CLIP/GPT 역할을 그대로 두고 국소 visual 경로를 보강하는 대조**를 만들 수 있다. 기존에DINO CLS/부분FT를 시험한 결과를 새patch+직접VLM 조합의 결과로 간주하지 않는다.

phase 정확도가 문제인지 분할 자체가문제인지 구분하려면 작은 사람검수 phase 대조를 만든다. 테스트phase 정답을사용한 oracle실험은 배포 가능한 방법이 아니라 상한/원인진단으로만 표시한다. 정상학습에 사람phase를쓴 supervised설정과 machine-only설정도 별도로 구분한다.

VLM 모델/프롬프트 개선은 같은 소수 인간검수 표본에서 먼저 비교한다. 비싼 모델로 전체재추론하거나 무작정AE50ep로 바꾸는 것은 우선순위가 아니다. **VLM fine-tuning을 하려면 별도의 검수된 이미지·상태/phase target이 필요**하며 지금API추론의 epoch를 늘리는 옵션은 없다.

정상-only 프로토콜을 유지하면 anomaly test를보고 fusion/epoch/threshold를 최적화해 같은test에 보고하지 않는다. 정상-only 기준으로고정하거나, 이상 development 라벨을허용하는 별도프로토콜을 명시하고 untouched test를 남긴다. threshold 변경은 경고 절충을 바꾸지만 고정score의AUROC 자체를 높이지 않는다.

## 11. 코드·실행·재현 제한

코드: [`local_experiments/mentor_pipeline`](../local_experiments/mentor_pipeline/README.md). 평가 CSV/JSON/문서는public이고 원본ZIP·모델·feature·accepted image inference cache·비용원장은local이다.

### 설치 환경

기존 Windows/Python3.12/RTX4060 8GiB,torch2.7.1cu128/transformers4.57.6/supervision0.27.0 환경을 사용했다. [공통 설치·원본 특징 생성 절차](REPRODUCIBILITY.md)를 먼저 본다. 새로운 PC에서full fresh-clone 재학습을 완료했다고 주장하지 않는다.

### API 없이 코드 계약 검사

프로젝트root에서 필요한Python dependencies가 설치된 경우:

```powershell
& .\.venv\Scripts\python.exe -m local_experiments.mentor_pipeline.tests
```

실제 VLM 호출이 아니라 mocked 입력/모델 계약 검사다. 테스트 픽셀은 합성 단색 이미지이며 IPAD이미지를 재배포하지 않는다. 통과가 탐지성능 입증은 아니다.

### 저자 실행환경의 단계별 명령

아래는 **원본cache/grammar/API예산원장/공식backbone이 준비된 저자환경**의 명령이다. clone만으로 즉시실행되는 학습패키지가 아니다.

```powershell
# metadata preparation / fresh detector+tracker+CLIP extraction
& .\.venv\Scripts\python.exe -m local_experiments.mentor_pipeline.run --prepare-only
& .\.venv\Scripts\python.exe -m local_experiments.mentor_pipeline.run --extract-only

# 실제 유료VLM. 별도명시승인과자기예산/키가 준비된 환경에서만 실행
& .\.venv\Scripts\python.exe -m local_experiments.mentor_pipeline.run --paid --workers 3
& .\.venv\Scripts\python.exe -m local_experiments.mentor_pipeline.run --normal-reference --paid --workers 2

# accepted response/cache가 있는 경우 API 없이 score/report 재생성
& .\.venv\Scripts\python.exe -m local_experiments.mentor_pipeline.run
& .\.venv\Scripts\python.exe -m local_experiments.mentor_pipeline.compare_runs

# saved model + 새MP4 + 실제API를 사용하는 별도inference
& .\.venv\Scripts\python.exe -m local_experiments.mentor_pipeline.infer --scene R04 --video 'D:\data\my_video.mp4' --limit 6 --paid --out 'output\my_video\mentor_direct'
# 정상참고 모델을사용하려면 위명령에 --normal-reference 추가
```

### 새 환경에서 반드시 확인할 의존성

1. 공식IPAD ZIP은 별도다운로드하고 `run.py/infer.py/compare_runs.py/smoke.py`의저자ZIP경로를 본인환경에맞춘다.
2. CLIP/GDINO공식backbone을받고, 기존`extract_features.py --encoders clip --max-train 5000`의완료framecache를 만든다. `base_cache`는장면/encoder별해당cache가정확히하나있어야한다.
3. `data.GRAMMARS`가가리키는 원본grammar 두경로를 준비한다. 공개한`output/mentor_direct_20261005/R01/grammar.json`, `R04/grammar.json`은숫자/텍스트원본이며픽셀은없다. 각각 `local_experiments/runs/improvements_20261005/schema_v2/llm/R01/strong/grammar.json`와 `.../improvements_20261005/llm/R04/strong/grammar.json`로별도복사해재사용할수있다. 이들은사람미검증후보이며새공정정답이아니다.
4. `api.LEDGER`의ignored `local_experiments/cache/contexts/api_budget.json`은**자기승인한도**로별도초기화한다. 코드가참조하는필드는`limit_usd`, `reserved_usd`, `measured_estimate_usd`, `attempts`, `successful_calls`, `settled_receipt_sha256`, `followup_model_prices_usd_per_million`이다. 과거저자의$4승인/원장을새사용자에게승계하지않는다. 미확인예약은삭제해한도를늘리지않는다.
5. 새실험은RUN/OUT경로와프로토콜을새version으로분리한다. 완료표본/모델/봉인을덮어쓰지않는다. `--paid`없이accepted cache가없으면중단되는것이의도된동작이다.
6. report/comparison은저자예산원장및두버전완료cache를참조한다. 공개CSV를읽는것과이를재생성하는것은다르다.

새 API키/예산초기화 자체를 이번업로드에서실행하지않았다. 새일반사용자의end-to-end 재현은미검증이며이를원클릭재현으로홍보하지않는다.

## 12. 비용·공개 범위·출처

기존사용자가승인한누적$4안에서직접VLM실험을수행했다. main 비용추정은기본약$0.4215/정상참고약$0.5621이며과거작업과raw smoke를포함한누적사용량추정은약**$1.0995**다. 실패/미확인예약을포함한보수적reserved는약$3.8851로보존했다. 가격은당시토큰단가에따른보수적추정이며실청구서가최종기준이다.

기본버전R04에서응답이없었던연결timeout1건은failure를남기고별도1회recovery했다. 성공usage가확인된예약만정산하며실패hold를지웠다고주장하지않는다. API키값·request image payload·원비용원장·request/response ID목록은이번public업로드에서제외한다.

이번에추가게시하는것은소스/문서/숫자·텍스트metadata다. IPAD원본/파생영상,검수overlay,JPEG,MP4,features,PCAarray,AEweight,APIsecret는추가업로드하지않는다. 이전Release/커밋의자료는별도로보존하며이번업로드허가를데이터나모델의상업재배포허가로해석하지않는다.

공개체크아웃에서12개offline계약검사를재실행해통과했고,11개Python소스가저자원본과일치함을확인했다. 문서상대링크/JSON/40행지표평균/비밀키패턴·실제base64픽셀payload도검사했다. [공개파일SHA와검사기록](MENTOR_PUBLICATION_CHECKS.json). 이업로드확인에추가학습/유료API는사용하지않았다.

원데이터·논문·모듈출처:

- [IPAD 프로젝트](https://ljf1113.github.io/IPAD_VAD/): 산업공정 영상벤치마크. 이번결과는그공식전체평가와동일조건이아니다.
- [SubspaceAD](https://arxiv.org/abs/2602.23013): frozen DINOv2 patch-feature의정상PCA/residual아이디어. 현CLIP경로는정확한논문재현이아니다.
- [DINOv2](https://github.com/facebookresearch/dinov2), [CLIP](https://github.com/openai/CLIP), [GroundingDINO](https://github.com/IDEA-Research/GroundingDINO), [ByteTrack](https://github.com/ifzhang/ByteTrack): 사전학습모듈/추적아이디어의출처. 전부새로발명했다고주장하지않는다.
- [OpenAI 이미지입력](https://developers.openai.com/api/docs/guides/images-vision), [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs): 실제API입력/구조화출력경로.

팀공유용한문장: **"VLM을직접학습한것은아니고, 실제VLM이추정한객체상태·공정단계를정상공간/전이모델에연결했다. 전체경로는실행했지만phase분할이현재성능을낮춰,객체·phase정확도/관측간격/정상표본을먼저검증해야한다."**
