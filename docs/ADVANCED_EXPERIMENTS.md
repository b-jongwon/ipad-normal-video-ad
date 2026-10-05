# 고도화 실험: 학습 구성·방법론·trade-off

대상: `advanced_20261005`. 이전v3와 별도 실행이다. source: [advanced_pipeline](../local_experiments/advanced_pipeline). 원 실행 상세: [결과보고서](../output/advanced_20261005/결과보고서.md).

## 1. 설계 목표와 달라진 점

정상-only를 유지하면서 에포크 고정/단계 후보 신뢰성/평가 부족을 보완한다. 정상fit/tune/calibration 분리,3seed,DAE,인과GRU/EMA,자동 시각 상태별PCA,frame/alarm/event/video지표,영상 bootstrap와streaming replay를 추가했다.

원래 phase MLP/semantic rule은 v3에서 보존한다. 주 고도화는 human phase에 의존하지 않는 전체normal/시각군집 경로다. S12를 더했다고 original LLM+GDINO+semantic13단계를16개 전체에 검증한 것은 아니다.

## 2. 표현과 입력

| 경로 | 입력 | 범위 |
|---|---|---|
| `dino_frame` | frozen DINO-S/14 CLS384,224px,stride4 | R4+S12 |
| `object_raw` | frozenCLIP full512+crop512+geometry6=1030 | R4,기존v3cache |
| `object_roi` | 같은joint1030,normal mobile ROI필터 | R4 |
| 추가crop-only | crop512+geometry6=518,stationary normal ROI | R4,사후탐색 |

fit의 평균/표준편차로 neural input을 표준화(std하한0.01)한다. normalcal로 object class별residual을보정하고nonnegative/maxobjects로프레임점수를만든다. 같은clip/ID인과history만GRU에들어간다.

## 3. 실제 학습 모델

| head | 구조 | 학습 loss | inference anomaly score |
|---|---|---|---|
| plain AE | d→128→32→128→d,GELU | MSE | 표준화feature MSE잔차 |
| denoising AE | d→256,LayerNorm,GELU,Dropout0.1→64→256→d | SmoothL1 beta0.5 | MSE잔차 |
| forecast | d→64,GELU,GRUhidden96→d,context8 | SmoothL1 beta0.5 | 현재feature MSE예측잔차 |

DAE에학습때만Gaussian noise std0.03을입력에더한다. tune/infer에서는잡음을더하지않는다. loss와ADscore가다르므로SmoothL1훈련이라고ADscore도SmoothL1이라고적으면틀리다. 서로다른losscurve절댓값으로우열을결정하지않는다.

최대100/min10epoch,patience10,유의개선relative0.005,AdamWlr0.001/wd0.001,batch128,gradclip1,ReduceLROnPlateaufactor0.5/patience3/minlr0.00001. bestweight는정상tune최소loss다. plateau판정용유의개선값과최소losscheckpoint는구분된다.

주208head의bestepoch12~100,median92.5. 정상plateau121head,100cap87head. cap은실험예산상한이지수렴확인이아니다.

## 4. 왜208+24개인가

| 묶음 | 계산 | head 수 |
|---|---|---:|
| 화면plainAE/DAE/GRU | 16장면×3seed×3 | 144 |
| raw objectplainAE | 4×3×1 | 12 |
| ROI objectplainAE/DAE/GRU | 4×3×3 | 36 |
| 화면few-shotDAE | 16×seed0×1 | 16 |
| 주 실험 합계 | 위4묶음 | **208** |
| 사후crop-onlyDAE/GRU | 4×3×2 | **24** |
| 고도화 총계 | 208+24 | **232** |

PCA/군집/전이/EMA는이neuralhead수에포함하지않는다. 580평가행에는고정통계기준/결합점수도있어head수와다르다.

주 실험18method union중all16공통은11개(seed0만few-shot,다른seed10),R4에는추가객체7개(seed0총18,다른seed17)가있다. 따라서 R4:4×(18+17+17)=208행,S12:12×(11+10+10)=372행,합계580행. 숫자208이우연히R4행수와head총수양쪽에등장하지만같은개념이아니다.

## 5. 주 실험method사전

| method | 의미 | 범위 |
|---|---|---|
| `dino_global_pca` | 정상fit DINO전역PCA잔차 | all16 |
| `dino_state_pca` | 시각군집별PCA,unknown/표본부족globalfallback | all16 |
| `dino_frame_plain_ae` | 화면normal재구성 | all16 |
| `dino_frame_denoising_ae` | 화면normal잡음제거재구성 | all16 |
| `dino_frame_forecast` | 화면과거8관측예측 | all16 |
| `visual_state_transition` | 시각상태전이드묾 | all16 |
| `dino_spatiotemporal` | DAE70%+forecast30% | all16 |
| `dino_visual_state` | DAE90%+state10% | all16 |
| `dino_full` | DAE60%+forecast30%+state10% | all16 |
| `dino_full_ema` | dinoFull의causalEMAalpha0.4 | all16 |
| `dino_fewshot3_denoising_ae` | fit3normalclip DAE,추가tune/cal | all16,seed0 |
| `object_raw_plain_ae` | 기존joint1030AE | R4 |
| `object_roi_plain_ae` | mobileROIjointAE | R4 |
| `object_roi_denoising_ae` | mobileROIjointDAE | R4 |
| `object_roi_forecast` | mobileROI동일IDGRU | R4 |
| `roi_hybrid` | objectDAE50%+화면DAE30%+objectGRU20% | R4 |
| `roi_hybrid_ema` | 위hybrid의EMA0.4 | R4 |
| `roi_hybrid_state` | objectDAE40%+화면DAE30%+objectGRU20%+state10% | R4 |

