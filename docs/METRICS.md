# 평가 지표와 숫자 읽는 법

고도화 구현 기준: [metrics.py](../local_experiments/advanced_pipeline/metrics.py), [evaluate.py](../local_experiments/advanced_pipeline/evaluate.py). 초기/v3 지표에는 지속 경고/event/video 평가가 모두 있지 않으므로 서로 같은 열인지 먼저 확인한다.

## 1. 점수·경고·정답

- **score:** 이상할수록 커지도록 만든 연속 값. 정상feature residual 등을 뜻한다.
- **threshold:** 별도 normal calibration의99분위수. test label로 고르지 않았다.
- **frame flag:** 해당 관측score가threshold보다 엄격히 큰가(`>`).
- **persistent alarm:** 3관측 연속high면켜고2연속low면끄는 상태. 녹화 경계reset.
- **label:** 공개된0/1 anomaly frame 정답. phase/object/defect pixel 정답은 아니다.

EMA는현재점수0.4+이전평활화0.6이다. 미래프레임 없이 계산한다. alarm이 나중에 켜져도 이전high를 소급positive로 고치지 않는다. frame/alarm은 같은score의 다른 경고 정책이라 서로 결과가 다르다.

## 2. 순위 성능: threshold와 별개

| 열 | 의미 | 해석 주의 |
|---|---|---|
| `auroc` | ROC면적,정상보다이상점수를높게두는능력 | 73%는정확도73%가아님 |
| `average_precision` | recall증가량으로가중한precision요약 | PR사다리꼴면적과같지않음 |
| `pr_auc_trapezoid` | PR곡선사다리꼴적분 | AP와다른열 |
| `partial_auroc_fpr10` | FPR≤0.1의표준화partialROC | 전체AUROC와다른범위 |
| `diagnostic_tpr_at_fpr1/5` | testROC상저FPR에서의TPR | 실제배포threshold아님 |
| `diagnostic_fpr_at_tpr95` | testROC상TPR95%에서FPR | 정상q99배포기준과다름 |

마지막3개는 test rank 진단이다. test ROC에서 찾은 operating point를 다시 deployment threshold로 사용하지 않았다. 정상/이상 중 한 class만 있으면 ranking 지표는null/N/A다. 0%로 꾸며 넣지 않는다.

## 3. 정상q99 경고의 혼동행렬

frame와alarm 각각 TP(잡은이상),FN(놓친이상),FP(정상오경보),TN(맞춘정상)을 저장한다.

| 지표 | 식 | 운영 질문 |
|---|---|---|
| precision | TP/(TP+FP) | 경고중얼마나실제이상인가 |
| recall | TP/(TP+FN) | 이상중얼마나잡는가 |
| F1 | 2PR/(P+R) | precision/recall균형 |
| normalFPR | FP/(FP+TN) | 정상중얼마나잘못울리는가 |
| specificity | TN/(TN+FP) | 정상중얼마나조용한가 |
| accuracy | (TP+TN)/전체 | class불균형의영향을받음 |
| balancedaccuracy | (recall+specificity)/2 | 두class균등정확도 |
| MCC | 혼동행렬상관계수 | 불균형까지보는요약 |

경고가전혀없으면precision/F1 등분모0의classification ratio는코드의`division()`정책에따라0을반환한다. 이는class가하나뿐이라AUROC를정의못해null을두는경우와다르다. 예를들어state-transition-only의alarmFPR0은이상을잘잡았다는뜻이아니다. recall/F1도0이다.

`normal_calibration_frame_fpr`, `normal_tuning_frame_fpr`, `frame_normal_fpr`를 비교하면 새 정상분포 변화가 보인다. q99가 calibration에서약1%여도 testnormal이달라지면오탐이높다. R01에서는이문제가심했다.

## 4. Event: 이상 구간을 적어도 한번 잡았는가

