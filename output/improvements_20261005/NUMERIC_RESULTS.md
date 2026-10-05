# 개선 실험의 저장 수치 전체 비교

모든 신규 실험은 이미 관찰한 IPAD에 대한 사후 개발 실험이다. 독립 최종 평가나 모든 공장 일반화 증거가 아니다.
고도화 기존3seed 평균과 아래 seed0 비교를 혼합하지 않는다. FPR/recall은 3관측 ON·2관측 OFF 경고 기준이다.

## memory / real4 / seed0

| 방법 | AUROC | AP | 경고 FPR | 경고 recall | 경고 F1 |
| --- | --- | --- | --- | --- | --- |
| prototype256 | 74.67% | 65.27% | 17.23% | 39.83% | 37.56% |
| prototype64 | 73.15% | 63.99% | 17.30% | 38.00% | 34.42% |
| prototype_fewshot3 | 72.52% | 62.30% | 17.04% | 31.84% | 26.00% |
| prototype_motion | 70.33% | 59.83% | 17.55% | 35.37% | 31.27% |
| prototype_motion_ema | 70.35% | 60.16% | 21.56% | 42.77% | 40.01% |
| prototype_neural | 77.08% | 68.39% | 17.65% | 40.44% | 38.69% |
| prototype_neural_ema | 77.82% | 69.86% | 21.57% | 45.96% | 44.05% |
| reference_dino_frame_denoising_ae | 75.36% | 66.51% | 18.75% | 40.67% | 39.03% |
| reference_dino_full_ema | 78.33% | 70.35% | 21.77% | 46.46% | 44.48% |
| reference_dino_global_pca | 74.10% | 63.85% | 17.95% | 40.06% | 38.43% |

## memory / synthetic12 / seed0

| 방법 | AUROC | AP | 경고 FPR | 경고 recall | 경고 F1 |
| --- | --- | --- | --- | --- | --- |
| prototype256 | 62.21% | 30.71% | 5.82% | 7.16% | 10.00% |
| prototype64 | 54.16% | 27.33% | 5.24% | 4.82% | 6.87% |
| prototype_fewshot3 | 39.96% | 19.36% | 4.65% | 1.45% | 2.21% |
| prototype_motion | 53.01% | 25.95% | 5.94% | 5.53% | 7.87% |
| prototype_motion_ema | 52.82% | 26.37% | 6.29% | 6.79% | 9.37% |
| prototype_neural | 68.52% | 33.76% | 6.33% | 8.78% | 12.03% |
| prototype_neural_ema | 68.69% | 34.09% | 6.57% | 9.86% | 13.20% |
| reference_dino_frame_denoising_ae | 66.49% | 34.53% | 6.55% | 9.59% | 12.99% |
| reference_dino_full_ema | 71.36% | 36.40% | 7.08% | 14.52% | 17.26% |
| reference_dino_global_pca | 61.84% | 31.56% | 6.16% | 7.79% | 10.53% |

## memory / all16 / seed0

| 방법 | AUROC | AP | 경고 FPR | 경고 recall | 경고 F1 |
| --- | --- | --- | --- | --- | --- |
| prototype256 | 65.32% | 39.35% | 8.67% | 15.33% | 16.89% |
| prototype64 | 58.91% | 36.49% | 8.25% | 13.12% | 13.76% |
| prototype_fewshot3 | 48.10% | 30.09% | 7.75% | 9.05% | 8.16% |
| prototype_motion | 57.34% | 34.42% | 8.84% | 12.99% | 13.72% |
| prototype_motion_ema | 57.20% | 34.82% | 10.10% | 15.78% | 17.03% |
| prototype_neural | 70.66% | 42.42% | 9.16% | 16.69% | 18.69% |
| prototype_neural_ema | 70.97% | 43.04% | 10.32% | 18.88% | 20.91% |
| reference_dino_frame_denoising_ae | 68.71% | 42.52% | 9.60% | 17.36% | 19.50% |
| reference_dino_full_ema | 73.10% | 44.89% | 10.75% | 22.50% | 24.07% |
| reference_dino_global_pca | 64.91% | 39.64% | 9.11% | 15.86% | 17.50% |

## covariance / real4 / seed0

| 방법 | AUROC | AP | 경고 FPR | 경고 recall | 경고 F1 |
| --- | --- | --- | --- | --- | --- |
| covariance_neural | 77.52% | 68.29% | 18.55% | 40.09% | 38.43% |
| covariance_neural_ema | 77.95% | 68.99% | 21.18% | 45.77% | 43.80% |
| mahalanobis | 75.31% | 65.18% | 17.89% | 39.36% | 37.37% |
| mixture_mahalanobis | 71.10% | 61.33% | 17.94% | 33.57% | 30.22% |
| reference_dino_full_ema | 78.33% | 70.35% | 21.77% | 46.46% | 44.48% |
| reference_dino_global_pca | 74.10% | 63.85% | 17.95% | 40.06% | 38.43% |