고도화 `dino_full`의state는v3`full_pipeline`의semanticprocess가아니다. 이름이같아보여도같은방법/분할로취급하지않는다.

## 6. 시각상태는공정phase정답이아니다

정상feature에서PCA/KMeans4군집을적합한다. confidence가부족하면unknown,전이빈도는normalfit에서Laplace0.5로보정한다. state별PCA는99%variance,min30normal관측,unknown/미지원state는globalPCA다.

semanticarrival/grasp/release를사람이확인해학습한모델이아니다. 자동state전이단독은all16AUROC49.84%,alarm0으로좋지않았다. statePCA는all16에서68.85>global64.91이지만R4에서는71.10<74.10이다. 특정모듈의효과를전체일반명제로확대하지않는다.

## 7. 정상ROI와R01실패

mobileROI는normalfit의동일IDtrack에최소5관측,displacement0.08,최소5mobiletracks/3녹화를요구한다. centerq01/q99,padding0.05로영역을정한다. 이동증거가부족하면해당class는필터를끄고기존후보를유지한다.

R01활성class0/2,테스트후보100%유지. 정지배경계측기가product로잡히는문제를해결하지못했다. R02/R03/R04의후보유지율98.52/99.88/96.16%는GT없이계산한filter효과지정확도아니다. 객체ROI밖새로운이상/검출실패위험때문에화면경로도유지한다.

## 8. 경고와인과성

normalcalibrationq99,strictscore>threshold로frameflag를만든다. 3회연속초과후persistentalarm활성,2회연속미초과후해제한다. EMA/GRU/alarm은clip경계reset하고미래를보지않는다. 나중에alarm이났다고과거구간을소급positive로바꾸는pointadjustment는없다.

q99는calibrationnormal에서정한분위수다. 새testnormal분포가달라지면FPR1%보장이없다. 높은AUROC와높은오경보가동시에가능하다.

## 9. 추가crop-only사후탐색

R4test를본뒤설계했다. normalpositionROI는최소30fit관측/3녹화,q01/q99+0.05로정하며이동을필수로요구하지않는다. crop518DAE/GRU,결합0.8/0.2,EMA0.4,기존normal3분할/earlystop/q99를사용했다.

| method | AUROC | AP | alarmFPR | alarmrecall |
|---|---:|---:|---:|---:|
| `crop_roi_denoising_ae` | 74.34% | 66.57% | 3.43% | 24.74% |
| `crop_roi_forecast` | 70.39% | 61.98% | 4.09% | 23.95% |
| `crop_roi_fusion` | 74.61% | 66.86% | 3.45% | 26.11% |
| `crop_roi_ema` | 75.80% | 67.95% | 8.57% | 33.91% |

이름은실제CSV와일치한다. 추가24head/48행,모델/replay검증통과. ROI밖이상/전체sequence/미검출을놓칠수있고static오검출을정상ROI로학습할수있다. 낮은오경보만으로default채택하지않았다.

## 10. 평가·봉인·실행비용

주실험의protocol/model/threshold/scores와statePCA를봉인한뒤evaluation이test값으로지표를계산했다. 파일length/0·1검사는그전에도있다. test모델선택을막는절차와라벨파일접근자체가없었다는설명은구분한다.

208head의cachedtraining1346.46초,24추가146.08초. S12feature318.84초. Rfeature재사용. “약25분이면새공장을전체학습한다”로변환하면안된다.

48장면×seed무결성,208headfinite/normal분리/q99/bestepoch검증. seed0의16장면firsttest최대120관측에서독립inferroundtrip;cropR4×3seed도동일검사. 모든원본test전체의rawdetector재실행검증은아니다.

원본CSV: [580행](../output/advanced_20261005/scene_seed_metrics.csv), [그룹평균](../output/advanced_20261005/group_summary.csv), [48행](../output/advanced_20261005/exploratory_crop_roi/metrics.csv), [232헤드 전체 epoch 학습 이력](../output/advanced_20261005/training_history.csv). 이력은 stage/scene/seed/view/head로 구분하고 normal fit/tune loss와 LR을 포함한다. 자세한 지표는 [METRICS](METRICS.md), 실행조건은 [REPRODUCIBILITY](REPRODUCIBILITY.md).
