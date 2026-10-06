# 멘토 직접 VLM 경로 검증·비교

두 버전 모두 MLP 대신 실제 이미지/crop VLM 추정이다. v2는 정상 설명/3FIT참고 이미지를 추가했다.
같은 정상72 fit/32 cal, R01 테스트125/R04 테스트264, stride32. 이전16장면 실험과 다른 조건이다.

| 버전 | 방법 | R01 AUROC | R04 AUROC | 두 장면 평균 |
|---|---|---:|---:|---:|
| mentor_direct_20261005 | visual_global | 68.66% | 70.51% | 69.59% |
| mentor_direct_20261005 | visual_phase | 64.61% | 64.36% | 64.48% |
| mentor_direct_20261005 | process | 50.82% | 59.48% | 55.15% |
| mentor_direct_20261005 | mentor_full | 65.09% | 65.03% | 65.06% |
| mentor_direct_20261005 | ae_baseline | 60.82% | 67.12% | 63.97% |
| mentor_direct_reference_20261005 | visual_global | 68.66% | 70.51% | 69.59% |
| mentor_direct_reference_20261005 | visual_phase | 61.45% | 68.54% | 64.99% |
| mentor_direct_reference_20261005 | process | 53.04% | 55.43% | 54.23% |
| mentor_direct_reference_20261005 | mentor_full | 61.90% | 67.17% | 64.53% |
| mentor_direct_reference_20261005 | ae_baseline | 60.82% | 67.12% | 63.97% |

## 녹화 단위 paired bootstrap 500회

| 버전/장면 | 비교 | AUROC 차이(pp) | 95% CI(pp) |
|---|---|---:|---|
| mentor_direct_20261005 / R01 | phase+semantic vs global visual | -3.58 | [-13.74, 6.59] |
| mentor_direct_20261005 / R01 | semantic added to same phase visual | 0.48 | [-1.19, 2.29] |
| mentor_direct_20261005 / R04 | phase+semantic vs global visual | -5.47 | [-9.67, -1.79] |
| mentor_direct_20261005 / R04 | semantic added to same phase visual | 0.68 | [-0.96, 2.22] |
| mentor_direct_reference_20261005 / R01 | phase+semantic vs global visual | -6.77 | [-15.06, 0.79] |
| mentor_direct_reference_20261005 / R01 | semantic added to same phase visual | 0.45 | [-0.62, 1.38] |
| mentor_direct_reference_20261005 / R04 | phase+semantic vs global visual | -3.33 | [-8.51, 1.30] |
| mentor_direct_reference_20261005 / R04 | semantic added to same phase visual | -1.36 | [-3.03, 0.27] |
| reference v2 minus v1 / R01 | matched mentor_full | -3.19 | [-10.87, 6.10] |
| reference v2 minus v1 / R04 | matched mentor_full | 2.14 | [-3.29, 6.62] |

코드 수행과 추정 정확도는 다르다. 직접 VLM 응답은 실제로 있었지만 사람이 확인한 phase/state 정답은 없다.
LLM+phase를 추가했다고 성능 향상을 자동 주장하지 않는다. 한 생성/한 state inference씩, 이미 확인한 테스트이므로 탐색 결과다.
원본/파생 영상 픽셀과 모델 파일을 외부에 게시하지 않았다. 모든 원본 v3/advanced 모델은 보존했다.
