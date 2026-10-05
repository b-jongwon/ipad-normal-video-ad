# 실험 연대기와 완료 범위

이 문서는 실험 순서를 설명한다. 각 번호는 재현 가능한 실행 묶음이지 논문 알고리즘 이름이 아니다. v1/v2 중간 결과를 v3와 합산하거나 과거 최고 점수를 새로운 분할의 baseline으로 사용하지 않는다.

## E01 — 환경/데이터/표현 기준선, 2026-10-04

목표: 정상-only 영상 학습이 가능한지 확인하고, 비싼 전체 파이프라인 전 간단한 기준선을 세운다.

- IPAD ZIP을 읽기 전용으로 열어 연속 JPG/녹화/정답 길이를 검사했다. 전체 압축 해제를 전제로 하지 않았다.
- R01~R04 정상 녹화를 train/normal validation으로 나눴다. 시간순서와 stride4를 유지했다.
- DINOv2-S/14와 CLIP-B/16 특징을 동결 상태로 추출·캐시했다.
- 전역/시각 군집별 PCA, patch PCA, AE, GRU 및 고정 결합을 비교했다.
- 초기 object branch는 GroundingDINO + causal Lucas–Kanade tracking/role pooling이었다. 후속 ByteTrack 개별 객체 모델과 구분한다.
- 정상 영상 기반 GPT 문맥/CLIP text-image 단계 후보도 별도 비교했다.

초기 원CSV는248행이고,epoch0 통계모델의10epoch폴더 반복 저장을 제외하면44구성×4장면=176집계행이다. [중복 제외support](../output/meeting_20261004/comparison_summary_support.csv)도 제공한다. DINO global PCA74.66%,visual-state PCA74.76%로 차이가 작았다. AE/temporal/semantic을 추가한다고 일관되게 개선되지 않았다. 이를 생략하고 복잡 모델만 제시하지 않는다.

초기 단계의 R04 좁은 RGB crop(높이3) 처리에서 channel axis 자동 추정 문제가 있었다. channels-last를 명시하고 R04 객체 특징을 재추출했다. 기존 다른 결과를 지우지 않았고 regression fixture를 추가했다. 처음 실패한 출력/이전 실험은 로컬 실행 기록으로 남았다.

코드: `extract_features.py`, `compare.py`, `object_features.py`, `semantic_compare.py`, `report_results.py`, `verify_results.py`. 증거: [초기 보고서](../output/meeting_20261004/회의용_비교결과.md), [verification](../output/meeting_20261004/verification.json), [환경](../output/meeting_20261004/environment.json).

## E02 — 정상 데이터 예산 비교

normal PCA fit에 정상3/5/10녹화만 사용하고 각3번 선택했다. 전체fit 비교는1번이므로 장면당10실행,4장면40실행이다. 별도 정상 calibration 녹화를 추가로 사용한다.

| fit 예산 | R4 평균 AUROC |
|---|---:|
| 3녹화 | 74.41% |
| 5녹화 | 74.31% |
| 10녹화 | 74.91% |
| 전체fit | 74.66% |

정상 예시가 적어도 이 조건에서는 PCA 순위 성능이 크게 무너지지 않았다. 그러나 “어느 새 공장도3개로 된다”는 증거가 아니다. calibration 예산/오경보도 별도로 필요하다. 당시 저장한 PCA fit 수십ms는 **이미 계산한 특징 위의 fitting**만 측정했다. 영상 feature 추출/설정/검증 포함 전체 적응 시간이 아니다.

코드: `fewshot.py`, `uncertainty.py`. 증거: [few-shot 결과](../output/meeting_20261004/fewshot_results.csv), [summary](../output/meeting_20261004/fewshot_summary.json), [영상 bootstrap](../output/meeting_20261004/uncertainty.json).

## E03 — 멘토 제안 전체 파이프라인, v1→v2→v3

초기 간단한 객체 pooling 대신 개별 detection/track/crop을 유지하도록 확장했다. 정상 grammar 후보 → GDINO/ByteTrack → CLIP/DINO → weak phase MLP → phase normal spaces → process rules → AE/GRU → 후보 시각화/추론을 연결했다.

v3는 최종 공개된 원 제안 실행 묶음이다. v1/v2는 교정 전 중간 실행이며 독립적인 성공 재현으로 합산하지 않는다. 주요 교정은 이상 점수의 feature를 낮은 차원으로 미리 압축해 이상 정보를 없애지 않도록 하고, phase routing용64차원 투영과 anomaly feature를 분리한 것이다. 저장된 patch feature의 FP16과 온라인 연산의 FP32 차이도 비교했다. 수치 roundtrip 허용오차와 최종 보고서에 이를 기록했다.

- phase MLP10epoch, AE/개별track GRU는5/10epoch checkpoint.
- 정상 validation이 scale/threshold와 일부 phase confidence에 사용됨. 고도화의 독립 tune/calibration보다 단순한 초기 프로토콜.
- R4 ×18점수 구성 =72개 결과.
- 기존 Full10은72.08%, Joint AE5는75.01%, object global PCA73.32%.
- 정상/이상 순위가 적당히 분리됐다는 사실만으로 규칙/phase 추가 기여가 입증되지는 않았다.
- 정상 bbox/phase 후보를 사람이 모두 확인하지 못했다.

