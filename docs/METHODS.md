# 18가지 비교 구성

완전히 다른 사전학습 모델18종이 아니라, 같은 특징 추출기에서 어떤 정보를 점수에 사용하는지 바꾼 구성입니다. 각 수치는 R01~R04 평균 프레임 AUROC입니다. `only`는 최종 점수의 정보 범위를 뜻하며 단계 추정에는 화면/객체 특징이 함께 사용될 수 있습니다.

| 방법 | 점수에 사용하는 정보 | 평균 AUROC |
|---|---|---:|
| frame_only | CLIP 전체 화면의 단계별 PCA 잔차 | 67.27% |
| crop_only | CLIP 개별 crop의 객체 종류·단계별 PCA 잔차 | 68.44% |
| frame_object_joint | 화면512 + crop512 + geometry6 결합의 단계별 PCA 잔차 | 70.05% |
| frame_global_no_phase | 단계 구분 없는 CLIP 전체 화면 PCA 잔차 | 72.21% |
| object_global_no_phase | 단계 구분 없는 객체 종류별 결합 특징 PCA 잔차 | 73.32% |
| motion_only | 위치·크기·이동량의 정상 분포 편차 | 60.52% |
| patch_phase_only | DINO 패치의 단계별 PCA 잔차, 가장 높은3개 패치 평균 | 68.82% |
| explicit_process_only | 단계 건너뛰기·역순·객체 누락·지연 규칙 | 50.22% |
| visual_fusion | 보정된 frame35% + joint35% + patch20% + motion10% | 70.31% |
| visual_process | visual80% + process20% | 70.35% |
| joint_ae_5 | 정상 결합 특징 재구성 오차, AE5ep | 75.01% |
| joint_ae_10 | 같은 AE10ep 체크포인트 | 74.87% |
| track_forecast_5 | 같은 ID의 과거8관측으로 현재 특징 예측, GRU5ep | 70.30% |
| track_forecast_10 | 같은 GRU10ep 체크포인트 | 70.56% |
| spatial_temporal_5 | visual70% + GRU5ep30% | 72.14% |
| spatial_temporal_10 | visual70% + GRU10ep30% | 72.31% |
| full_pipeline_5 | visual60% + GRU5ep20% + process20% | 71.96% |
| full_pipeline_10 | visual60% + GRU10ep20% + process20% | 72.08% |

- 5/10ep는 같은 학습의 중간/최종 저장 시점입니다. 단계 분류기는 두 구성 모두10ep이고 PCA에는 에포크가 없습니다.
- AE는 영상 픽셀이 아닌 특징을 복원하고, GRU도 객체 특징을 예측합니다. `full_pipeline`에는 AE 점수가 들어가지 않습니다.
- 객체별 점수에서 해당 프레임의 최댓값을 사용합니다. 여러 객체를 평균내어 이상을 희석하지 않습니다.
- 방법별 점수 규모는 정상 검증으로 보정합니다. 가중치는 테스트 정답으로 최적화하지 않았습니다.
- 최고 순위는 같은 테스트에서 관측한 탐색 결과입니다. 독립 평가 없이 최적 모델로 확정하지 않습니다.

## CSV 열

- `macro_frame_auroc`: 네 장면의 프레임 AUROC 평균. 높을수록 좋으며 정확도는 아닙니다.
- `macro_frame_ap`: 네 장면의 프레임 average precision 평균. 높을수록 좋습니다.
- `macro_test_normal_fpr`: 정상 테스트 프레임 오경보율 평균. 낮을수록 좋습니다.

원자료: [18개 평균](../output/full_pipeline_20261004/방법별평균_18개.csv), [72개 장면별 결과](../output/full_pipeline_20261004/전체비교_72개.csv).