각 clip의 샘플링된연속positive를GT event로, 연속alarm을alert event로본다. GT구간안에alarm이하나라도있으면detected GT event다. 예측alert가어떤GT와한번이라도겹치면true alert다.

| 열 | 의미 |
|---|---|
| `gt_events_sampled` | stride4 label의연속이상구간수 |
| `detected_gt_events` | alarm과겹친GT구간수 |
| `predicted_alert_events` | 연속persistentalarm구간수 |
| `false_alert_events` | GT와전혀겹치지않은alert수 |
| `event_recall_overlap` | detectedGT/GT |
| `event_precision_overlap` | GT와겹친alert/모든alert |
| `median_detected_delay_observations` | 탐지된GT구간의첫alarm까지관측수중앙값 |
| `median_detected_delay_original_frames` | 같은지연의원본frame번호차이 |

구간overlap은frame recall보다관대할수있다. 긴alert하나가여러GT와겹칠수있어one-to-one matching평가가아니다. miss된구간은지연중앙값에포함하지않으므로지연만낮다고좋다고판단하면안된다. detected/GT를함께본다. pointadjustment는없다.

`false_alerts_per_1000_normal_only_video_observations`는이상이하나도없는testclip에서1000관측당alert event수다. 모든normalframe중의FPR나시간당오경보가아니다. normal-only영상이없으면N/A다.

## 5. Video: 영상 전체에 이상이 있는가

video score는clip의상위5%프레임점수평균이다. video label은그영상에positive가한개라도있으면1이다. `video_auroc_top5mean`, `video_ap_top5mean`은영상class가두종류있을때만계산한다. 모든testvideo가이상이라면정상video없는videoAUROC는정의되지않는다.

Video기준이있다고학습에이상video전체label을쓴weak-supervisedVAD로바뀐것은아니다. 이번가중치fit은normal-only다.

## 6. 평균과seed 표준편차

우선각scene/seed/method의지표를계산한다. 같은seed의scene지표를동등가중평균하고그seed macro를평균/표준편차로요약한다. 서로다른scene의rawscore를붙여pooledROC를만들지않는다.

`n_scenes`, `n_scene_seed_runs`, `*_defined_scene_seed_runs`와seedstd를함께본다. few-shot은seed0만있어seedstd가null이다. 고정PCA의3seed행은같은통계기준을재사용하므로신경망3초기값분산과같은의미가아니다.

rawJSON은0~1비율,Markdown은100배한%다. AUROC0.7309→73.09%. 73.09−64.91은**8.18percentage points(pp)**이지상대8.18%증가가아니다. seedstd0.000312는약0.0312pp다.

## 7. 영상 단위 paired bootstrap

scene안의영상묶음을통째로재표집하고두method에같은선택을적용한다. 인접frame을독립표본처럼섞지않는다. 500반복,seed0,scene-equalmacroAUROC차이95%구간이다.

all16에서는500중480유효/20단일classundefined제외. R4비교는500유효. 이구간은현재scene/seed에조건부이며newfactory보장이나다중비교보정이아니다. 0을포함하는구간은안정적개선확정이라고쓰지않는다.

## 8. 측정하지 못한 지표

- 객체/instance GT없음: detector mAP,IoU,trackingHOTA/IDF1 미측정.
- phase/action GT없음: 실제phaseaccuracy/semanticfault 종류별recall 미측정.
- 결함pixel GT없음: pixelAUROC/AUPRO/segmentationIoU 미측정.
- ZIP원본FPS미확인: 초단위delay/시간당falsealarm 미측정.
- 48프레임AI참고agreement는humanGT정확도가아님.
- oracle99/99는rulecontract검사,raw stress비율은인위변조입력의alarm비율. 실제공정불량성능아님.

공식 정의 참고: [scikit-learn ROC AUC](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html), [AP](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html). 실제 프로젝트 수치는 [580행 CSV](../output/advanced_20261005/scene_seed_metrics.csv)와 [그룹평균](../output/advanced_20261005/group_summary.csv)에서 확인한다.