코드: `full_pipeline/`. 증거: [v3 보고서](../output/full_pipeline_20261004/완성결과_읽어주세요.md), [72행](../output/full_pipeline_20261004/전체비교_72개.csv), [모델 검증](../output/full_pipeline_20261004/verification_v3.json), [raw 입력](../output/full_pipeline_20261004/실제추론_검증.json).

## E04 — 16장면 고도화, 2026-10-05

고정50epoch 대신 정상 tune loss early stopping으로 변경했다. 정상 fit/tune/calibration을 녹화 단위로 분리했다. 새 DAE, 3seed, 자동 시각 상태별 PCA, causal EMA/persistent alarm, 더 많은 지표와 bootstrap를 추가했다.

- R4 + S12, 전체148,060샘플 관측. 48장면×seed 설정.
- 주208학습 head,580평가 행. 원래 semantic13단계는 여전히R4 범위.
- 선택 epoch12~100,중앙값92.5. 정상 plateau121개/상한87개.
- 추가 API0회. R 특징 재사용, S 화면 DINO 특징 새 추출.
- 모든 모델/점수/threshold와 state-PCA를 봉인한 뒤 테스트 값으로 지표 계산.
- R4는 이미 관측한 개발 평가. S12는 평가 전 방법을 고정한 별도 합성 시험.
- `dino_full_ema`: all16 73.09%,R4 78.24%,S12 71.38%.
- all16 PCA64.91% 대비 개선이 있으나 persistent recall22.84%와FPR10.78%로 실제 운영 문제는 남음.

코드/설정: `advanced_pipeline/`. [고도화 보고서](../output/advanced_20261005/결과보고서.md), [580행](../output/advanced_20261005/scene_seed_metrics.csv), [protocol](../output/advanced_20261005/protocol_locked.json), [학습 봉인](../output/advanced_20261005/training_all_sealed.json).

## E05 — crop-only 정상 ROI 후속 탐색

R4 고도화 지표를 본 후 배경의 영향을 줄이는 별도 실험을 추가했다. normal stationary ROI를 만들고 joint1030에서 full512를 제외했다. crop518 DAE/GRU24head,48평가 행.

- AUROC보다 FPR/recall trade-off를 같이 보았다.
- crop DAE FPR3.43%,recall24.74%; 결합EMA AUROC75.80%,FPR8.57%,recall33.91%.
- LLM/semantic role 문제나 R01 계측기를 진짜 제품으로 잘못 보는 문제는 해결하지 못함.
- ROI/context 제거를 동시에 바꿔 각 효과를 완전히 분리하지 못함.
- test 관찰 후 설계된 탐색. 기본 runtime/최종 모델을 이 점수로 자동 교체하지 않음.

[추가 protocol](../output/advanced_20261005/exploratory_crop_roi/protocol.json), [48행](../output/advanced_20261005/exploratory_crop_roi/metrics.csv), [검증](../output/advanced_20261005/exploratory_crop_roi/verification.json).

## E06 — 객체/phase/공정 규칙 감사

목표는 새 최고점을 만드는 것이 아니라 “원 가이드가 실행됐다는 것과 실제 의미가 맞다는 것이 같은가”를 검증하는 것이었다.

- 기존 v3 소스/weights/scores/grammar SHA를 보존하고 변경 없음 확인.
- normal evaluation 후보48프레임 AI 참고 검토. human GT 없음.
- phase 기호 주입 oracle99건 전부 통과.
- raw 정상/역순/80반복/140반복16건,1,880관측 실제 detector→head→rule 재실행.
- R01 정상에도 잘못된 order reason. R04 반복에서unknown으로dwell판단 불가.
- R01 manual noun/ROI 검출36회 교정과 normal median foreground 후보는 실패,미채택.
- 감사 trace에만 unknown/미검증 규칙 guard 추가. 기존 default score/모델 불변.
- 팀원 참고 commit/split/support 차이와 같은 v3 모듈 제거 효과를 기록.

감사에는 새 neural training과 유료 API 호출이 없다. [감사 보고서](../output/pipeline_audit_20261005/검증결과_팀원설명.md), [최종 확인](../output/pipeline_audit_20261005/final_verification.json).

## 남은 핵심과 선택 기준

| 과제 | 지금 상태 | 완료를 판단할 근거 |
|---|---|---|
| R01 객체 역할 교정 | 자동 교정2후보 실패 | 사람 role GT,정상/독립test 재추출·재학습·오탐 비교 |
| phase 의미/배타성 | weak/AI 후보만 | 사람이 확정한 phase와 연속 구간 GT |
| 공정 오류 종류별 검증 | oracle/인위 stress만 | 실제 skip/reverse/missing/stop 라벨과 recall |
| LLM 도입 당위성 | matched no-LLM 대조 없음 | 같은 vocab/phase 수동·LLM 및 설정시간/실패율 |
| 신규 공정 빠른 적응 | 기존 장면 few-shot만 | feature 추출·설정 포함 end-to-end 적응시간과 성능 |
| 독립 현장 일반화 | 미수행 | 새 실제 공정/카메라/조명에서 보류 평가 |
| 상용 배포 | 미검증 | 라이선스,장시간오경보,FPS/지연,운영 안전성 |

완료한 구현을 숨기지도, 남은 검증을 완료로 표시하지도 않는다. 성능이 좋아진 모듈만 기본 경로로 남기는 판단은 가능하지만 다음 버전은 새 protocol/독립 평가와 함께 보존해야 한다.