## covariance / synthetic12 / seed0

| 방법 | AUROC | AP | 경고 FPR | 경고 recall | 경고 F1 |
| --- | --- | --- | --- | --- | --- |
| covariance_neural | 68.73% | 34.23% | 6.30% | 9.39% | 12.55% |
| covariance_neural_ema | 68.90% | 34.53% | 6.93% | 11.42% | 14.37% |
| mahalanobis | 62.27% | 31.80% | 6.13% | 7.31% | 10.01% |
| mixture_mahalanobis | 71.18% | 38.60% | 4.83% | 9.32% | 12.96% |
| reference_dino_full_ema | 71.36% | 36.40% | 7.08% | 14.52% | 17.26% |
| reference_dino_global_pca | 61.84% | 31.56% | 6.16% | 7.79% | 10.53% |

## covariance / all16 / seed0

| 방법 | AUROC | AP | 경고 FPR | 경고 recall | 경고 F1 |
| --- | --- | --- | --- | --- | --- |
| covariance_neural | 70.93% | 42.75% | 9.36% | 17.06% | 19.02% |
| covariance_neural_ema | 71.16% | 43.15% | 10.50% | 20.01% | 21.72% |
| mahalanobis | 65.53% | 40.14% | 9.07% | 15.33% | 16.85% |
| mixture_mahalanobis | 71.16% | 44.28% | 8.11% | 15.38% | 17.28% |
| reference_dino_full_ema | 73.10% | 44.89% | 10.75% | 22.50% | 24.07% |
| reference_dino_global_pca | 64.91% | 39.64% | 9.11% | 15.86% | 17.50% |

## LLM v1 불완전 arms

| 장면 | 모델arm | 점수 | AUROC | AP | 경고 FPR | 경고 recall |
| --- | --- | --- | --- | --- | --- | --- |
| R01 | mini | global_pca | 69.74% | 45.51% | 33.12% | 58.84% |
| R01 | mini | phase_hard | 64.62% | 39.46% | 1.62% | 0.00% |
| R01 | mini | phase_soft | 72.32% | 47.12% | 54.55% | 98.07% |
| R04 | strong | global_pca | 71.84% | 71.53% | 1.88% | 4.19% |
| R04 | strong | phase_hard | 63.17% | 66.01% | 2.22% | 2.62% |
| R04 | strong | phase_soft | 62.96% | 69.05% | 1.33% | 7.34% |

## LLM v2 R01 matched

| 장면 | 모델arm | 점수 | AUROC | AP | 경고 FPR | 경고 recall |
| --- | --- | --- | --- | --- | --- | --- |
| R01 | mini | global_pca | 69.74% | 45.51% | 33.12% | 58.84% |
| R01 | mini | phase_hard | 61.95% | 38.39% | 18.83% | 38.91% |
| R01 | mini | phase_soft | 61.37% | 41.73% | 50.32% | 64.63% |
| R01 | strong | global_pca | 69.74% | 45.51% | 33.12% | 58.84% |
| R01 | strong | phase_hard | 67.01% | 42.66% | 60.55% | 95.50% |
| R01 | strong | phase_soft | 65.83% | 40.94% | 54.55% | 85.21% |

## DINO 일부 층 추가 학습: R01/R04

| 장면 | 방법 | AUROC | AP | 경고 FPR | 경고 recall |
| --- | --- | --- | --- | --- | --- |
| R01 | frozen_pca | 81.14% | 56.03% | 66.56% | 100.00% |
| R01 | finetuned_pca | 80.57% | 55.25% | 66.07% | 100.00% |
| R04 | frozen_pca | 76.56% | 77.67% | 3.33% | 19.21% |
| R04 | finetuned_pca | 76.33% | 77.24% | 3.22% | 17.64% |

## 같은 기존 Full EMA의 정상 임계치 절충: all16 seed0

q는 정상 calibration만으로 계산했다. 테스트 결과를 보고 기본 q99를 교체하지 않았다. AUROC는 임계치와 무관하다.

| 정상 quantile | 경고 FPR | 경고 recall | 경고 F1 | 이상구간 recall |
| --- | --- | --- | --- | --- |
| 0.95 | 16.64% | 33.68% | 31.87% | 44.25% |
| 0.975 | 13.29% | 27.82% | 28.32% | 37.99% |
| 0.99 | 10.75% | 22.50% | 24.07% | 31.37% |
| 0.995 | 9.56% | 20.17% | 21.92% | 28.53% |
| 0.999 | 8.17% | 15.70% | 17.03% | 24.20% |
